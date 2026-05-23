import torch.nn as nn

class FlappyBatPolicyNet(nn.Module):
    """
    Policy Network Structure

    This class defines the neural network structure the agent (player) will train
    as it figures out how to get rewards.

    Note: Once you start curriculum training the neural network structure
    cannot change.
    """

    def __init__(self, obs_dim = 9, n_actions = 2):
        """
        Define the structure of the neural network.
        :param obs_dim: Number of input observations. This must be the same as the number values returned in the tensor
        returned from get_observation_tensor in flappybat_game_rl_environment.py

        :param n_actions: Number of possible actions. Must include NOOP (no button press)
        This game as 2 total actions, NOOP, FLAP

        The policy network is used in MVHSGameEngineML/src/rl/agent_trainer.py

        """
        super().__init__()
        self.net = nn.Sequential(
            # First hidden layer, input must be obs_dim. You can change the number of neurons as you see fit
            # (Be cautious not to overfit!)
            nn.Linear(obs_dim, 32),
            # Activation function of the first hidden layer
            nn.ReLU(),

            # Define additional layers as needed (Be cautious of overfitting, likely not need additional hidden layers)

            # Define output layer, The number of outputs much be n_actions
            nn.Linear(32, n_actions),

            # No activation function on output layer. We want the raw output, logits from the NN.
        )

    def forward(self, x):
        """
        Forward pass of the neural network
        """
        return self.net(x)