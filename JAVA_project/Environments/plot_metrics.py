import matplotlib.pyplot as plt

def plot_metrics(log, agent, focus):
        episodes = []
        policy_losses = []
        value_losses = []
        approx_kls = []

        with open(log, 'r') as f:
            episode = None
            policy_loss = None
            value_loss = None
            approx_kl = None

            for line in f:
                if "Episode_number" in line:
                    if episode is not None:
                        if (policy_loss is not None and value_loss is not None and approx_kl is not None):
                            if episode % 5 == 0 or episode % 3 == 0:
                                episodes.append(episode)
                                policy_losses.append(policy_loss)
                                value_losses.append(value_loss)
                                approx_kls.append(approx_kl)
                    episode = int(line.split()[1])
                    policy_loss = None
                    value_loss = None
                    approx_kl = None
                elif "Policy Loss" in line:
                    try:
                        policy_loss = float(line.split(':')[1].strip())
                    except:
                        policy_loss = None
                elif "Value Loss" in line:
                    try:
                        value_loss = float(line.split(':')[1].strip())
                    except:
                        value_loss = None
                elif "Approx KL" in line:
                    try:
                        approx_kl = float(line.split(':')[1].strip())
                    except:
                        approx_kl = None

            if episode is not None and (policy_loss is not None and value_loss is not None and approx_kl is not None):
                if episode % 5 == 0 or episode % 3 == 0:
                    episodes.append(episode)
                    policy_losses.append(policy_loss)
                    value_losses.append(value_loss)
                    approx_kls.append(approx_kl)

        # Policy Loss Plot
        plt.figure(figsize=(6, 4))
        plt.plot(episodes, policy_losses, marker='o', label='Policy Loss', color='blue')
        plt.xlabel('Episodes')
        plt.ylabel('Loss')
        plt.title('Policy Loss Over Episodes')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'../Plots/{agent}/policy_loss_{focus}.png')
        plt.close()

        # Value Loss Plot
        plt.figure(figsize=(6, 4))
        plt.plot(episodes, value_losses, marker='o', label='Value Loss', color='orange')
        plt.xlabel('Episodes')
        plt.ylabel('Loss')
        plt.title('Value Loss Over Episodes')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'../Plots/{agent}/value_loss_{focus}.png')
        plt.close()

        # Approx KL Plot
        plt.figure(figsize=(6, 4))
        plt.plot(episodes, approx_kls, marker='o', label='Approx KL', color='green')
        plt.xlabel('Episodes')
        plt.ylabel('KL Divergence')
        plt.title('Approx KL Over Episodes')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'../Plots/{agent}/approx_kl_{focus}.png')
        plt.close()

        print("[PLOT] Saved")

def merge_logs(log_files):
    output_file = "log_unificato.txt"
    episode_offset = 0

    with open(output_file, "w") as fout:
        for log in log_files:
            max_episode_in_file = 0
            try:
                with open(log, "r") as fin:
                    lines = fin.readlines()
                    for i, line in enumerate(lines):
                        if "Episode_number" in line:
                            episode_num = int(line.split()[1])
                            new_episode_num = episode_num + episode_offset
                            line = f"Episode_number {new_episode_num}\n"
                            if episode_num > max_episode_in_file:
                                max_episode_in_file = episode_num
                        fout.write(line)
                episode_offset += max_episode_in_file
            except Exception as e:
                continue

    print(f"[MERGE] Merged logs into {output_file} with episode offset {episode_offset}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plot metrics from training logs.")
    parser.add_argument("--agent", type=str, required=True, help="Agent type (e.g., 'victim' or 'attacker').")
    parser.add_argument("--focus", type=str, required=True, help="Focus of the plot (e.g., 'train' or 'test').")
    parser.add_argument("--start", type=int, required=True, help="Start of the plot (e.g., 'train' or 'test').")
    parser.add_argument("--end", type=int, required=True, help="End of the plot (e.g., 'train' or 'test').")
    args = parser.parse_args()

    list_files = []
    for i in range(args.start, args.end + 1):
        list_files.append(f"Logs/{args.agent}_log/log_{i}.txt")

    # print(list_files)
    merge_logs(list_files)
    plot_metrics("log_unificato.txt", args.agent, args.focus)