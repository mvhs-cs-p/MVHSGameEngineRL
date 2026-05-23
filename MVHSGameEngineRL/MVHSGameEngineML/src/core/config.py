from dataclasses import dataclass
from enum import Enum

class Mode(Enum):
    HUMAN_PLAY = 0
    AI_TRAIN = 1
    AI_TRAIN_HEADLESS = 2
    AI_PLAY = 3

class TrainingStatus(Enum):
    TRAINING = 0
    SUCCESS = 1
    TIMEOUT = 2
    GAME_OVER = 3

@dataclass
class EngineConfig:
    mode: Mode
    train_headless: bool = False
    fixed_dt: float = 1/60
    action_repeat: int = 1
    max_steps: int = 1000
    action_repeat_times: int = 4