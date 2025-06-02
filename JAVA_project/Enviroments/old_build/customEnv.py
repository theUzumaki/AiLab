
# Library used for creating a multi-agent environment in RLlib
import numpy as np
from ray.rllib.env.multi_agent_env import MultiAgentEnv, EnvContext
from gymnasium import spaces

# Library used for object detection and sending actions to the Java game server
from ultralytics import YOLO
import json
import socket
import time
import os
import fcntl

ABSOLUTE_PATH = "/Users/lachithaperera/Documents/AiLab/JAVA_project/"

class KillerVictimEnv(BaseEnv):
    def __init__(self, config: EnvContext = None):
        self.config = config or {}
        self.agents = ["killer", "victim"]  # Initialize agents based on the configuration
        self._agent_ids = set(self.agents)

        # confi print
        print(f"[ENV] KillerVictimEnv initialized with agents: {config}")

        # The info dictionary will be used to store the state of each agent
        self.info = {
            config["agent"]:
                {
                    "status": "visible",  # Status of the agent
                    "items": 0,  # Number of items the agent has (victim)
                    "end-game": False,  # Current stage of the agent (False: initial, True: end-game)
                    "map": 0, # Current map of the agent (0: Mappa fuori, 1: Casa sinistra, 2: Casa destra)
                    "global_timer": 0,  # Time starting in the end - game
                    "slow": False,  # Whether the agent is slow in water/grass 
                    "speed": False,  # Whether the agent is sprinting (victim)
                    "win": False,  # Whether the agent has won
                    "timer": 0,  # Timer for the agent
                    "finished": False,  # Whether the agent has finished the game
                },
        }

        self.observations = {i: None for i in self.agents}

        self._spaces_in_preferred_format = True
        self.observation_spaces = {
            config["agent"] : spaces.Box(low=-0, high=100, shape=(10, 5), dtype=np.float32),
        }

        self.action_spaces = { config["agent"]: spaces.Discrete(5) if config["agent"] == "killer" else spaces.Discrete(6) }

        super().__init__()

    def reset(self, *, seed=None, options=None):
        """
        Reset the environment and return initial observations for all agents.
        Args:
            seed (int, optional): Seed for random number generation.
            options (dict, optional): Additional options for reset.
        Returns:
            dict: Initial observations for all agents.
        """
        super().reset(seed=seed, options=options)  # Call the parent reset method
        self.info = {
            self.config["agent"]: {
                "status": "visible",  # Status of the agent (hide, visible, interact)
                "items": 0,  # Number of items the agent has (victim)
                "end-game": False,  # Current stage of the agent (False: initial, True: end-game)
                "map": 0,  # Current map of the agent (0: Mappa fuori, 1: Casa sinistra, 2: Casa destra)
                "global_timer": 0,  # Time starting in the end - game
                "slow": False,  # Whether the agent is slow in water/grass 
                "speed": False,  # Whether the agent is sprinting (victim)
                "win": False,  # Whether the agent has won
                "timer": 0,  # Timer for the agent
                "finished": False,  # Whether the agent has finished the game
            },
        }
        obs = {agent: np.zeros((10, 5), dtype=np.float32) for agent in self.agents}

        print("[ENV] Reset chiamato")
        
        return obs, self.info
    
    def step(self, action_dict):
        """
        Perform a step in the environment based on the actions of the agents.
        Args:
            action_dict (dict): A dictionary where keys are agent IDs and values are actions.
        Returns:
            obs (dict): Observations for each agent.
            rew (dict): Rewards for each agent.
            done (dict): Done flags for each agent.
            info (dict): Additional information for each agent.
        """

        def is_all_done(done: spaces.Dict, agent) -> bool:
            """
            Check if the selected agent are done.
            Args:
                done (dict): A dictionary where keys are agent IDs and values are done flags.
            Returns:
                bool: True if the agents are done, False otherwise.
            """
            return True if done[agent] else False
        # Initialize dictionaries for observations, rewards, done flags, and info
        obs, rew, terminateds, info = {}, {}, {}, {}
        
        terminateds = {agent: False for agent in self.agents}  # Initialize termination flags for each agent
        rew = {agent: 0.0 for agent in self.agents}  # Initialize rewards for each agent

        # print("[INFO] Action dictionary received:", action_dict)

        agent = self.config["agent"]  # Get the agent ID
        # Check if the action dictionary is valid and contains the agent's action
        if action_dict == {}:
            action = ""
        else:
            action = action_dict.get(agent, "")

        # ******************************************************************************
        # Perform the action
        # ******************************************************************************

        obs, rew, terminateds = self.move(agent, action, obs, rew, terminateds)

        # ******************************************************************************
        # Part 5: FINALIZE
        # ******************************************************************************

        terminateds['__all__'] = is_all_done(terminateds, agent)  # say if episode is over

        truncateds = {i: False for i in self.agents}  # No truncation logic implemented
        truncateds['__all__'] = False

        # Info
        # print(f"[INFO] {agent} info: {self.info[agent]}")

        if terminateds["__all__"]:
            print(f"[DEBUG] Episodio terminato")

        return obs, rew, terminateds, truncateds, info

    def move(self, agent, action, obs, rew, terminateds):

        # Action meanings for the Java game
        action_meaning = ["up", "down", "right", "left", "interact", "dash"]
        # ******************************************************************************
        # Part 1: SEND ACTION TO JAVA
        # ******************************************************************************

        # print(f"[ACTION] {agent} is performing action: {action}")

        """if agent == "killer" and self.info[agent]["status"] != "interact":
            self.send_action_to_java({"get-game": False, "agent": agent, "action": action_meaning[action]})
        elif agent == "victim" and self.info[agent]["status"] == "hide" and action_meaning[action] == "interact":
            self.send_action_to_java({"get-game": False, "agent": agent, "action": action_meaning[action]})
        elif agent == "victim" and self.info[agent]["speed"] == True and action_meaning[action] != "dash":
            self.send_action_to_java({"get-game": False, "agent": agent, "action": action_meaning[action]})
        elif agent == "victim" and self.info[agent]["status"] != "hide":
            self.send_action_to_java({"get-game": False, "agent": agent, "action": action_meaning[action]})"""

        self.send_action_to_java({"get-game": False, "agent": agent, "action": action_meaning[action]})

        # ******************************************************************************
        # Part 2: GET GAME STATE
        # ******************************************************************************
        self.get_game_state(agent)

        # ******************************************************************************
        # Part 3: OBSERVATION
        # ******************************************************************************
        obs[agent] = self.extract_features(
            self.object_detection(agent), max_objects=10
        )  # Perform object detection and extract features

        # ******************************************************************************
        # Part 4: REWARD
        # ******************************************************************************

        if self.info[agent]["finished"] == True:
            terminateds[agent] = True
            print(f"[INFO] {agent} has finished the game!")
        
        # Check if the agent has won
        if self.info[agent]['win']:
            rew[agent] += 1.0
            terminateds[agent] = True
            print(f"[INFO] {agent} has won the game!")
        
        # If the agent is the victim and is dead, give a large negative reward
        if agent == "victim" and self.info[agent]['dead']:
            rew[agent] -= 1.0
            print("[INFO] Victim is dead, ending game.")
            terminateds[agent] = True

        if terminateds[agent] == True:
            return obs, rew, terminateds

        self.info[agent]["global_timer"] += 1

        if self.info[agent]['slow'] == True:
            rew[agent] -= 0.05

        if action == "":
            rew[agent] -= 0.1  # If no action is taken, give a small negative reward
            if agent == "killer" and self.info[agent]["end-game"] == True:
                rew[agent] -= 0.1

        # VICTIM

        if agent == "victim" and self.info[agent]['global_timer'] > 100 and self.info[agent]['end-game'] == False:
            rew[agent] -= 0.05 * (self.info[agent]['global_timer']  - 100) if 0.05 * (self.info[agent]['global_timer'] - 100) < 0.5 else 0.5

        # If the victim see a killer, reset timer else increase
        if agent == "victim" and any(obj[4] == 0 for obj in obs[agent]):
            self.info['victim']['timer'] = 0
            rew[agent] -= 0.1
        elif agent == "victim" and any(obj[4] == 0 for obj in obs[agent]) == False:
            self.info['victim']['timer'] += 1

        # If the agent is the victim and is sprinting, give a small reward
        if agent == "victim" and self.info[agent]['timer'] < 15 and self.info[agent]['speed']:
            rew[agent] += 0.2

        # If the agent is the victim and is in the end-game, give a small reward based on the timer
        if agent == "victim" and self.info[agent]['end-game'] == True:
            rew[agent] += 0.01 * self.info[agent]['timer'] if  0.01 * self.info[agent]['timer'] < 0.2 else 0.2
            rew[agent] += 0.01

        # If the agent is the victim and is in a house, give a small reward
        if agent == "victim" and self.info[agent]['items'] == 1:
            rew[agent] += 0.2

        if agent == "victim" and any(obj[4] == 6 for obj in obs[agent]) and self.info[agent]['status'] == "interact":
            rew[agent] += 0.2
        elif agent == "victim" and any(obj[4] == 6 for obj in obs[agent]):
            rew[agent] += 0.1

        # If the agent is the victim and see a win object, give a small reward
        if agent == "victim" and any(obj[4] == 6 for obj in obs[agent]) and self.info[agent]['status'] == "interact":
            rew[agent] += 0.5
        elif agent == "victim" and any(obj[4] == 6 for obj in obs[agent]):
            rew[agent] += 0.2

        # If the agent is the victim and is hiding and in the obs the killer is visible give a small reward
        if agent == "victim" and self.info[agent]['timer'] <= 15 and any(obj[4] == 2 for obj in obs[agent]):
            rew[agent] += 0.1
        elif agent == "victim" and self.info[agent]['timer'] <= 15 and self.info[agent]['status'] == "hide":
            rew[agent] += 0.2
        elif agent == "victim" and self.info[agent]['status'] == "hide" and self.info[agent]['end-game'] == False:
            rew[agent] -= 0.05

        # KILLER

        if agent == "killer" and self.info[agent]["timer"] < 15:
            rew[agent] += (0.2 - 0.01 * self.info[agent]["timer"]) if (0.2 - 0.01 * self.info[agent]["timer"]) > 0 else 0

        # If the agent is the killer and sees a victim, give a small reward
        if agent == "killer" and any(obj[4] == 1 for obj in obs[agent]) and self.info[agent]['status'] == "interact":
            rew[agent] += 0.5
        elif agent == "killer" and any(obj[4] == 1 for obj in obs[agent]):
            rew[agent] += 0.4

        # If the agent is the killer and interacts with a object, give a small reward
        if agent == "killer" and self.info[agent]['status'] == "interact" and (any(obj[4] == 4 for obj in obs[agent]) or any(obj[4] == 2 for obj in obs[agent])):
            rew[agent] += 0.05

        if agent == "killer" and self.info[agent]['status'] == "interact":
            rew[agent] -= 0.1

        return obs, rew, terminateds
    
    def wait_for_ack(self, path):
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

    def send_action_to_java(self, action):
        """
        Send the action to the Java game server.
        Args:
            action (dict): The action to send, containing the agent and the action details.
        """
        # Convert the action to JSON and send it to the Java game server
        # print("[INFO] Sending action to Java server:", action)

        # print(f"[INFO] {self.config['agent']} is performing action: {action}")

        response = None  # Initialize response variable

        if action["get-game"]:
            while not response:
                try:
                    with open(ABSOLUTE_PATH + "game_state_" + self.config["agent"] + ".json", "r+") as f:
                        # Lock the file to prevent concurrent reads
                        fcntl.flock(f, fcntl.LOCK_SH)
                        response = json.load(f)

                        f.seek(0)
                        f.truncate()
                        
                        # Unlock the file after reading
                        fcntl.flock(f, fcntl.LOCK_UN)
                        break
                except Exception as e:
                    print("[DEBUG] Game state file not ready, waiting... ")
                    continue  # If the file is not ready, continue waiting
            # print(f"[GAME STATE] {self.config['agent']} received game state: {response}")
        else:
            with open(ABSOLUTE_PATH + "action_" + self.config["agent"] + ".json", "w") as f:
                # Lock the file to prevent concurrent writes
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(action, f)
                fcntl.flock(f, fcntl.LOCK_UN)

            # print(f"[SENT ACTION] {self.config['agent']} sent action: {action}")

            _ = self.wait_for_ack(ABSOLUTE_PATH + "ack_" + self.config["agent"] + ".json")
            
            # print(f"[ACK RECEIVED] {self.config['agent']} received ack from Java server")

        return response # Return the response from the Java server


    
    # Function to get the current game state from the Java server
    def get_game_state(self, agent):
        """
        Get the current game state from the Java game server for a specific agent.
        Args:
            agent (str): The agent for which to get the game state ("killer" or "victim").
        """
        # Send a request to the Java game server to get the current game state
        game_state = self.send_action_to_java({"get-game": True, "agent": agent, "action": "get-game"})

        timer = self.info[agent]["timer"]
        global_timer = self.info[agent]["global_timer"]

        # print(f"[DEBUG] {agent} received game state: {response}")
        
        # Update agent states based on the game state
        if agent == "victim":
            self.info[agent] = {
                "status": game_state[agent]["status"],  # Status of the agent (hide, visible, interact)
                "items": game_state[agent]["items"],
                "map": game_state[agent]["map"],
                "slow": game_state[agent]["slow"],
                "speed": game_state[agent]["speed"],
                "win": game_state[agent]["win"],
                "end-game": game_state[agent]["end-game"],
                "finished": game_state[agent]["finished"],
                "dead": game_state[agent]["dead"],
                "timer": timer,
                "global_timer": global_timer
            }
        else:
            self.info[agent] = {
                "status": game_state[agent]["status"],  # Status of the agent (hide, visible, interact)
                "map": game_state[agent]["map"],
                "slow": game_state[agent]["slow"],
                "win": game_state[agent]["win"],
                "end-game": game_state[agent]["end-game"],
                "finished": game_state[agent]["finished"],
                "timer": timer,
                "global_timer": global_timer
            }

    # Function to perform object detection using a pre-trained YOLO model
    def object_detection(self, agent):
        """
        Perform object detection using a pre-trained YOLO model and save the results in JSON format.
        Args:
            agent (str): The agent for which to perform object detection ("killer" or "victim").
        Returns:
            list: A list of detected objects with their class, bounding box, and confidence.
        """

        # Suppress prints from the YOLO model

        model_path = ABSOLUTE_PATH + "Object_detection/best.pt"
        model = YOLO(model_path)

        if agent == "killer":
            output_path = ABSOLUTE_PATH + "detections_jason.json"
            image_path = ABSOLUTE_PATH + "jason_view.png"
        else:
            output_path = ABSOLUTE_PATH + "detections_panam.json"
            image_path = ABSOLUTE_PATH + "victim_view.png"

        with open(image_path, "r") as f:
            try:
                # Prova ad acquisire un lock condiviso (lettura) BLOCCANTE
                fcntl.flock(f, fcntl.LOCK_SH)  # shared lock → attende il rilascio dell'esclusivo Java
                results = model(image_path)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)  # Rilascia il lock

        output = []
        for r in results:
            for box in r.boxes:
                cls = r.names[int(box.cls)]
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                output.append(
                    {
                        "class": cls,  # "killer" o "victim"
                        "bbox": [x1, y1, x2, y2],
                        "confidence": float(box.conf[0]),
                    }
                )

        # Salva in formato JSON
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

        return output

    # Function to extract features from the detections
    def extract_features(self, detections, max_objects=10):
        """
        Extract features from the detections and return them in a structured format.
        Args:
            detections (list): List of detected objects with their class, bounding box, and confidence.
            max_objects (int): Maximum number of objects to consider.
        Returns:
            np.ndarray: An array of shape (max_objects, 5) containing the features:
                - x1: Top-left x-coordinate of the bounding box
                - y1: Top-left y-coordinate of the bounding box
                - x2: Bottom-right x-coordinate of the bounding box
                - y2: Bottom-right y-coordinate of the bounding box
                - class_id: Class ID (0 for "Jason", 1 for "Victim", 2 for "Hide", 3 for "Slow", 4 for "Interaction", 5 for "Obstacle", 6 for "Win")
        """
        # Filter detections based on confidence
        detections = sorted(detections, key=lambda d: d["confidence"], reverse=True)[
            :max_objects
        ]

        obs = np.zeros((max_objects, 5))  # x1, y1, x2, y2, class_id
        for i, d in enumerate(detections):
            x1, y1, x2, y2 = d["bbox"]
            class_name = d["class"]
            # Map class names to numerical IDs
            if class_name == "Jason":
                class_id = 0
            elif class_name == "Victim":
                class_id = 1
            elif class_name == "Hide":
                class_id = 2
            elif class_name == "Slow":
                class_id = 3
            elif class_name == "Interaction":
                class_id = 4
            elif class_name == "Obstacle":
                class_id = 5
            elif class_name == "Win":
                class_id = 6
            obs[i] = [x1, y1, x2, y2, class_id]

        return np.array(obs, dtype=np.float32)
    
    def close(self, *args, **kwargs):
        """
        Close the environment and release resources.
        """
        print("[INFO] Environment closed " + self.config["agent"])
        pass