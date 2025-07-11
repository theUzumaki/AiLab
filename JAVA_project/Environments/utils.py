import argparse, time, fcntl, json
import os
import numpy as np


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

    parser.add_argument("--agent", dest="agent", type=str, default="")
    parser.add_argument("--player", dest="player", type=str, default="")  # 'killer' or 'victim'
    parser.add_argument("--train", dest="train", action="store_true")

    parser.add_argument("--n_ep", dest="episodes", type=int, default=100)
    parser.add_argument("--log_file", dest="log_file", type=str, default="log.txt")
    parser.add_argument("--n_train", dest="n_train", type=int, default=0)
    parser.add_argument("--batch-size-victim", dest="batch_size_v", type=int, default=512)
    parser.add_argument("--batch-size-killer", dest="batch_size_k", type=int, default=512)

    parser.add_argument("--lr_actor", dest="lr_actor", type=float, default=1e-3)
    parser.add_argument("--lr_critic", dest="lr_critic", type=float, default=0.001)
    parser.add_argument("--entropy-v", dest="entropy_v", type=float, default=0.01)
    parser.add_argument("--entropy-k", dest="entropy_k", type=float, default=0.01)
    parser.add_argument("--debug", dest="debug", action="store_true")

    parser.add_argument("--map", dest="map", type=int, default=0)
    parser.add_argument("--focus", dest="focus", type=str, default="")
    parser.add_argument("--max-distance", dest="max_distance", type=int, default=0)
    parser.add_argument("--show", dest="show", action="store_true")
    parser.add_argument("--java-pid", dest="java_pid", type=str, default="")

    parser.add_argument("--neuron", dest="neuron", type=int, default=128)
    parser.add_argument("--clip", dest="clip", type=float, default=0.1)
    parser.add_argument("--gamma", dest="gamma", type=float, default=0.99)
    parser.add_argument("--epochs", dest="epochs", type=int, default=4)
    parser.add_argument("--critic", dest="critic", action="store_true")
    parser.add_argument("--deterministic", dest="deterministic", action="store_true")

    args = parser.parse_args()

    return args


def reset_files(agent):
    """
    Resets the debug files for both agents.
    """

    all_files = [
        "Comunications_files/ack_" + agent + ".json",
        "Comunications_files/game_state_" + agent + ".json",
        "Comunications_files/action_" + agent + ".json",
        f"Object_detection/detections_{"jason" if agent == "killer" else "panam"}.json",
    ]

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
            with open(path, "r+") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                ack = json.load(f)
                f.seek(0)
                f.truncate()
                fcntl.flock(f, fcntl.LOCK_UN)
                return ack
        except FileNotFoundError:
            time.sleep(0.2)
        except json.JSONDecodeError:
            time.sleep(0.2)


def distance(x1, y1, x2, y2):
    """
    Calculate the Euclidean distance between two points (x1, y1) and (x2, y2).
    Parameters:
        x1 (float): x-coordinate of the first point.
        y1 (float): y-coordinate of the first point.
    returns:
        float: The Euclidean distance between the two points.
    """
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


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


def extract_info_features_victim(info):
    # Ordine delle chiavi fisso per coerenza
    keys = [
        "end-game",
        "map",
        "win",
        "finished",
        "dead",
        "distance_1_x",
        "distance_2_x",
        "distance_1_y",
        "distance_2_y",
        "battery",
        "phone",
        "status",
        "killer_visible",
        "killer_distance",
        "num_win",
        "num_hide",
        "num_slow",
        "num_interaction",
        "num_obstacle",
        "agent_x",
        "agent_y",
    ]
    features = []
    for k in keys:
        v = info.get(k, 0)
        if k == "map":
            features.append(float(v) / 2.0)
        if k == "distance_1_x":
            features.append(float(v) / 800.0 if info["map"] == 0 else float(v) / 320.0)
        elif k == "distance_2_x":
            features.append(float(v) / 800.0 if info["map"] == 0 else float(v) / 320.0)
        elif k == "distance_1_y":
            features.append(float(v) / 400.0 if info["map"] == 0 else float(v) / 160.0)
        elif k == "distance_2_y":
            features.append(float(v) / 400.0 if info["map"] == 0 else float(v) / 160.0)
        elif k == "status":
            if v == "visible":
                features.append(1.0)
            elif v == "hide":
                features.append(0.5)
            else:
                features.append(0.0)
        elif k == "num_obstacle":
            features.append(float(v) / 9.0)
        elif k == "num_win":
            features.append(float(v) / 1.0)
        elif k == "num_hide":
            features.append(float(v) / 3.0)
        elif k == "num_interaction":
            features.append(float(v) / 9.0)
        elif k == "num_slow":
            features.append(float(v) / 9.0)
        elif k == "killer_distance":
            features.append(float(v))
        elif k == "agent_x":
            if info["map"] == 0:
                features.append(float(v) / 800.0)
            else:
                features.append(float(v) / 320.0)
        elif k == "agent_y":
            if info["map"] == 0:
                features.append(float(v) / 400.0)
            else:
                features.append(float(v) / 160.0)
        elif isinstance(v, bool):
            features.append(float(v))
        else:
            features.append(0.0)
    return np.array(features, dtype=np.float32)


