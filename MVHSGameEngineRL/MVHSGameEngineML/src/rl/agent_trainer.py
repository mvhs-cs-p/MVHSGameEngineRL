import copy
import time

import torch
import torch.optim as optim
from torch.distributions import Categorical

from .training_file_store import TrainingFileStore
from ..core.config import TrainingStatus


class AgentTrainer:
    def __init__(self, agent_trainer_config):
        self.policy = agent_trainer_config["policy"]
        self.learning_rate = agent_trainer_config["learning_rate"]
        self.gamma = agent_trainer_config["gamma"]
        self.episodes = agent_trainer_config["episodes"]
        self.environment = agent_trainer_config["environment"]

        # Optimizer only set if loading a trained policy
        if "optimizer_state_dict" in agent_trainer_config:
            self.optimizer_state_dict = agent_trainer_config["optimizer_state_dict"]
        else:
            self.optimizer_state_dict = None

        self.exploration_bonus = agent_trainer_config["exploration_bonus"]
        self.is_training = False
        self.is_saving = False
        self.training_episode = 0
        self.should_stop = False
        self.start_training_time = None
        self.estimated_remaining_training_times = []
        self.optimizer = None
        self.best_average_reward = float("-inf")

        # Best policy and optimizer states (led to the highest reward) are saved during
        self.best_policy_state = None
        self.best_optimizer_state = None


        # Training stats used to update training dashboard, not saved
        self.training_stats = {
            "last_training_episode": 0,
            "training_episodes": 0,
            "elapsed_training_time": 0,
            "estimated_remaining_training_time": 0,
            "episode_rewards": [],
            "episode_steps": [],
            "episode_end_status" : [],
            "best_average_reward": float("-inf"),
            "best_average_reward_episode": 0,
        }

    def start_training(self):
        """
        Start the agent training loop.
        Resets the training stats for the training GUI

        If training over a saved policy (curriculum) the optimizer state dict is loaded
        """
        self.is_training = True
        self.should_stop = False
        self.training_episode = 0

        self.training_stats["last_training_episode"] = 0
        self.training_stats["training_episodes"] = self.episodes
        self.training_stats["elapsed_training_time"] = 0
        self.training_stats["estimated_remaining_training_time"] = 0
        self.training_stats["episode_rewards"].clear()
        self.training_stats["episode_steps"].clear()
        self.training_stats["episode_end_status"].clear()
        self.training_stats["best_average_reward"] = float("-inf")
        self.training_stats["best_average_reward_episode"] = 0

        self.best_average_reward = float("-inf")

        self.start_training_time = time.time()

        self.optimizer = optim.Adam(self.policy.parameters(), lr=self.learning_rate)

        if self.optimizer_state_dict is not None:
            self.optimizer.load_state_dict(self.optimizer_state_dict)

            for param_group in self.optimizer.param_groups:
                param_group["lr"] = self.learning_rate

        self._train()


    def _train(self):

        """
        Train the agent and save the best average reward.
        """
        while self.training_episode < self.episodes:

            # Headless training runs on a separate thread, GUI on main thread, the training thread can be stopped here
            if self.should_stop:
                break


            self.training_episode += 1

            # The environment is the wrapper between this trainer code and the actual game (environment).
            # Each game handles restart differently, but are all triggered through this method
            self.environment.restart()

            # Get initial observation after restarting the environment
            obs_tensor = self.environment.get_observation_tensor()

            # Stores how likely the policy thought each chosen action was
            # These are used later to update the policy after the episode ends.
            log_probs = []

            # Rewards accumulated this episode each step(s) during this training episode
            # Game RL environment may so multiple steps with same action before calculating and
            # returning a reward. See ACTION_REPEAT in game config file
            rewards = []

            # Entropies measure how spread out log_probs are for each step during this training episode
            # Entropies are saved to force the agent to occasionally choose a different action
            # even after the lob probabilities strongly suggest one move should be chosen. This prevents
            # the agent from getting stuck during training and continues exploring.
            entropies = []

            # Run through an entire episode
            # The environment wrapper is incharge of stepping through the environment, each iteration through this
            # while loop may result in multiple sequential steps. Rewards are only collected after this sequence
            # see game config files for ACTION_REPEAT
            done = False
            while not done:

                # Forward pass through the neural network. The raw action scores are saved
                logits = self.policy(obs_tensor)

                # Create a probability distribution from the logits,
                # then sample one action from that distribution.
                # The highest distribution is not automatically chosen, but it does have the best chance of being chosen
                distribution = Categorical(logits=logits)
                action = distribution.sample()

                # Agent applies the action and steps through the environment, each game handles this differently
                # depending on the nature of the game, all game RL environment wrappers implement step
                result = self.environment.step(int(action.item()))
                if result["status"] != TrainingStatus.TRAINING:
                    done = True

                # Save results of selected action and rewards
                log_probs.append(distribution.log_prob(action))
                rewards.append(result["reward"])
                entropies.append(distribution.entropy())

                obs_tensor = self.environment.get_observation_tensor()


            # Discounted return for each step in the episode. A return value is
            # the total future reward from that index forward.
            returns = []

            # G stores the return as we work backward through the episode.
            # It starts at 0 because there are no future rewards after the episode ends.
            G = 0.0

            # Loop through all rewards in reverse order. gamma controls how much short term, vs long term rewards matter
            for reward in reversed(rewards):
                G = reward + self.gamma * G
                returns.append(G)

            # Put returns back in the order they were created from playing through the episode, conver to tensor
            returns.reverse()
            returns = torch.tensor(returns, dtype=torch.float32)

            # Normalize the returns to make training more stable.
            # After this, positive values mean "better than average for this episode"
            # and negative values mean "worse than average for this episode."
            if returns.shape[0] > 1:
                returns = (returns - returns.mean()) / (returns.std() + 1e-8)


            # Compute the loss to determine how actions need to be adjusted for given reward
            # Actions that lead to higher rewards get increase probability in distribution
            # Actions that lead to lower rewards get decrease in probability in distribution
            # Note: The negative sign is used because PyTorch minimizes loss, but we want to maximize reward. Needed for RL
            # Entropy is subtracted to encourage exploration, prevents getting stuck in a policy that is not optimal.
            loss = -(torch.stack(log_probs) * returns).sum() - self.exploration_bonus * torch.stack(entropies).sum()

            # Update the neural network
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()


            self.update_training_stats(rewards, self.environment.step_count, result["status"])

            # Keep a copy of the best found policy, this policy is saved to disk after training is complete
            if len(self.training_stats["episode_rewards"]) >= 200:
                recent_average_rewards = sum(self.training_stats["episode_rewards"][-50:])/50
                if recent_average_rewards > self.best_average_reward:
                    self.best_average_reward = recent_average_rewards
                    self.best_policy_state = copy.deepcopy(self.policy.state_dict())
                    self.best_optimizer_state = copy.deepcopy(self.optimizer.state_dict())
                    self.training_stats["best_average_reward"] = self.best_average_reward
                    self.training_stats["best_average_reward_episode"] = self.training_episode


        self.is_training = False


    def update_training_stats(self, last_episode_rewards, last_episode_steps, episode_end_status):
        """
        Update the training stats based on last episode rewards and last episode steps.
        Training GUI displays stats
        """
        self.training_stats["episode_rewards"].append(sum(last_episode_rewards))
        self.training_stats["episode_steps"].append(last_episode_steps)
        self.training_stats["last_training_episode"] = self.training_episode


        self.training_stats["estimated_remaining_training_time"] = self.get_estimated_remaining_training_time()
        self.training_stats["episode_end_status"].append(episode_end_status)
        self.training_stats["elapsed_training_time"] = time.time() - self.start_training_time


    def get_estimated_remaining_training_time(self):
        """
        Returns the estimated remaining training time in seconds. Calculated by how much time the last 50 episodes took
        :return:
        """

        if self.training_stats["elapsed_training_time"] == 0:
            return 0

        last_last_episode_end_time = self.training_stats["elapsed_training_time"]
        last_episode_end_time = time.time() - self.start_training_time

        remaining_episodes = self.episodes - self.training_episode
        if remaining_episodes <= 1:
            return 0

        remaining_seconds = (last_episode_end_time - last_last_episode_end_time) * remaining_episodes
        self.estimated_remaining_training_times.append(remaining_seconds)
        if len(self.estimated_remaining_training_times) > 50:
            self.estimated_remaining_training_times.pop(0)
            return sum(self.estimated_remaining_training_times) / 50
        else:
            return 0





    # def save_policy(self, file_path):
    #     self.is_saving = True
    #     policy_file_name = TrainingFileStore.save_training(file_path, self)
    #     # policy_data_path = file_path
    #     # policy_data_path.mkdir(parents=True, exist_ok=True)
    #     # current_time = datetime.datetime.now()
    #     # policy_file_name = f"policy_{current_time.strftime('%Y%m%d-%H%M')}.pt"
    #     # policy_file = policy_data_path / policy_file_name
    #     # torch.save(self.policy.state_dict(), policy_file)
    #     self.is_saving = False
    #     return policy_file_name




