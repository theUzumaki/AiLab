import subprocess

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

    start_game_server()  # Start the Java game server

    # Comandi per avviare i processi
    command_killer = "cd Documents/AiLab/JAVA_project && source Object_detection/.venv/bin/activate && python3 Enviroments/train.py killer"
    command_victim = "cd Documents/AiLab/JAVA_project && source Object_detection/.venv/bin/activate && python3 Enviroments/train.py victim"

    print("[INFO] Starting training processes in separate terminals...")
    start_process_in_terminal(command_killer)
    start_process_in_terminal(command_victim)