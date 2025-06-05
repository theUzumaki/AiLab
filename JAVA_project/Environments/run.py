import subprocess
from utils import reset_files, get_args

def start_process_in_terminal(command):
        """
        Avvia un processo in un nuovo terminale.
        """
        subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "{command}"'])
        
def start_game_server():
    """
    Starts the Java game server for the Killer-Victim environment.
    """
    print("[INFO] Starting Java game server...")

    # Run the game server before starting the training
    import subprocess
    subprocess.Popen(
        [
            "java",
            "-cp",
            "bin:../Librerie/JSON-java 2025.jar",
            "main.Main",
        ]
    )

    import time
    time.sleep(5)  # Wait for the Java game to start
    print("[INFO] Java game server started.")

if __name__ == "__main__":

    reset_files("killer")  # Reset the files for both agents
    reset_files("victim")  # Reset the files for both agents
    start_game_server()  # Start the Java game server

    args = get_args()

    # Comandi per avviare i processi
    command_killer = f"cd Documents/AiLab/JAVA_project && source .venv/bin/activate && python3 Environments/train.py --agent killer --n_ep {args.episodes} --ep_ibatch {args.ibatch_ep} --ep_fbatch {args.fbatch_ep} --log_file {args.log_file} --batch_ppo {args.batch} --learning_rate {args.learning_rate} --n_train {args.n_train}"
    command_victim = f"cd Documents/AiLab/JAVA_project && source .venv/bin/activate && python3 Environments/train.py --agent victim --n_ep {args.episodes} --ep_ibatch {args.ibatch_ep} --ep_fbatch {args.fbatch_ep} --log_file {args.log_file} --batch_ppo {args.batch} --learning_rate {args.learning_rate} --n_train {args.n_train}"

    print("[INFO] Starting training processes in separate terminals...")
    start_process_in_terminal(command_killer)
    start_process_in_terminal(command_victim)