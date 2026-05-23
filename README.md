# MVHS Game Engine ML

Lightweight 2D game engine built with Pygame, designed for building simple games and training reinforcement learning agents. 
## Overview

This project has two parts:

- **MVHSGameEngineRL** — A simple 2D game engine with physics, collision, animation, camera, event system, and UI overlay

- **Games** — Games built on top of the engine, each with an RL training pipeline that lets an AI agent learn to play

Students can train AI agents to play them using the REINFORCE policy gradient algorithm. A training dashboard GUI lets you monitor training progress, save and load policies.

## Games Included

| Game | Description | 
|------|-------------|
| **Simple Game** | Move a player to reach a goal | 
| **Flappy Bat (Flappy Bird)** | Navigate through gaps between barriers | 

More games will be added soon


## Requirements

- Python 3.12+


## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mvhs-cs-p/MVHSGameEngineML.git
cd MVHSGameEngineML
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- **Windows:** `.venv\Scripts\activate`
- **macOS/Linux:** `source .venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### Optional - Install PyTorch with CUDA

The `requirements.txt` installs CPU-only PyTorch. 
Using CUDA does not offer significant training advantages. The game engine, MVHSGameEngineML, is a bottleneck that will prevent any significant speed increase.



## Running a Game

Each game has a `config.py` file in its `src` directory. Open it and set the `mode` variable at the top to choose how to run:

```python
mode = Mode.HUMAN_PLAY          # Play the game yourself
mode = Mode.AI_TRAIN_HEADLESS   # Train the AI (fastest, opens training dashboard)
mode = Mode.AI_TRAIN            # Train the AI with game visible (slow, for debugging)
mode = Mode.AI_PLAY             # Watch a trained AI play
```

Then run the file:

```bash
python Games/simple_game/src/main.py
```

## Training an AI Agent

### Headless Training (Recommended)

1. Set `mode = Mode.AI_TRAIN_HEADLESS` in the game's `mconfig.py`
2. Run the game's `main.py` file in src — the Training Dashboard GUI will open
3. Adjust episodes, learning rate, gamma, and exploration bonus as needed. See game's `config.py` for descriptions
4. Click **Train** to start training
5. Watch the reward curve climb on the graph
6. Click **Stop & Save** when satisfied, or let it finish

The dashboard saves both the final policy and the best policy (based on rolling average reward). Use the best policy for playback.  
Policies are saved in the game's `rl/policies` directory.

### Watching a Trained Agent

1. Set the policy file name in the game's `config.py` under `PLAY_POLICY_FILE`
2. Set `mode = Mode.AI_PLAY` in `config.py`
3. Run the file

### Curriculum Training

For better training results, train in stages:

1. Start with easy settings (generous thresholds)
2. Train until the agent performs well
3. Click **Load Policy** in the dashboard and select the saved policy
4. Adjust the game difficulty in `config.py` (differnt games have different settings)
5. Optionally lower the learning rate for fine-tuning
6. Click **Continue Training**

Each stage builds on the previous policy's learned behavior.

## Key Files

When building a new game or modifying an existing one, these are the main files you'll work with:

| File | Purpose |
|------|---------|
| `config.py` | Game settings, RL hyperparameters, file paths |
| `rl/policy_net.py` | Neural network structure |
| `rl/*_rl_environment.py` | Observations, rewards, step logic |

## How REINFORCE Works (Brief)

You can review the basic of reinforcement learning here:  
[Reinforcement Learning Slide Deck](https://www.canva.com/design/DAHKUSyNffk/w21kSxz_l89JRjXBCJn-Og/view)



## Tips for Training

- **Start simple.** Get the easiest version of your game working before adding complexity.
- **Play it yourself first.** If you can't beat it, the agent can't learn it.
- **Watch the reward curve.** If it's flat after 500 episodes, something is wrong — don't just add more episodes.
- **Save the best policy.** REINFORCE can degrade — the final policy isn't always the best one.
- **Lower learning rate for curriculum stages.** The agent already has skills, large updates can destabilize them.
- **Use the exploration bonus** when the agent gets stuck on one action (0.05-0.1 to break out).
- **If the agent does something unexpected, check your reward function.** The reward is probably encouraging it. Adjust the `compute_reward()` function in the games `rl_environment.py` file

