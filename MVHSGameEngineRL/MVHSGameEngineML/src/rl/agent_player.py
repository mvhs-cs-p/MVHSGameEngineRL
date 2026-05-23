import torch
import time
from MVHSGameEngineML.src.core.config import TrainingStatus
from MVHSGameEngineML.src.rl.training_file_store import TrainingFileStore


class AgentPlayer:
    def __init__(self, agent_player_config):
        self.policy_network = agent_player_config["policy_network"]
        self.environment = agent_player_config["environment"]
        self.policy_file = agent_player_config["policy_file"]
        self.max_steps = self.environment.max_steps

        self._load_policy()


    def _load_policy(self):
        policy_file = TrainingFileStore.load_training(self.policy_file)
        self.policy_network.load_state_dict(policy_file['policy_state_dict'])
        self.policy_network.eval()


    def play(self, episodes, pause_between_episodes=1):
        for episode in range(episodes):
            self.environment.restart()
            done = False
            steps = 0
            while not done and steps < self.max_steps:
                observation = self.environment.get_observation_tensor()
                action = None
                with torch.no_grad():
                    logits = self.policy_network(observation)
                    distribution = torch.distributions.Categorical(logits=logits)
                    action = distribution.sample()

                result = self.environment.step(action)
                steps = self.environment.step_count
                #next_obs, reward, steps_taken, status = self.environment.step(action)
                #print(status)
                #steps += steps_taken


                # Training Status is used when still in progress,
                # DO NOT change unless a new TrainingStatus is created
                if result["status"] != TrainingStatus.TRAINING:
                    time.sleep(pause_between_episodes)
                    done = True

