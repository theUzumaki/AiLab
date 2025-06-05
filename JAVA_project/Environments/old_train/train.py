import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.logger import configure
from stable_baselines3.common.callbacks import BaseCallback
import subprocess

from agents import KillerVictimEnv

import sys

# Number of episodes to stop training
N_EPISODES = 10

class StopEp(BaseCallback):
    def __init__(self, n_episodes=2, verbose=0, agent=None):
        super().__init__(verbose)
        self.n_episodes = n_episodes
        self.episode_count = 0
        self.agent = agent

    def _on_step(self) -> bool:
        # Verifica se un episodio è terminato
        if self.locals.get("dones") is not None:
            if any(self.locals["dones"]):
                self.episode_count += sum(self.locals["dones"])
                print(f"Episodi completati: {self.episode_count}")

                logs = self.logger.name_to_value
                # Calcola il reward totale dell'episodio corrente
                rewards = self.locals.get("rewards")
                total_reward = None
                if rewards is not None:
                    # Somma i reward dell'ultimo step per tutti gli agenti
                    if isinstance(rewards, (list, tuple)):
                        total_reward = sum(rewards)
                    else:
                        total_reward = rewards

                if "train/learning_rate" in logs:
                    print(f"\nStep {self.episode_count}")
                    print(f"  Learning Rate     : {logs['train/learning_rate']:.6f}")
                    print(
                        f"  Policy Loss       : {logs.get('train/policy_loss', 'N/A')}"
                    )
                    print(
                        f"  Value Loss        : {logs.get('train/value_loss', 'N/A')}"
                    )
                    print(
                        f"  Entropy           : {logs.get('train/entropy_loss', 'N/A')}"
                    )
                    print(f"  Approx KL         : {logs.get('train/approx_kl', 'N/A')}")
                    print(
                        f"  Explained Var     : {logs.get('train/explained_variance', 'N/A')}"
                    )
                    print(f"  Total Reward      : {total_reward}")

                with open("Logs/" + self.agent + "_log/log.txt", "a") as f:
                    f.write(f"Step {self.episode_count}\n")
                    f.write(
                        f"  Learning Rate     : {logs['train/learning_rate']:.6f}\n"
                    )
                    f.write(
                        f"  Policy Loss       : {logs.get('train/policy_loss', 'N/A')}\n"
                    )
                    f.write(
                        f"  Value Loss        : {logs.get('train/value_loss', 'N/A')}\n"
                    )
                    f.write(
                        f"  Entropy           : {logs.get('train/entropy_loss', 'N/A')}\n"
                    )
                    f.write(
                        f"  Approx KL         : {logs.get('train/approx_kl', 'N/A')}\n"
                    )
                    f.write(
                        f"  Explained Var     : {logs.get('train/explained_variance', 'N/A')}\n"
                    )
                    f.write(f"  Total Reward      : {total_reward}\n")
                    f.write(
                        f"-------------------------------------------------------------------------------------\n"
                    )

                if self.episode_count >= self.n_episodes:
                    print(f"Training fermato dopo {self.episode_count} episodi.")
                    return False  # Ferma il training
        return True


def trainable(agent: str):
    # Configurazione dell'environment
    env_config = {"agent": agent}  # o "killer"

    # Creazione dell'environment
    env = KillerVictimEnv(config=env_config)

    # (Opzionale) Controllo compatibilità environment
    check_env(env, warn=True)

    log_path = "./Logs/" + agent + "_log/"
    new_logger = configure(log_path, ["stdout", "csv", "tensorboard"])

    # Definizione del modello RL
    # model = PPO("MlpPolicy", env=env, verbose=2, learning_rate=0.0003, n_steps=2048 if agent == "victim" else 1024, batch_size=128, ent_coef=0.02, clip_range=0.2, gae_lambda=0.98)

    for _ in range(30):
        model = PPO.load(
            "./Model_game/ppo_" + agent + "_3",
            env=env,
            verbose=2,
            learning_rate=0.0003,
            n_steps=1024 if agent == "victim" else 256,
            batch_size=128,
            ent_coef=0.02,
            clip_range=0.2,
            gae_lambda=0.98,
        )

        # Training
        model.learn(
            callback=StopEp(n_episodes=5, agent=agent),
            progress_bar=True,      
            total_timesteps=100000000000,
            log_interval=1,
        )

        # Salvataggio del modello
        model.save("./Model_game/ppo_" + agent + "_3")

        print("[TRAIN] Model saved succesfuly")
        print("[TRAIN] Restart training with 10 EP")
        
        

    # Chiusura dell'environment
    env.close()


if __name__ == "__main__":
    trainable(sys.argv[1])  # Passa l'agente come argomento da riga di comando
