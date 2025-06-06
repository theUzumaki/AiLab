import numpy as np
import torch
import torch.optim as optim
import torch.nn.functional as F
from agents import KillerVictimEnv
from network import ActorCritic

from utils import log_episode, get_args, plot_metrics, send_mail_with_logs, extract_info_features_victim, extract_info_features_killer 
from utils import CLIP_EPSILON, TARGET_KL, GAMMA, LAM

def compute_gae(rewards, values):
    advantages = []
    gae = 0
    values = values + [0]
    for t in reversed(range(len(rewards))):
        delta = rewards[t] + GAMMA * values[t + 1] - values[t]
        gae = delta + GAMMA * LAM * gae
        advantages.insert(0, gae)
    return advantages

def ppo_update_v2(model, optimizer, states, actions, log_probs_old, returns, advantages, epochs=4, batch_size=32):
    
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
            surr2 = torch.clamp(ratio, 1.0 - CLIP_EPSILON, 1.0 + CLIP_EPSILON) * batch_advantages
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
            if kl > 1.5 * TARGET_KL:
                print(f"Early stopping PPO update per KL troppo alto: {kl:.4f}")
                break

    approx_kl /= (epochs * max(1, dataset_size // batch_size))
    return policy_loss.item(), value_loss.item(), entropy.item(), approx_kl

def train(env, model, optimizer, num_episodes=150, log_file="log.txt", episodes_per_batch=1, max_episode_batch=5, batch_ppo = 32):
    episode = 0
    prev_policy_loss = None
    prev_value_loss = None

    while episode < num_episodes:
        # Usa sempre il valore corrente di episodes_per_batch (non più dipendente da episode)
        current_batch = episodes_per_batch

        # Buffer per batch multipli di episodi
        batch_states, batch_actions, _, _, batch_log_probs, batch_returns, batch_advantages = [], [], [], [], [], [], []
        batch_total_rewards = []

        for _ in range(current_batch):
            obs, info = env.reset()
            done = False
            total_reward = 0

            states, actions, rewards, values, log_probs = [], [], [], [], []

            while not done:
                obs_tensor = torch.FloatTensor(obs).flatten() / 100.0  # (50,)
                if env.agent == "victim":
                    info_features = extract_info_features_victim(info)            # (n_info,)
                else:
                    info_features = extract_info_features_killer(info)            # (n_info,)
                full_obs = np.concatenate([obs_tensor.numpy(), info_features])  # (50 + n_info,)
                full_obs_tensor = torch.FloatTensor(full_obs).unsqueeze(0)      # (1, 50 + n_info)
                action, log_prob, _, value = model.act(full_obs_tensor)
                next_obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                reward = np.clip(reward, -1.0, 1.0)

                states.append(torch.FloatTensor(full_obs))
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
                R = r + GAMMA * R
                returns.insert(0, R)

            # Normalizzazione dei returns
            returns = np.array(returns)
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)
            returns = returns.tolist()

            advantages = compute_gae(rewards, values)

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
            model, optimizer, batch_states, batch_actions, batch_log_probs, batch_returns, batch_advantages, batch_size = batch_ppo)

        lr = optimizer.param_groups[0]['lr']
        # Logga la media dei reward degli episodi nel batch
        avg_total_reward = np.mean(batch_total_rewards)
        log_episode(log_file, episode, lr, policy_loss, value_loss, entropy_val, approx_kl, avg_total_reward)
        print(f"Episodes {episode - episodes_per_batch + 1}-{episode}/{num_episodes}, Avg Total Reward: {avg_total_reward}")

        # --- Adattamento dinamico episodes_per_batch ---
        POLICY_LOSS_THRESHOLD = 0.5
        VALUE_LOSS_THRESHOLD = 0.5

        if prev_policy_loss is not None and prev_value_loss is not None:
            if (abs(policy_loss - prev_policy_loss) > POLICY_LOSS_THRESHOLD or
                abs(value_loss - prev_value_loss) > VALUE_LOSS_THRESHOLD):
                episodes_per_batch = min(episodes_per_batch + 1, max_episode_batch)
                print(f"[ADAPTIVE] Aumento episodes_per_batch a {episodes_per_batch} per maggiore stabilità.")
                if episodes_per_batch == max_episode_batch:
                    print("[TRAINING] Training instabile")
                    break

        prev_policy_loss = policy_loss
        prev_value_loss = value_loss

if __name__ == "__main__":

    try:
        # Get argument
        args = get_args()

        print("[DEBUG]")
        print("Argomenti passati:")
        for k, v in vars(args).items():
            print(f"  {k}: {v}")

        # Set the env
        env = KillerVictimEnv(config={"agent": args.agent, "map": args.map})  # or "victim"
        obs_dim = env.observation_space.shape[0] * env.observation_space.shape[1] + (9 if args.agent == "victim" else 5)
        act_dim = env.action_space.n

        # Set the model
        model = ActorCritic(obs_dim, act_dim)

        percorso_modello = f"Model_game/{args.agent}/model_5.pth"
        try:
            model.load_state_dict(torch.load(percorso_modello))
            print(f"Modello caricato da {percorso_modello}")
        except FileNotFoundError:
            print("Nessun modello precedente trovato, si parte da zero.")

        optimizer = optim.Adam(model.parameters(), lr=1e-4)

        # Start training
        log = "Logs/" + args.agent + "_log/" + args.log_file

        train(env, model, optimizer, 
            num_episodes=args.episodes,
            log_file=log,
            episodes_per_batch=args.ibatch_ep,
            max_episode_batch=args.fbatch_ep,
            batch_ppo=args.batch    
        )

        torch.save(model.state_dict(), f"Model_game/{args.agent}/model_5.pth")
        plot_metrics(log, args.agent, args.n_train)

        send_mail_with_logs(
            subject=f"Training {args.agent} PPO",
            body="In allegato i log del training.",
            to="lachithaperera75@gmail.com",
            files=[
                log,
                f"../Plots/{args.agent}/total_rewards_{args.n_train}.png"
                f"../Plots/{args.agent}/approx_kl_{args.n_train}.png"
                f"../Plots/{args.agent}/value_loss_{args.n_train}.png"
                f"../Plots/{args.agent}/policy_los_{args.n_train}.png"
            ]
        )
    except Exception as e:
        send_mail_with_logs(
            subject=f"Error training {args.agent} PPO",
            body=f"In allegato i log del training, ha dato il seguente errore\n {e}",
            to="lachithaperera75@gmail.com",
            files=[
                log
            ]
        )