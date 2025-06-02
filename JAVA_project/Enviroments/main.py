import subprocess
import os

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

def reset_files():
    """
    Resets the debug files for both agents.
    """

    all_files = ["Comunications_files/ack_killer.json", "Comunications_files/ack_victim.json", "Comunications_files/game_state_killer.json", "Comunications_files/game_state_victim.json", "Comunications_files/action_killer.json", "Comunications_files/action_victim.json", "Object_detection/detections_jason.json", "Object_detection/Detections_panam.json"]
    for c_file in all_files:
        try:
            with open(c_file, "r+") as f:
                f.seek(0)
                f.truncate()
        except FileNotFoundError:
            print(f"[WARNING] File {c_file} not found. Skipping reset.")

    print("[INFO] Debug files reset.")

if __name__ == "__main__":

    reset_files()  # Reset the files for both agents
    start_game_server()  # Start the Java game server

    # Comandi per avviare i processi
    command_killer = "cd Desktop/Studio/Uni/AiLab/JAVA_project && source .venv/bin/activate && python3 Enviroments/new_train.py killer"
    command_victim = "cd Desktop/Studio/Uni/AiLab/JAVA_project && source .venv/bin/activate && python3 Enviroments/new_train.py victim"

    print("[INFO] Starting training processes in separate terminals...")
    start_process_in_terminal(command_killer)
    start_process_in_terminal(command_victim)