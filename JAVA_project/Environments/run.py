import subprocess

from utils import reset_files, get_args

def start_process_in_terminal(command):
        """
        Avvia un processo in un nuovo terminale.
        """
        subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "{command}"'])
        
def start_game_server(map):
    """
    Starts the Java game server for the Killer-Victim environment.
    """
    print("[INFO] Starting Java game server...")

    # Avvia il processo Java e salva il riferimento al processo
    java_process = subprocess.Popen(
        [
            "java",
            "-cp",
            "bin:../Librerie/JSON-java 2025.jar",
            "main.Main",
            str(map)  # Assicurati che l'argomento sia un intero come richiesto da Java
        ]
    )
    # Puoi chiudere il processo in seguito usando java_process.terminate() o java_process.kill()

    import time
    time.sleep(5)  # Wait for the Java game to start
    print("[INFO] Java game server started.")

    return java_process

if __name__ == "__main__":

    reset_files("killer")  # Reset the files for both agents
    reset_files("victim")  # Reset the files for both agents
    
    args = get_args()

    java_process = start_game_server(args.map)  # Start the Java game server

    # Comandi per avviare i processi
    command_killer = f"cd Documents/AiLab/JAVA_project && source .venv/bin/activate && python3 Environments/train.py --agent killer --n_ep {args.episodes} --ep_ibatch {args.ibatch_ep} --ep_fbatch {args.fbatch_ep} --log_file {args.log_file} --batch {args.batch} --learning_rate {args.learning_rate} --n_train {args.n_train} --map {args.map}"
    command_victim = f"cd Documents/AiLab/JAVA_project && source .venv/bin/activate && python3 Environments/train.py --agent victim --n_ep {args.episodes} --ep_ibatch {args.ibatch_ep} --ep_fbatch {args.fbatch_ep} --log_file {args.log_file} --batch {args.batch} --learning_rate {args.learning_rate} --n_train {args.n_train} --map {args.map}"

    print("[INFO] Starting training processes in separate terminals...")
    start_process_in_terminal(command_killer)
    start_process_in_terminal(command_victim)