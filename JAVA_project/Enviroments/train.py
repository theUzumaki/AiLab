
# This script is used to train a reinforcement learning agent using the PPO algorithm
from ray.tune import Tuner, RunConfig
from ray.rllib.algorithms import ppo
from ray.tune.registry import register_env

# Import the custom environment and configuration
from customEnv import KillerVictimEnv

# Import the custom policy mapping function
from config import policy_map_fn, get_multiagent_policies

# Used to take arguments from the command line
import sys

N_EPISODES = 2  # <-- numero desiderato di episodi
ABSOLUTE_PATH = "/Users/lachithaperera/Documents/AiLab/JAVA_project/" # <-- percorso assoluto del progetto

def env_creator(agent):
    """
    Creates the environment configuration for the Killer-Victim environment
    and sets up the it for training using the PPO algorithm.
    """

    # Define the configuration for the PPO algorithm
    config = ppo.PPOConfig().env_runners(
        batch_mode="complete_episodes",
        num_env_runners=0,
        num_envs_per_env_runner=1,
        create_env_on_local_worker=True,
        episode_lookback_horizon=1          # numero di episodi da guardare indietro per il calcolo della ricompensa
    ).environment(
        env="KillerVictimEnv",
        env_config={
            "is_use_visualization": False,
            "agent": agent,
            "msg_path": f"msg_{agent}.json"
        },
    ).framework(
        framework="torch",  # Use PyTorch as the framework
    ).multi_agent(
        policies=get_multiagent_policies(),
        policy_mapping_fn=policy_map_fn,
        policies_to_train=["killer"] if agent == 'killer' else ["victim"],
        policy_map_capacity=100,
        count_steps_by="agent_steps",
        observation_fn=None
    ).api_stack(
        enable_rl_module_and_learner=False,
        enable_env_runner_and_connector_v2=False,
    ).training(
        train_batch_size=10,           # 1 episodio intero
        num_sgd_iter= 1,
        minibatch_size=1,         # dimensione del minibatch per l'aggiornamento SGD
    )

    return config

def trainable(agent):
    # Register the custom environment with Ray
    register_env(
        "KillerVictimEnv",
        KillerVictimEnv
    )

    tuner = Tuner(
        "PPO",
        run_config=RunConfig(
            stop={
                "env_runners/num_episodes": N_EPISODES,  # Stop after N episoded   
            },
            verbose=1,
            name="KillerVictimRun"
        ),
        param_space=env_creator(agent).to_dict(),
    )

    results = tuner.fit()

    best_result = results.get_best_result(metric="episode_reward_mean", mode="max")
    print(f"[INFO] Best result: {best_result}")

if __name__ == "__main__":
    trainable(sys.argv[1])  # Start training with the specified agent