import torch
import numpy as np

from ppo import PPO
from agents import KillerVictimEnv

from utils import (
    extract_info_features_victim,
    extract_info_features_killer,
    get_args,
    log_episode
)


class Train:
    """
    This class is used to train a model with the PPO algorithm
    """

    def __init__(self, env: KillerVictimEnv, name_model: str, n_info: int, args):
        self.args = args

        # Set device based on availability
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("[TRAIN] Device set to: Apple Silicon GPU (mps)")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            print("[TRAIN] Device set to: CUDA GPU")
        else:
            self.device = torch.device("cpu")
            print("[TRAIN] Device set to: CPU")

        self.env = env

        # Setup model
        grid_shape = (
            self.env.observation_space.shape[0],
            self.env.observation_space.shape[1],
        )
        act_dim = self.env.action_space.n
        state_dim = grid_shape[0] * grid_shape[1] + n_info
        self.name_model = name_model

        # Setup log file
        self.log = "Logs/" + args.agent + "_log/" + args.log_file

        # Setup model path
        self.path_model = f"Model_game/{self.args.agent}/{self.name_model}.pth"

        # Setup PPO
        has_continuous_action_space = False
        action_std_init = 0.6  # Usato quando continuous action space è True

        self.ppo = PPO(
            state_dim=state_dim,
            action_dim=act_dim,
            lr_actor=self.args.lr_actor,
            lr_critic=self.args.lr_critic,
            gamma=self.args.gamma,
            K_epochs=self.args.epochs,
            eps_clip=self.args.clip,
            has_continuous_action_space=has_continuous_action_space,
            action_std_init=action_std_init,
            entropy_coef=self.args.entropy_v
            if self.env.agent == "victim"
            else self.args.entropy_k,
        )

        try:
            self.ppo.load(self.path_model)
            print(f"[TRAIN] Model {self.path_model} loaded successfully.")
        except FileNotFoundError:
            print(
                f"[TRAIN] Model {self.path_model} not found. Starting training from scratch."
            )
        self.batch_size = (
            self.args.batch_size_v
            if self.env.agent == "victim"
            else self.args.batch_size_k
        )

        if self.args.debug:
            print("[TRAIN] Train setup completed")

    def train(self):
        episode = 0
        battery = 0
        phone = 0
        total_reward = 0
        exit_house = 0
        enter_house_phon = 0
        dst = 0
        alive = 0

        while episode < self.args.episodes:
            obs, info = self.env.reset()
            done = False

            while not done:
                grid_tensor = torch.FloatTensor(obs).reshape(-1) / 100.0
                if self.env.agent == "victim":
                    info_features = extract_info_features_victim(info)
                else:
                    info_features = extract_info_features_killer(info)

                info_tensor = torch.FloatTensor(info_features)
                state = (
                    torch.cat([grid_tensor, info_tensor]).unsqueeze(0).to(self.device)
                )

                action = self.ppo.select_action(state.cpu().numpy().flatten())
                next_obs, reward, terminated, truncated, next_info = self.env.step(
                    action
                )

                if self.args.focus != "jason":
                    if self.env.agent == "victim" and (
                        info["battery"] != next_info["battery"] or info["phone"] != next_info["phone"]
                    ):
                        print(
                            f"[TRAIN] Battery/Phone changed from {info['phone']} to {next_info['phone']}"
                        )
                        phone += 1
                    elif (
                        self.env.agent == "victim"
                        and next_info["phone"] == False
                        and terminated
                    ):
                        print(f"[TRAIN] Phone not changed: {info['battery']}")
                        reward -= 10

                if self.args.focus == "jason":
                    
                    if self.env.agent == "victim" and not next_info["dead"] and terminated:
                        alive += 1
                    if self.env.agent == "killer" and not next_info["win"] and terminated:
                        alive += 1

                    if self.env.agent == "victim" and terminated and not next_info["dead"]:
                        reward += 10
                    if self.env.agent == "killer" and terminated and not next_info["win"]:
                        reward -= 10

                if self.args.focus == "exit_battery":
                    if (
                        self.env.agent == "victim"
                        and next_info["map"] == 0
                        and next_info["battery"]
                        and terminated
                    ):
                        print("[TRAIN] Victim exited the house")
                        exit_house += 1
                    elif (
                        self.env.agent == "victim"
                        and next_info["map"] != 0
                        and terminated
                    ):
                        print("[TRAIN] Victim is still in the house")
                        reward -= 20
                    elif (
                        self.env.agent == "victim"
                        and next_info["map"] == 0
                        and not next_info["battery"]
                        and terminated
                    ):
                        print(
                            "[TRAIN] Victim isn't in the house and not taked the battery"
                        )
                        reward -= 10

                if self.args.focus == "exit_phone":
                    if (
                        self.env.agent == "victim"
                        and next_info["map"] == 0
                        and next_info["phone"]
                        and terminated
                    ):
                        print("[TRAIN] Victim exited the house")
                        exit_house += 1
                    elif (
                        self.env.agent == "victim"
                        and next_info["map"] != 0
                        and terminated
                    ):
                        print("[TRAIN] Victim is still in the house")
                        reward -= 20
                    elif (
                        self.env.agent == "victim"
                        and next_info["map"] == 0
                        and not next_info["phone"]
                        and terminated
                    ):
                        print(
                            "[TRAIN] Victim isn't in the house and not taked the phone"
                        )
                        reward -= 10
                    
                done = terminated or truncated

                self.ppo.buffer.rewards.append(reward)
                self.ppo.buffer.is_terminals.append(done)

                obs = next_obs
                info = next_info
                total_reward += reward

                if self.args.debug:
                    print(total_reward)

            episode += 1

            if (
                len(self.ppo.buffer.states) >= self.batch_size
                or episode == self.args.episodes
            ):
                self.ppo.update()

                # Dopo ogni episodio
                policy_loss = getattr(self.ppo, "last_policy_loss", None)
                value_loss = getattr(self.ppo, "last_value_loss", None)
                entropy = getattr(self.ppo, "last_entropy", None)
                approx_kl = getattr(self.ppo, "last_approx_kl", None)
                actor_lr = self.ppo.optimizer.param_groups[0]["lr"]
                critic_lr = self.ppo.optimizer.param_groups[1]["lr"]

                log_episode(
                    self.log,
                    episode,
                    actor_lr,
                    critic_lr,
                    policy_loss,
                    value_loss,
                    entropy,
                    approx_kl,
                    total_reward,
                    phone if self.args.focus != "jason" else alive,
                    exit_house,
                    dst,
                    env.agent == "victim",
                    self.args.focus,
                )

                total_reward = 0
                battery = 0
                phone = 0
                dst = 0
                exit_house = 0
                alive = 0

            if args.debug:
                print(f"[TRAIN] Episode {episode} completed.")

        # Save model
        self.ppo.save(self.path_model)

        if self.args.java_pid != "" and self.args.focus != "jason":
            try:
                import os
                import signal

                os.kill(int(self.args.java_pid), signal.SIGTERM)
                print(f"[TRAIN] Java process {self.args.java_pid} terminated.")
            except Exception as e:
                print(f"[TRAIN] Error terminating Java process: {e}")

    def save_model(self):
        torch.save(self.model.state_dict(), self.path_model)

        if args.debug:
            print(f"[TRAIN] Modello salvato in {self.path_model}")


if __name__ == "__main__":
    args = get_args()
    env = KillerVictimEnv(
        config={"agent": args.agent, "map": args.map, "focus": args.focus}, debug=args.debug
    )
    n_info = 22 if args.agent == "victim" else 14
    name_model = f"modello_ppo_{args.n_train}"

    Train(env, name_model, n_info, args).train()
