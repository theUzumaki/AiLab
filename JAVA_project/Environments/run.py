import subprocess

from utils import reset_files, get_args, ABSOLUTE_PATH


def start_process_in_terminal(command):
    """
    Start process in a new terminal.
    """
    subprocess.Popen(
        ["osascript", "-e", f'tell app "Terminal" to do script "{command}"']
    )


def start_game_server(map: int, focus: str, show, max_distance):
    """
    Starts the Java game server for the Killer-Victim environment.
    """
    print("[INFO] Starting Java game server...")

    java_process = subprocess.Popen(
        [
            "java",
            "-cp",
            "bin:../Librerie/JSON-java 2025.jar",
            "main.Main",
            str(show),
            str(map),
            focus,
            str(max_distance),
        ]
    )

    import time

    time.sleep(5)  # Wait for the Java game to start
    print(f"[INFO] Java game server started PID: {java_process.pid}.")

    return java_process


if __name__ == "__main__":
    reset_files("killer")  # Reset the files for both agents
    reset_files("victim")  # Reset the files for both agents

    args = get_args()

    java_process = start_game_server(
        args.map, args.focus, args.show, args.max_distance
    )  # Start the Java game server

    if args.train:
        if args.player == "victim":
            command_victim = f"cd {ABSOLUTE_PATH} && source .venv/bin/activate && python3 Environments/train.py --agent victim --n_ep {args.episodes} --log_file {args.log_file} --lr_actor {args.lr_actor} --lr_critic {args.lr_critic} --n_train {args.n_train} --map {args.map} {'--debug' if args.debug else ''} --neuron {args.neuron} --epochs {args.epochs} --gamma {args.gamma} --clip {args.clip} {'--critic' if args.critic else ''} {'--deterministic' if args.deterministic else ''} --focus {args.focus} --entropy-v {args.entropy_v} --batch-size-victim {args.batch_size_v} --max-distance {args.max_distance} --java-pid {java_process.pid}"

            print(
                "[INFO] Starting training process for victim agent in a separate terminal..."
            )
            start_process_in_terminal(command_victim)
        elif args.player == "killer":
            command_killer = f"cd {ABSOLUTE_PATH} && source .venv/bin/activate && python3 Environments/train.py --agent killer --n_ep {args.episodes} --log_file {args.log_file} --lr_actor {args.lr_actor} --lr_critic {args.lr_critic} --n_train {args.n_train} --map {args.map} {'--debug' if args.debug else ''} --neuron {args.neuron} --epochs {args.epochs} --gamma {args.gamma} --clip {args.clip} {'--critic' if args.critic else ''} {'--deterministic' if args.deterministic else ''} --focus {args.focus} --entropy-k {args.entropy_k} --batch-size-killer {args.batch_size_k} --max-distance {args.max_distance} --java-pid {java_process.pid}"

            print(
                "[INFO] Starting training process for killer agent in a separate terminal..."
            )
            start_process_in_terminal(command_killer)
        else:
            command_killer = f"cd {ABSOLUTE_PATH} && source .venv/bin/activate && python3 Environments/train.py --agent killer --n_ep {args.episodes} --log_file {args.log_file} --lr_actor {args.lr_actor} --lr_critic {args.lr_critic} --n_train {args.n_train} --map {args.map} {'--debug' if args.debug else ''} --neuron {args.neuron} --epochs {args.epochs} --gamma {args.gamma} --clip {args.clip} {'--critic' if args.critic else ''} {'--deterministic' if args.deterministic else ''} --focus {args.focus} --entropy-k {args.entropy_k} --batch-size-killer {args.batch_size_k} --max-distance {args.max_distance}"
            command_victim = f"cd {ABSOLUTE_PATH} && source .venv/bin/activate && python3 Environments/train.py --agent victim --n_ep {args.episodes} --log_file {args.log_file} --lr_actor {args.lr_actor} --lr_critic {args.lr_critic} --n_train {args.n_train} --map {args.map} {'--debug' if args.debug else ''} --neuron {args.neuron} --epochs {args.epochs} --gamma {args.gamma} --clip {args.clip} {'--critic' if args.critic else ''} {'--deterministic' if args.deterministic else ''} --focus {args.focus} --entropy-v {args.entropy_v} --batch-size-victim {args.batch_size_v} --max-distance {args.max_distance}"

            print("[INFO] Starting training processes in separate terminals...")
            start_process_in_terminal(command_killer)
            start_process_in_terminal(command_victim)
    else:
        command_killer = f"cd {ABSOLUTE_PATH} && source .venv/bin/activate && python3 Environments/run_ai.py --agent killer --map {args.map} --focus {args.focus} {'--show' if args.show else ''} {'--debug' if args.debug else ''} --n_ep {args.episodes} "
        command_victim = f"cd {ABSOLUTE_PATH} && source .venv/bin/activate && python3 Environments/run_ai.py --agent victim --map {args.map} --focus {args.focus} {'--show' if args.show else ''} {'--debug' if args.debug else ''} --n_ep {args.episodes} "
        print("[INFO] Starting training processes in separate terminals for test...")
        start_process_in_terminal(command_killer)
        start_process_in_terminal(command_victim)