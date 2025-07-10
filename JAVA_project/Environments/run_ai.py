from ppo import PPO, ActorCritic
import torch
from agents import KillerVictimEnv

from utils import extract_info_features_killer, extract_info_features_victim, get_args

class RL_AGENT:
    def __init__(self, env: KillerVictimEnv, n_info: int, battery_path: str, phone_path: str, move_path: str):
        self.env = env

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

        # Load model
        grid_shape = (
            self.env.observation_space.shape[0],
            self.env.observation_space.shape[1],
        )
        action_dim = self.env.action_space.n
        state_dim = grid_shape[0] * grid_shape[1] + n_info
        action_std_init = 0.6

        self.moving = ActorCritic(state_dim, action_dim, False, action_std_init).to(self.device)
        self.moving.load_state_dict(torch.load(move_path, map_location=lambda storage, loc: storage))

        if self.env.agent == "victim":
            self.battery = ActorCritic(state_dim, action_dim, False, action_std_init).to(self.device)
            self.battery.load_state_dict(torch.load(battery_path, map_location=lambda storage, loc: storage))

            self.phone = ActorCritic(state_dim, action_dim, False, action_std_init).to(self.device)
            self.phone.load_state_dict(torch.load(phone_path, map_location=lambda storage, loc: storage))


    def run(self, num_episodes=1000):
        for episode in range(num_episodes):
            obs, info = self.env.reset()
            done = False
            total_reward = 0
            
            while not done:
                grid_tensor = torch.FloatTensor(obs).reshape(-1) / 100.0
                if self.env.agent == "victim":
                    info_features = extract_info_features_victim(info)
                else:
                    info_features = extract_info_features_killer(info)

                info_tensor = torch.FloatTensor(info_features)
                state = (torch.cat([grid_tensor, info_tensor]).unsqueeze(0).to(self.device))

                with torch.no_grad():
                    state = torch.FloatTensor(state.cpu().numpy().flatten()).to(self.device)

                    if self.env.agent == "killer":
                        print("[MODEL] Focusing on moving")
                        self.env.set_focus("jason")
                        action, _, _ = self.moving.act(state)
                    elif (info["killer_visible"] and self.env.agent == "victim"):
                        print("[MODEL] Focusing on moving")
                        self.env.set_focus("jason")
                        action, _, _ = self.moving.act(state)
                    if self.env.agent == "victim" and ((float(info["agent_x"]) < 400 and info["map"] == 0 and not info["battery"]) or (info["map"] == 1) or (info["map"] == 0 and info["phone"])):
                        print("[MODEL] Focusing on battery")
                        self.env.set_focus("exit_battery")
                        action, _, _ = self.battery.act(state)
                    elif self.env.agent == "victim" and ((float(info["agent_x"]) >= 400 and info["map"] == 0 and not info["phone"]) or (info["map"] == 2) or (info["map"] == 0 and info["battery"])):
                        print("[MODEL] Focusing on phone")
                        self.env.set_focus("exit_phone")
                        action, _, _ = self.phone.act(state)

                next_obs, reward, terminated, truncated, next_info = self.env.step(action.item())

                obs = next_obs
                info = next_info
                done = terminated or truncated
                total_reward += reward
            
            print(f"Episode {episode + 1}: Total Reward: {total_reward}")

if __name__ == "__main__":
    args = get_args()
    env = KillerVictimEnv(config={"agent": args.agent, "map": args.map, "focus": args.focus}, debug=args.debug)
    n_info = 22 if args.agent == "victim" else 14
    
    battery_path = "./Model_game/victim/modello_ppo_3.pth" if args.agent == "victim" else ""
    phone_path = "./Model_game/victim/modello_ppo_4.pth" if args.agent == "victim" else ""
    move_path = "./Model_game/killer/modello_ppo_5.pth" if args.agent == "killer" else "./Model_game/victim/modello_ppo_5.pth"

    RL_AGENT(env, n_info, battery_path, phone_path, move_path).run(num_episodes=args.episodes)