def extract_info_features_killer(info):
    keys = [
        "end-game",
        "map",
        "win",
        "finished",
        "sub_map",
        "status",
        "victim_visible",
        "num_win",
        "num_hide",
        "num_slow",
        "num_interaction",
        "num_obstacle",
        "agent_x",
        "agent_y",
    ]
    features = []
    for k in keys:
        v = info.get(k, 0)
        if k == "map":
            features.append(float(v) / 2.0)
        elif k == "sub_map":
            features.append(float(v) / 4.0)
        elif k == "status":
            if v == "visible":
                features.append(1.0)
            elif v == "interact":
                features.append(0.5)
            else:
                features.append(0.0)
        elif k == "num_obstacle":
            features.append(float(v) / 9.0)
        elif k == "num_win":
            features.append(float(v) / 1.0)
        elif k == "num_hide":
            features.append(float(v) / 3.0)
        elif k == "num_interaction":
            features.append(float(v) / 9.0)
        elif k == "num_slow":
            features.append(float(v) / 9.0)
        elif k == "agent_x":
            if info["map"] == 0:
                features.append(float(v) / 800.0)
            else:
                features.append(float(v) / 320.0)
        elif k == "agent_y":
            if info["map"] == 0:
                features.append(float(v) / 400.0)
            else:
                features.append(float(v) / 160.0)
        elif isinstance(v, bool):
            features.append(float(v))
        else:
            features.append(0.0)
    return np.array(features, dtype=np.float32)


def log_episode(
    log_file,
    episode,
    lr_actor,
    lr_critic,
    policy_loss,
    value_loss,
    entropy,
    approx_kl,
    total_reward,
    battery,
    phone,
    enter_house_phone,
    victim,
    focus
):
    with open(log_file, "a") as f:
        f.write(f"Episode_number {episode}\n")
        f.write(f"  Lr Actor          : {lr_actor:.6f}\n")
        f.write(f"  Lr Critic         : {lr_critic:.6f}\n")
        f.write(
            f"  Policy Loss       : {policy_loss if policy_loss is not None else 'N/A'}\n"
        )
        f.write(
            f"  Value Loss        : {value_loss if value_loss is not None else 'N/A'}\n"
        )
        f.write(f"  Entropy           : {entropy if entropy is not None else 'N/A'}\n")
        f.write(
            f"  Approx KL         : {approx_kl if approx_kl is not None else 'N/A'}\n"
        )
        f.write(
            f"  Total Reward      : {total_reward if total_reward is not None else 'N/A'}\n"
        )
        if victim:
            if focus != "jason":
                f.write(f"  Phone             : {battery}\n")
                f.write(f"  Exit House        : {phone}\n")
                f.write(f"  Enter House       : {enter_house_phone}\n")
            else:
                f.write(f"  Victim alive      : {battery}\n")
        else:
            f.write(f"  Victim alive      : {battery}\n")
        f.write(
            "-------------------------------------------------------------------------------------\n\n"
        )

ABSOLUTE_PATH = get_absolute_path("")
COM_FILES = ABSOLUTE_PATH + "/Comunications_files/"
OBJ_FILES = ABSOLUTE_PATH + "/Object_detection/"