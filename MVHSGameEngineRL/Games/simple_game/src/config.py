from pathlib import Path

from MVHSGameEngineML import Mode

#########################################################################
# Application Configuration
########################################################################
"""
Modes:
    HUMAN_PLAY:
    Play the game yourself with keyboard controls. No AI involved.

    AI_TRAIN_HEADLESS:
    Train the AI agent without rendering the game. Opens the Training Dashboard
    GUI to monitor progress, adjust settings, and save/load policies.
    This is the fastest way to train and the primary training workflow.

    AI_TRAIN:
    Train the AI agent with the game rendering visible. Useful for watching
    the agent learn in real time, but not practical for actual policy creation.

    AI_PLAY:
    Watch a trained AI agent play the game. Loads a saved policy file
    set in PLAY_POLICY_FILE and runs it with the game rendering visible. 
    Use this to evaluate a trained agent.
"""
MODE = Mode.HUMAN_PLAY

#########################################################################
# File path configuration
#########################################################################
BASE_DIR = Path(__file__).resolve().parent.parent

# Game asset file paths
ASSETS_DIR = BASE_DIR / 'assets'
IMAGES_DIR = ASSETS_DIR / 'images'
SOUND_DIR = ASSETS_DIR / 'sounds'

# Policy file paths
POLICY_DIRECTORY = BASE_DIR / "rl" / "policies"

# When curriculum training change the file name of the policy file you would like to start
# training from. Policies are saved in the policies directory for this game
PLAY_POLICY_FILE = ""

PLAY_POLICY_FILE_PATH = POLICY_DIRECTORY / PLAY_POLICY_FILE
########################################################################

########################################################################
# Simple Game Configuration
#######################################################################
GAME_NAME = "Simple Game"
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

# Collision Layers
LAYER_DEFAULT = 1       # 0b0001
LAYER_PLAYER = 2        # 0b0010
LAYER_WALL = 4           # 0b0100
LAYER_GOAL = 8           # 0b1000

# Debug
DRAW_PHYSICS_DEBUG = False

# Player Configuration
# Does not change player speed, used only for normalization
PLAYER_MAX_VEL = 300

#######################################################################
# Reinforcement Learning Configuration
#######################################################################
# The number of actions the agent has, in this game there are 5 total, LEFT, RIGHT, UP, DOWN and NOOP
ACTIONS = 5

# Max training steps per episode. The game runs for this many frames per episode.
# Typical range: 500 - 10000. At 60 FPS, 6000 steps = 100 seconds of gameplay.
MAX_STEPS = 2000

# How many frames a chosen action should be repeated. To speed up training and ensure stability a new action does not need
# be selected every frame. This values specifies how many frame/steps, should use the same action
ACTION_REPEAT = 4

# How many total episodes the agent will train for.
# Typical range: 500 - 10000
DEFAULT_EPISODES = 2000

# How strongly to update the policy each episode.
# Higher (0.01) = learns faster but unstable. Lower (0.0001) = smoother but slower.
DEFAULT_LEARNING_RATE = 0.001

# Forces the agent to keep trying different actions.
# 0 = no extra exploration. 0.05+ = breaks out of stuck policies.
DEFAULT_EXPLORATION_BONUS = 0.0

# How much the agent values future rewards vs immediate rewards.
# Closer to 0 = short-sighted. Closer to 1 = long-term planning.
DEFAULT_GAMMA = 0.99

# Used to save configuration to policy file. Add any notes as strings to the end of this function as necessary!
def get_config_string_notes():
    save_notes = (f"\nSimple Game config notes\n"
        "--- Player Config ---\n"+
        "NA\n"+
        f"--- Additional Notes ---"+
        f"      ")      # Add custom notes here.

    return save_notes

