import torch
import datetime
from ..core.config import TrainingStatus
torch.serialization.add_safe_globals([TrainingStatus])

class TrainingFileStore:


    @staticmethod
    def save_training(save_file_path, agent_trainer_object, config_notes):
        policy_data_path = save_file_path
        policy_data_path.mkdir(parents=True, exist_ok=True)
        current_time = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        policy_file_name = f"policy_{current_time}.pt"
        policy_file = policy_data_path / policy_file_name

        torch.save({
            "policy_state_dict" : agent_trainer_object.policy.state_dict(),
            "optimizer_state_dict" : agent_trainer_object.optimizer.state_dict(),
            "training_stats" : agent_trainer_object.training_stats,
            "config_notes" : config_notes
        }, policy_file)


        if agent_trainer_object.best_policy_state is not None:
            policy_file_name = f"best_policy_{current_time}.pt"
            policy_file = policy_data_path / policy_file_name

            # These are kept separate to display which policy was loaded to continue training
            best_average_reward = agent_trainer_object.training_stats["best_average_reward"]
            best_average_reward_episode = agent_trainer_object.training_stats["best_average_reward_episode"]

            torch.save({
                "policy_state_dict" : agent_trainer_object.best_policy_state,
                "optimizer_state_dict" : agent_trainer_object.best_optimizer_state,
                "training_stats" : agent_trainer_object.training_stats,
                "config_notes" : config_notes,
                "best_average_reward" : best_average_reward,
                "best_average_reward_episode" : best_average_reward_episode
        }, policy_file)

        return current_time


    @staticmethod
    def load_training(file_path):
        return torch.load(file_path)



