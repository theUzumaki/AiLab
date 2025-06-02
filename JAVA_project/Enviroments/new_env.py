import numpy as np
from gymnasium import spaces
from ultralytics import YOLO
import json
import fcntl
import time
import os
from gymnasium import Env
import sys
import contextlib

COM_FILES = "/Users/lachithaperera/Documents/AiLab/JAVA_project/Comunications_files/"
OBJ_FILES = "/Users/lachithaperera/Documents/AiLab/JAVA_project/Object_detection/"

class KillerVictimEnv(Env):
    def __init__(self, config=None):
        self.config = config or {}
        self.agent = self.config["agent"]  # "killer" o "victim"
        print(f"[ENV] KillerVictimEnv initialized with agent: {self.agent}")

        self.info = {
            "status": "visible",
            "items": 0,
            "end-game": False,
            "map": 0,
            "global_timer": 0,
            "slow": False,
            "speed": False ,
            "win": False,
            "timer": 0,
            "finished": False,
            "dead": False,
            "sub_map": 0,
            "timer_map": 0,
        }

        self.observation_space = spaces.Box(low=0, high=100, shape=(10, 5), dtype=np.float32)
        self.action_space = spaces.Discrete(5) if self.agent == "killer" else spaces.Discrete(6)
        super().__init__()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed, options=options)
        self.info = {
            "status": "visible",
            "items": 0,
            "end-game": False,
            "map": 0,
            "global_timer": 0,
            "slow": False,
            "speed": False,
            "win": False,
            "timer": 0,
            "finished": False,
            "dead": False,
            "sub_map": 0,
            "timer_map": 0,
        }
        obs = np.zeros((10, 5), dtype=np.float32)
        print("[ENV] Reset chiamato")
        return obs, self.info

    def step(self, action):
        obs = {}
        rew = 0.0
        terminated = False
        truncated = False
        info = {}

        obs, rew, terminated = self.move(self.agent, action, obs, rew, terminated)
        truncated = False

        if terminated:
            print(f"[DEBUG] Episodio terminato")

        return obs, rew, terminated, truncated, self.info

    def distance(self, obj_1, obj_2):
        # Assume the first victim and first killer detected
        obj1_x1, obj1_y1, obj1_x2, obj1_y2, _ = obj_1[0]
        obj2_x1, obj2_y1, obj2_x2, obj2_y2, _ = obj_2[0]
        # Calculate center points
        obj1_cx, obj1_cy = (obj1_x1 + obj1_x2) / 2, (obj1_y1 + obj1_y2) / 2
        obj2_cx, obj2_cy = (obj2_x1 + obj2_x2) / 2, (obj2_y1 + obj2_y2) / 2
        # Calculate Euclidean distance
        distance = np.sqrt((obj1_cx - obj2_cx) ** 2 + (obj1_cy - obj2_cy) ** 2)

        # Normalize distance to [0, 1] assuming image size is 0-100
        max_distance = np.sqrt((100) ** 2 + (100) ** 2)
        distance = 1 - (distance / max_distance)

        print(str(distance) + " class id: " + str(obj_2[0][4]))
        return distance

    def move(self, agent, action, obs, rew, terminated):
        action_meaning = ["up", "down", "right", "left", "interact", "dash"]

        self.info["global_timer"] += 1
        sub_map = self.info["sub_map"]

        # INITIAL REWARD

        # If the victim is near to a house or to a winObject and he is pressing the interact button gave him a reward
        if agent == "victim" and ((self.info["sub_map"] in [1, 4] and self.info["phone"] == False) or (self.info["sub_map"] in [2, 3] and self.info["battery"] == False)) and action_meaning[action] == "interact":
            victim_boxes = [obj for obj in obs if obj[4] == 1]
            winObj_boxes = [obj for obj in obs if obj[4] == 6]
            interaction_boxes = [obj for obj in obs if obj[4] == 4]

            if victim_boxes and winObj_boxes:
                ds = self.distance(victim_boxes, winObj_boxes)
                if ds > 0.65:
                    rew += 0.05

            if victim_boxes and interaction_boxes:
                ds = self.distance(victim_boxes, winObj_boxes)
                if ds > 0.65:
                    rew += 0.1

        if agent == "victim" and self.info['timer'] < 15 and action_meaning[action]:
            rew += 0.2

        # If the agent is the killer and sees a victim, give a small reward
        if agent == "killer" and action_meaning[action] == "interact":
            killer_boxes = [obj for obj in obs if obj[4] == 0]
            victim_boxes = [obj for obj in obs if obj[4] == 1]
            interaction_boxes = [obj for obj in obs if obj[4] == 4]

            if killer_boxes and victim_boxes:
                ds = self.distance(killer_boxes, victim_boxes)
                if ds > 0.4:
                    rew += ds

            if killer_boxes and interaction_boxes:
                ds = self.distance(killer_boxes, interaction_boxes)
                if self.info['end-game'] == False and (self.info['sub_map'] == 2 or self.info['sub_map'] == 4) and action_meaning[action] == "interact" and ds > 0.4:
                    rew += 0.2

        # ACTION

        # Send Action
        self.send_action_to_java({"get-game": False, "agent": agent, "action": action_meaning[action]})

        # Get Game State
        self.get_game_state(agent)

        # Object Detection of new vision of the agent
        obs = self.extract_features(self.object_detection(agent), max_objects=10)


        # REWARD

        if self.info["finished"]:
            terminated = True
            print(f"[INFO] {agent} has finished the game!")
        if self.info['win']:
            rew += 1.0
            terminated = True
            print(f"[INFO] {agent} has won the game!")
        if agent == "victim" and self.info["dead"] and self.info["global_timer"] != 0:
            rew -= 1.0
            print("[INFO] Victim is dead, ending game.")
            terminated = True

        if self.info['slow']:
            rew -= 0.05

        if action == "":
            rew -= 0.1
            if agent == "killer" and self.info["end-game"]:
                rew -= 0.1

        # VICTIM

        if agent == "victim" and self.info['global_timer'] > 200 and self.info['end-game'] == False and self.info['sub_map'] in [0, 5, 6, 7, 8]:
            rew -= 0.05 * (self.info['global_timer']  - 200) if 0.05 * (self.info['global_timer'] - 200) < 0.2 else 0.2

        # If the victim is near the house where is the battery game him a small reward
        elif agent == "victim" and self.info['end-game'] == False and self.info['sub_map'] == 2 and self.info['battery'] == False:
            victim_boxes = [obj for obj in obs if obj[4] == 1]
            interaction_boxes = [obj for obj in obs if obj[4] == 4]

            if victim_boxes and interaction_boxes:
                ds = self.distance(victim_boxes, interaction_boxes)
                if ds > 0.65:
                    rew += ds
            else:
                rew += 0.1

        # If the victim is near the battery gave him a reward
        elif agent == "victim" and self.info["end-game"] == False and self.info['sub_map'] == 3 and self.info['battery'] == False:
            victim_boxes = [obj for obj in obs if obj[4] == 1]
            battery_boxes = [obj for obj in obs if obj[4] == 6]

            if victim_boxes and battery_boxes:
                ds = self.distance(victim_boxes, battery_boxes)
                if ds > 0.65:
                    rew += ds
            else:
                rew += 0.1

        # If the victim is near the house where is the phone gave him a small reward
        elif agent == "victim" and self.info['end-game'] == False and self.info['sub_map'] == 1 and self.info['phone'] == False:
            victim_boxes = [obj for obj in obs if obj[4] == 1]
            interaction_boxes = [obj for obj in obs if obj[4] == 4]

            if victim_boxes and interaction_boxes:
                ds = self.distance(victim_boxes, interaction_boxes)
                if ds > 0.65:
                    rew += ds
            else:
                rew += 0.1

        # If the victim is near the phone gave him a reward
        elif agent == "victim" and self.info["end-game"] == False and self.info['sub_map'] == 4 and self.info['phone'] == False:
            victim_boxes = [obj for obj in obs if obj[4] == 1]
            phone_boxes = [obj for obj in obs if obj[4] == 6]

            if victim_boxes and phone_boxes:
                ds = self.distance(victim_boxes, phone_boxes)
                if ds > 0.65:
                    rew += ds
            else:
                rew += 0.1

        # Check if the victim (class_id == 1) sees the killer (class_id == 0) in obs and calculate the distance
        if agent == "victim":
            victim_boxes = [obj for obj in obs if obj[4] == 1]
            killer_boxes = [obj for obj in obs if obj[4] == 0]

            if victim_boxes and killer_boxes:
                ds = self.distance(victim_boxes, killer_boxes)

                # You can use 'distance' for reward shaping or logging
                rew -= min(ds, 0.5)
                self.info['timer'] = 0
            else:
                self.info['timer'] += 1

        # If the agent is the victim and is sprinting, give a small reward
        if agent == "victim" and self.info['timer'] < 15 and self.info['speed'] and action_meaning[action] == "dash":
            rew += 0.2

        # If the agent is the victim and is in the end-game, give a small reward based on the timer
        if agent == "victim" and self.info['end-game'] == True:
            rew += 0.01 * self.info['timer'] if  0.01 * self.info['timer'] < 0.2 else 0.2
            rew += 0.01

        # If the agent is the victim and is in a house, give a small reward
        if agent == "victim" and (self.info["battery"] or self.info["phone"]):
            rew += 0.3

        if agent == "victim" and self.info['timer'] <= 15 and any(obj[4] == 2 for obj in obs):
            rew += 0.1
        elif agent == "victim" and self.info['timer'] <= 15 and self.info['status'] == "hide":
            rew += 0.2
        elif agent == "victim" and self.info['status'] == "hide" and self.info['end-game'] == False:
            rew -= 0.01 * self.info["timer"] if 0.01 * self.info["timer"] < 0.2 else 0.2

        if agent == "victim" and sub_map == self.info["sub_map"]:
            self.info["timer_map"] += 1
            rew -= 0.05 * self.info["timer_map"] if 0.05 * self.info["timer_map"] < 0.2 else 0.2
        else:
            self.info["timer_map"] = 0
            rew += 0.2

        # KILLER

        if agent == "killer":
            killer_boxes = [obj for obj in obs if obj[4] == 0]
            victim_boxes = [obj for obj in obs if obj[4] == 1]

            if victim_boxes and killer_boxes:
                ds = self.distance(victim_boxes, killer_boxes)

                # You can use 'distance' for reward shaping or logging
                rew += min(ds, 0.4)
                self.info['timer'] = 0
            else:
                self.info['timer'] += 1
            
            if self.info['timer'] > 15:
                rew -= 0.01 * self.info['timer'] if 0.01 * self.info['timer'] < 0.2 else 0.2
                self.info['timer'] += 1

            if self.info['end-game'] == False and (self.info['sub_map'] == 2 or self.info['sub_map'] == 4):
                rew += 0.01
                killer_boxes = [obj for obj in obs if obj[4] == 0]
                interaction_boxes = [obj for obj in obs if obj[4] == 4]

                if killer_boxes and interaction_boxes:
                    ds = self.distance(killer_boxes, interaction_boxes)
                    rew += 0.05
                
    
        if agent == "killer" and sub_map == self.info["sub_map"]:
            self.info["timer_map"] += 1
            rew -= 0.05 * self.info["timer_map"] if 0.05 * self.info["timer_map"] < 0.2 else 0.2
        elif agent == "killer" and self.info['end-game'] == False:
            self.info["timer_map"] = 0
            rew += 0.1

        # If the agent is the killer and interacts with a object, give a small reward
        if agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact") and (any(obj[4] == 4 for obj in obs) or any(obj[4] == 2 for obj in obs)) and self.info['timer'] < 40 and self.info['end-game'] == False:
            rew += 0.05
        elif agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact") and (any(obj[4] == 4 for obj in obs) or any(obj[4] == 2 for obj in obs)) and self.info['end-game'] == True:
            rew += 0.1
        elif agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact"):
            rew -= 0.2

        return obs, rew, terminated
    
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
                    with open(COM_FILES + "game_state_" + self.config["agent"] + ".json", "r+") as f:
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
            with open(COM_FILES + "action_" + self.config["agent"] + ".json", "w") as f:
                # Lock the file to prevent concurrent writes
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(action, f)
                fcntl.flock(f, fcntl.LOCK_UN)

            # print(f"[SENT ACTION] {self.config['agent']} sent action: {action}")

            _ = self.wait_for_ack(COM_FILES + "ack_" + self.config["agent"] + ".json")
            
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

        timer = self.info["timer"]
        global_timer = self.info["global_timer"]
        timer_map = self.info["timer_map"]

        # print(f"[DEBUG] {agent} received game state: {response}")
        
        # Update agent states based on the game state
        if agent == "victim":
            self.info = {
                "status": game_state[agent]["status"],  # Status of the agent (hide, visible, interact)
                "phone": game_state[agent]["phone"],
                "battery": game_state[agent]["battery"],
                "map": game_state[agent]["map"],
                "slow": game_state[agent]["slow"],
                "speed": game_state[agent]["speed"],
                "win": game_state[agent]["win"],
                "end-game": game_state[agent]["end-game"],
                "finished": game_state[agent]["finished"],
                "dead": game_state[agent]["dead"],
                "sub_map": game_state[agent]["sub_map"],
                "timer_map": timer_map,
                "timer": timer,
                "global_timer": global_timer
            }
        else:
            self.info = {
                "status": game_state[agent]["status"],  # Status of the agent (hide, visible, interact)
                "map": game_state[agent]["map"],
                "slow": game_state[agent]["slow"],
                "win": game_state[agent]["win"],
                "end-game": game_state[agent]["end-game"],
                "finished": game_state[agent]["finished"],
                "sub_map": game_state[agent]["sub_map"],
                "timer_map": timer_map,
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
        model_path = OBJ_FILES + "best.pt"
        model = YOLO(model_path)

        if agent == "killer":
            output_path = OBJ_FILES + "detections_jason.json"
            image_path = OBJ_FILES + "jason_view.png"
        else:
            output_path = OBJ_FILES + "detections_panam.json"
            image_path = OBJ_FILES + "victim_view.png"

        while True:
            try:
                with open(image_path, "r") as f:
                    try:
                        fcntl.flock(f, fcntl.LOCK_SH)  # shared lock, waits for exclusive release by Java
                        results = model(image_path)
                        break  # Exit loop if successful
                    finally:
                        fcntl.flock(f, fcntl.LOCK_UN)
            except (FileNotFoundError, PermissionError, OSError):
                time.sleep(0.2)

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
            fcntl.flock(f, fcntl.LOCK_EX)  # Lock the file for writing
            json.dump(output, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)

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
