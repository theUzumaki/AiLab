import argparse, time, fcntl, json
import os

import matplotlib.pyplot as plt

def get_args():
    """
        Description:
        Parses arguments at command line.

        Parameters:
            None

        Return:
            args - the arguments parsed
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--agent', dest='agent', type=str, default='')          
    parser.add_argument('--n_ep', dest='episodes', type=int, default=100)     
    parser.add_argument('--ep_ibatch', dest='ibatch_ep', type=int, default=1)
    parser.add_argument('--ep_fbatch', dest='fbatch_ep', type=int, default=5)
    parser.add_argument('--log_file', dest='log_file', type=str, default='log.txt')
    parser.add_argument('--batch_ppo', dest='batch', type=int, default=32)
    parser.add_argument('--learning_rate', dest='learning_rate', type=float, default=1e-4)
    parser.add_argument('--n_train', dest='n_train', type=int, default=0)

    args = parser.parse_args()

    return args

def reset_files(agent):
    """
        Resets the debug files for both agents.
    """

    all_files = [
         "Comunications_files/ack_"+agent+".json", 
         "Comunications_files/game_state_"+agent+".json",
         "Comunications_files/action_"+agent+".json", 
         f"Object_detection/detections_{"jason" if agent == "killer" else "panam"}.json"]
    
    for c_file in all_files:
        try:
            with open(c_file, "r+") as f:
                f.seek(0)
                f.truncate()
        except FileNotFoundError:
            print(f"[WARNING] File {c_file} not found. Skipping reset.")

    print("[INFO] Debug files reset")

def wait_for_ack(path):
    while True:
        try:
            with open(path, 'r+') as f:
                # Lock the file to prevent concurrent reads
                fcntl.flock(f, fcntl.LOCK_SH)
                ack = json.load(f)

                # Svuota il contenuto del file
                f.seek(0)
                f.truncate()

                # Unlock the file after reading
                fcntl.flock(f, fcntl.LOCK_UN)
                return ack
        except FileNotFoundError:
            time.sleep(0.2)
        except json.JSONDecodeError:
            time.sleep(0.2)

def get_absolute_path(relative_path):
    """
    Returns the absolute path relative to the current working directory
    when the program is executed.

    Parameters:
        relative_path (str): The relative path to resolve.

    Returns:
        str: The absolute path.
    """
    return os.path.abspath(os.path.join(os.getcwd(), relative_path))

# Function used to save data in the log file
def log_episode(log_file, episode, lr, policy_loss, value_loss, entropy, approx_kl, total_reward):
    with open(log_file, "a") as f:
        f.write(f"Episode_number {episode}\n")
        f.write(f"  Learning Rate     : {lr:.6f}\n")
        f.write(f"  Policy Loss       : {policy_loss if policy_loss is not None else 'N/A'}\n")
        f.write(f"  Value Loss        : {value_loss if value_loss is not None else 'N/A'}\n")
        f.write(f"  Entropy           : {entropy if entropy is not None else 'N/A'}\n")
        f.write(f"  Approx KL         : {approx_kl if approx_kl is not None else 'N/A'}\n")
        f.write(f"  Total Reward      : {total_reward if total_reward is not None else 'N/A'}\n")
        f.write("-------------------------------------------------------------------------------------\n\n")

import matplotlib.pyplot as plt

def plot_metrics(log_file, agent, n):
    episodes = []
    policy_losses = []
    value_losses = []
    approx_kls = []

    with open(log_file, 'r') as f:
        episode = None
        policy_loss = None
        value_loss = None
        approx_kl = None

        for line in f:
            if "Episode_number" in line:
                if episode is not None:
                    # Salva i dati solo se tutti i valori sono presenti
                    if (policy_loss is not None and value_loss is not None and approx_kl is not None):
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

        # Salva l'ultimo episodio se presente
        if episode is not None and (policy_loss is not None and value_loss is not None and approx_kl is not None):
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
    plt.savefig(f'../Plots/{agent}/policy_los_{n}.png')
    plt.close()

    # Value Loss Plot
    plt.figure(figsize=(6, 4))
    plt.plot(episodes, value_losses, marker='o', label='Value Loss', color='orange')
    plt.xlabel('Episodes')
    plt.ylabel('Loss')
    plt.title('Value Loss Over Episodes')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'../Plots/{agent}/value_loss_{n}.png')
    plt.close()

    # Approx KL Plot
    plt.figure(figsize=(6, 4))
    plt.plot(episodes, approx_kls, marker='o', label='Approx KL', color='green')
    plt.xlabel('Episodes')
    plt.ylabel('KL Divergence')
    plt.title('Approx KL Over Episodes')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'../Plots/{agent}/approx_kl_{n}.png')
    plt.close()

CLIP_EPSILON = 0.2
TARGET_KL = 0.01
GAMMA = 0.99
LAM = 0.95

ABSOLUTE_PATH = get_absolute_path("")
COM_FILES = ABSOLUTE_PATH + "/Comunications_files/"
OBJ_FILES = ABSOLUTE_PATH + "/Object_detection/"