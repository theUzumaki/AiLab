import numpy as np
import torch
import torch.optim as optim
import torch.nn.functional as F
from agents import KillerVictimEnv
from network import ActorCritic

from utils import log_episode, get_args, plot_metrics
from utils import CLIP_EPSILON, CLIP_EPSILON, TARGET_KL, GAMMA, LAM

def compute_gae(rewards, values, gamma=GAMMA, lam=LAM):
    advantages = []
    gae = 0
    values = values + [0]
    for t in reversed(range(len(rewards))):
        delta = rewards[t] + gamma * values[t + 1] - values[t]
        gae = delta + gamma * lam * gae
        advantages.insert(0, gae)
    return advantages

def ppo_update_v2( model, optimizer, states, actions, log_probs_old, returns, advantages,
    clip_epsilon=CLIP_EPSILON, epochs=4, batch_size=32, target_kl=TARGET_KL):
    
    if len(states) == 0:
        print("[DEBUG] states empty")
        # Batch vuoto, ritorna valori di default
        return 0.0, 0.0, 0.0, 0.0
    
    states = torch.stack(states).float()
    actions = torch.tensor(actions, dtype=torch.long)
    log_probs_old = torch.stack(log_probs_old).float()
    returns = torch.tensor(returns, dtype=torch.float32)
    advantages = torch.tensor(advantages, dtype=torch.float32)
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    dataset_size = states.size(0)
    approx_kl = 0

    # Inizializza i valori di default
    policy_loss = value_loss = entropy = torch.tensor(0.0)

    for _ in range(int(epochs)):
        idx = torch.randperm(dataset_size)
        for start in range(0, dataset_size, batch_size):
            end = start + batch_size
            batch_idx = idx[start:end]

            batch_states = states[batch_idx]
            batch_actions = actions[batch_idx]
            batch_log_probs_old = log_probs_old[batch_idx]
            batch_returns = returns[batch_idx]
            batch_advantages = advantages[batch_idx]

            logits, values = model(batch_states)
            dist = torch.distributions.Categorical(logits=logits)
            log_probs = dist.log_prob(batch_actions)
            entropy = dist.entropy().mean()

            ratio = torch.exp(log_probs - batch_log_probs_old)
            surr1 = ratio * batch_advantages
            surr2 = torch.clamp(ratio, 1.0 - clip_epsilon, 1.0 + clip_epsilon) * batch_advantages
            policy_loss = -torch.min(surr1, surr2).mean()
            value_loss = F.mse_loss(values.view(-1), batch_returns.view(-1))
            loss = policy_loss + 0.5 * value_loss - 0.01 * entropy

            # Approximate KL divergence
            with torch.no_grad():
                kl = (batch_log_probs_old - log_probs).mean().item()
                approx_kl += kl

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
            optimizer.step()

            # Early stopping se KL troppo alto
            if kl > 1.5 * target_kl:
                print(f"Early stopping PPO update per KL troppo alto: {kl:.4f}")
                break

    approx_kl /= (epochs * max(1, dataset_size // batch_size))
    return policy_loss.item(), value_loss.item(), entropy.item(), approx_kl

def train(env, model, optimizer, num_episodes=150, log_file="log.txt", gamma=GAMMA, lam=LAM, clip_epsilon=CLIP_EPSILON, episodes_per_batch=1, max_episode_batch=5):
    episode = 0
    while episode < num_episodes:
        current_batch = episodes_per_batch + episode // 5
        current_batch = min(current_batch, max_episode_batch)

        # Buffer per batch multipli di episodi
        batch_states, batch_actions, _, _, batch_log_probs, batch_returns, batch_advantages = [], [], [], [], [], [], []
        batch_total_rewards = []

        for _ in range(current_batch):
            obs, _ = env.reset()
            done = False
            total_reward = 0

            states, actions, rewards, values, log_probs = [], [], [], [], []

            while not done:
                obs_tensor = torch.FloatTensor(obs).unsqueeze(0).unsqueeze(0) / 100.0
                action, log_prob, _, value = model.act(obs_tensor)
                next_obs, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                reward = np.clip(reward, -1.0, 1.0)

                states.append(obs_tensor.squeeze(0))
                actions.append(action)
                rewards.append(reward)
                values.append(value.squeeze().item())
                log_probs.append(log_prob.detach())

                total_reward += reward
                obs = next_obs

            # Calcolo returns e vantaggi (GAE)
            returns = []
            R = 0
            for r in reversed(rewards):
                R = r + gamma * R
                returns.insert(0, R)

            # Normalizzazione dei returns
            returns = np.array(returns)
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)
            returns = returns.tolist()

            advantages = compute_gae(rewards, values, gamma, lam)

            # Accumula batch
            batch_states.extend(states)
            batch_actions.extend(actions)
            batch_log_probs.extend(log_probs)
            batch_returns.extend(returns)
            batch_advantages.extend(advantages)
            batch_total_rewards.append(total_reward)

            episode += 1
            if episode >= num_episodes:
                break

        # PPO update su tutto il batch accumulato
        policy_loss, value_loss, entropy_val, approx_kl = ppo_update_v2(
            model, optimizer, batch_states, batch_actions, batch_log_probs, batch_returns, batch_advantages, clip_epsilon
        )

        lr = optimizer.param_groups[0]['lr']
        # Logga la media dei reward degli episodi nel batch
        avg_total_reward = np.mean(batch_total_rewards)
        log_episode(log_file, episode, lr, policy_loss, value_loss, entropy_val, approx_kl, avg_total_reward)
        print(f"Episodes {episode - episodes_per_batch + 1}-{episode}/{num_episodes}, Avg Total Reward: {avg_total_reward}")

if __name__ == "__main__":
    
    # Get argument
    args = get_args()

    print("[DEBUG]")
    print("Argomenti passati:")
    for k, v in vars(args).items():
        print(f"  {k}: {v}")

    # Set the env
    env = KillerVictimEnv(config={"agent": args.agent})  # or "victim"
    obs_dim = env.observation_space.shape[0] * env.observation_space.shape[1]
    act_dim = env.action_space.n

    # Set the model
    model = ActorCritic(obs_dim, act_dim)

    percorso_modello = f"Model_game/{args.agent}/model_3.pth"
    try:
        model.load_state_dict(torch.load(percorso_modello))
        print(f"Modello caricato da {percorso_modello}")
    except FileNotFoundError:
        print("Nessun modello precedente trovato, si parte da zero.")

    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    # Start training
    log = "Logs/" + args.agent + "_log/" + args.log_file
    train(env, model, optimizer, 
          num_episodes=args.episodes,
          log_file=log,
          episodes_per_batch=args.ibatch_ep,
          max_episode_batch=args.fbatch_ep)

    torch.save(model.state_dict(), f"Model_game/{args.agent}/model_3.pth")
    plot_metrics(log, args.agent, args.n_train)
