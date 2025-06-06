import numpy as np
from gymnasium import spaces
from ultralytics import YOLO
import json
import fcntl
import time
from gymnasium import Env

from utils import COM_FILES, OBJ_FILES, reset_files

class KillerVictimEnv(Env):
    def __init__(self, config=None):
        self.config = config or {}
        self.agent = self.config["agent"]  # "killer" o "victim"
        print(f"[ENV] KillerVictimEnv initialized with agent: {self.agent}")

        self.info = {
            "status": "visible",
            "items": 0,
            "end-game": False,
            "map": self.config["map"],
            "slow": False,
            "speed": False ,
            "win": False,
            "finished": False,
            "dead": False,
            "sub_map": 0,
            "distance_1": 0,
            "distance_2": 0,
            "battery": False,
            "phone": False
        }

        self.timer_sub_map = 0
        self.timer = 0
        self.timer_map = 0
        self.global_timer = 0

        self.observation_space = spaces.Box(low=0, high=100, shape=(10, 5), dtype=np.float32)
        self.action_space = spaces.Discrete(5) if self.agent == "killer" else spaces.Discrete(6)
        super().__init__()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed, options=options)
        self.info = {
            "status": "visible",
            "items": 0,
            "end-game": False,
            "map": self.config["map"],
            "slow": False,
            "speed": False,
            "win": False,
            "finished": False,
            "dead": False,
            "sub_map": 0,
            "distance_1": 0,
            "distance_2": 0,
            "battery": False,
            "phone": False
        }
        self.timer_sub_map = 0
        self.timer = 0
        self.timer_map = 0
        self.global_timer = 0
        obs = np.zeros((10, 5), dtype=np.float32)
        reset_files(self.agent)
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
        sub_map = self.info["sub_map"]

        if agent == "victim" and self.info["map"] == 0 and self.info["phone"] == False:
            home_1 = self.info["distance_1"]
        if agent == "victim" and self.info["map"] == 0 and self.info["battery"] == False:
            home_2 = self.info["distance_2"]

        if agent == "victim" and self.info["map"] == 1 and self.info["battery"] == False:
            ds_1 = self.info["distance_1"]
        elif agent == "victim" and self.info["map"] == 2 and self.info["phone"] == False:
            ds_2 = self.info["distance_2"]

        # INITIAL REWARD

        # If the victim saw the killer and he is daashing gave a small reward
        if agent == "victim" and (self.timer < 15 or any(obj[4] == 1 for obj in obs)) and action_meaning[action] == "dash":
            rew += 0.1 * (15 - self.timer) if 0.05 * (15 - self.timer) < 0.3 else 0.3
        elif agent == "victim" and self.timer > 40 and any(obj[4] == 3 for obj in obs) and action_meaning[action] == "interact":
            rew -= 0.02

        if agent == "victim" and self.info["map"] == 0 and any(obj[4] == 6 for obj in obs) and action_meaning[action] == "interact" and (home_1 < 55.0 or home_2 < 55.0):
            victim_boxes = [obj for obj in obs if obj[4] == 2]
            interaction_boxes = [obj for obj in obs if obj[4] == 6]

            if victim_boxes and interaction_boxes:
                dist = self.distance(victim_boxes, winObject_boxes)
                if dist > 0.75:
                    rew += 0.3
        elif agent == "victim" and self.info["map"] == 0 and any(obj[4] == 6 for obj in obs) and action_meaning[action] != "interact" and (home_1 < 55.0 or home_2 < 55.0):
            rew -= 0.02


        if agent == "victim" and self.info["map"] != 0 and any(obj[4] == 6 for obj in obs) and action_meaning[action] == "interact":
            victim_boxes = [obj for obj in obs if obj[4] == 2]
            winObject_boxes = [obj for obj in obs if obj[4] == 7]
            hide_boxes = [obj for obj in obs if obj[4] == 3]

            if winObject_boxes and victim_boxes and hide_boxes:
                dist = self.distance(victim_boxes, winObject_boxes)
                if dist < self.distance(victim_boxes, hide_boxes) and dist > 0.75:
                    rew += 0.2
                else:
                    rew -= 0.01
            elif winObject_boxes and victim_boxes:
                if self.distance(victim_boxes, winObject_boxes) > 0.75:
                    print("Win Object Only")
                    rew += 1

        if agent == "victim":
            battery = True if self.info['battery'] else False
            phone = True if self.info['phone'] else False
            prev_map = self.info["map"]

        # If the agent is the killer and sees a victim, give a small reward
        if agent == "killer" and action_meaning[action] == "interact":
            killer_boxes = [obj for obj in obs if obj[4] == 1]
            victim_boxes = [obj for obj in obs if obj[4] == 2]
            interaction_boxes = [obj for obj in obs if obj[4] == 5]

            if killer_boxes and victim_boxes:
                ds = self.distance(killer_boxes, victim_boxes)
                if ds > 0.4:
                    rew += ds

            if killer_boxes and interaction_boxes:
                ds = self.distance(killer_boxes, interaction_boxes)
                if self.info['end-game'] == False and (self.info['sub_map'] == 2 or self.info['sub_map'] == 4) and action_meaning[action] == "interact" and ds > 0.4:
                    rew += 0.2

        # ACTION

        if action != "":
            # Send Action
            self.send_action_to_java({"get-game": False, "agent": agent, "action": action_meaning[action]})

            # Get Game State
            self.get_game_state(agent)

            # Object Detection of new vision of the agent
            obs = self.extract_features(self.object_detection(agent), max_objects=10)

        # REWARD

        if self.info["finished"]:
            rew -= 1.0 * self.global_timer if self.global_timer < 20 else 20
            terminated = True
            print(f"[INFO] {agent} has finished the game!")

        if self.info['win']:
            print("Win")
            rew += 1.0 * self.global_timer if self.global_timer < 20 else 50
            terminated = True
            print(f"[INFO] {agent} has won the game!")

        if agent == "victim" and self.info["dead"] and self.global_timer != 0:
            rew -= 1.0 * self.global_timer if self.global_timer < 20 else 20
            print("[INFO] Victim is dead, ending game.")
            terminated = True

        self.global_timer += 1

        if self.info['slow'] and self.timer > 40:
            rew -= 0.1

        if action == "":
            rew -= 0.1
            if agent == "killer" and self.info["end-game"]:
                rew -= 0.1

        # VICTIM

        if agent == "victim" and battery != self.info["battery"]:
            rew += 1

        if agent == "victim" and phone != self.info["phone"]:
            rew += 1

        if agent == "victim" and prev_map != self.info["map"] and self.info["map"] == 1 and self.info["battery"] == False:
            rew += 1
        elif agent == "victim" and prev_map != self.info["map"] and self.info["map"] == 2 and self.info["phone"] == False:
            rew += 1
        elif agent == "victim" and prev_map != self.info["map"] and self.info["map"] == 0 and self.info["battery"] == False and prev_map == 1:
            rew -= 0.2
        elif agent == "victim" and prev_map != self.info["map"] and self.info["map"] == 0 and self.info["phone"] == False and prev_map == 2:
            rew -= 0.2
 
        if agent == "victim" and self.info["map"] == 0 and self.global_timer > 20 and self.info["end-game"] == False:
            rew -= 0.01 * (self.global_timer - 20) if 0.05 * (self.global_timer - 20) < 0.1 else 0.1

        if agent == "victim" and self.info["map"] == 1 and self.info["battery"] == True:
            rew -= 0.01 * (self.global_timer - 20) if 0.05 * (self.global_timer - 20) < 0.1 else 0.1

        if agent == "victim" and self.info["map"] == 2 and self.info["phone"] == True:
            rew -= 0.01 * (self.global_timer - 20) if 0.05 * (self.global_timer - 20) < 0.1 else 0.1

        if agent == "victim" and self.info["map"] == 0:
            try:
                if self.info["distance_1"] < home_1 and home_1 < 255.0 and self.info["phone"] == False:
                    print("Distance home 1")
                    self.timer_map += 1
                    rew += 0.1 * self.timer_map if 0.1 * self.timer_map < 0.6 else 0.6
                elif self.info["distance_1"] >= home_1 and home_1 < 255.0 and self.info["phone"] == False:
                    self.timer_map = 0
                    rew -= 0.01
                elif self.info["distance_2"] < home_2 and home_2 < 255.0 and self.info["battery"] == False:
                    print("Distance home 2")
                    self.timer_map += 1
                    rew += 0.1 * self.timer_map if 0.1 * self.timer_map < 0.6 else 0.6
                elif self.info["distance_2"] >= home_2 and home_2 < 255.0 and self.info["battery"] == False:
                    self.timer_map = 0
                    rew -= 0.01
            except UnboundLocalError:
                pass

        try:
            if agent == "victim" and self.info["map"] == 1 and self.info['battery'] == False and self.info["distance_1"] < ds_1:
                print("Distance Battery")
                self.timer_map += 1
                rew += 0.1 * self.timer_map if 0.05 * self.timer_map < 0.5 else 0.5
            elif agent == "victim" and self.info["map"] == 1 and self.info['battery'] == False and self.info["distance_1"] >= ds_1:
                rew -= 0.01
                self.timer_map = 0
            elif agent == "victim" and self.info["map"] == 2 and self.info['phone'] == False and self.info["distance_2"] < ds_2:
                print("Distance Phone")
                self.timer_map += 1
                rew += 0.1 * self.timer_map if 0.05 * self.timer_map < 0.5 else 0.5
            elif agent == "victim" and self.info["map"] == 2 and self.info['phone'] == False and self.info["distance_2"] >= ds_2:
                rew -= 0.01
                self.timer_map = 0
        except UnboundLocalError:
            pass

        if agent == "victim" and any(obj[4] == 1 for obj in obs):
            self.timer = 0
            
            victim_boxes = [obj for obj in obs if obj[4] == 2]
            killer_boxes = [obj for obj in obs if obj[4] == 1]

            if victim_boxes and killer_boxes and self.distance(victim_boxes, killer_boxes) > 0.2:
                dst = self.distance(victim_boxes, killer_boxes)
                rew -= dst

        elif agent == "victim":
            self.timer += 1

        if agent == "victim" and self.timer < 10 and self.info["status"] == "hide":
            print("Hide see killer")
            rew += 0.05 * (10 - self.timer) if 0.05 * (10 - self.timer) < 0.2 else 0.2
        elif agent == "victim" and self.timer > 30 and self.info["status"] == "hide":
            rew -= 0.01

        if agent == "victim" and self.timer_sub_map > 20 and self.info["sub_map"] in [1, 2, 3, 4]:
            rew -= 0.02 * self.timer_sub_map if 0.02 * self.timer_sub_map < 0.1 else 0.1
            self.timer_sub_map += 1
        elif agent == "victim":
            self.timer_sub_map = 0


        # KILLER

        if agent == "killer":
            killer_boxes = [obj for obj in obs if obj[4] == 1]
            victim_boxes = [obj for obj in obs if obj[4] == 2]

            if victim_boxes and killer_boxes:
                ds = self.distance(victim_boxes, killer_boxes)

                if ds > 0.4:
                    rew += ds
                self.timer = 0
            else:
                self.timer += 1
            
            if self.timer > 15 and self.timer < 40:
                rew -= 0.01 * self.timer if 0.01 * self.timer < 0.2 else 0.2
                self.timer += 1

            if self.info['end-game'] == False and (self.info['sub_map'] == 2 or self.info['sub_map'] == 4):
                rew += 0.01
                killer_boxes = [obj for obj in obs if obj[4] == 1]
                interaction_boxes = [obj for obj in obs if obj[4] == 5]

                if killer_boxes and interaction_boxes:
                    ds = self.distance(killer_boxes, interaction_boxes)
                    rew += 0.05
    
        if agent == "killer" and sub_map == self.info["sub_map"]:
            self.timer_map += 1
            rew -= 0.05 * self.timer_map if 0.05 * self.timer_map < 0.2 else 0.2
        elif agent == "killer" and self.info['end-game'] == False and sub_map != self.info["sub_map"]:
            self.timer_map = 0
            rew += 0.3

        # If the agent is the killer and interacts with a object, give a small reward
        if agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact") and (any(obj[4] == 5 for obj in obs) or any(obj[4] == 3 for obj in obs)) and self.timer < 40 and self.info['end-game'] == False:
            rew += 0.2
        elif agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact") and (any(obj[4] == 5 for obj in obs) or any(obj[4] == 3 for obj in obs)) and self.info['end-game'] == True:
            rew += 0.2
        elif agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact"):
            rew -= 0.02
        
        print(rew)

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
                "distance_1": game_state[agent]["distance_1"],
                "distance_2": game_state[agent]["distance_2"],
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
        elif agent == "victim":
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
            except Exception as e:
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
                - class_id: Class ID (1 for "Jason", 2 for "Victim", 3 for "Hide", 4 for "Slow", 5 for "Interaction", 6 for "Obstacle", 7 for "Win")
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
                class_id = 1
            elif class_name == "Victim":
                class_id = 2
            elif class_name == "Hide":
                class_id = 3
            elif class_name == "Slow":
                class_id = 4
            elif class_name == "Interaction":
                class_id = 5
            elif class_name == "Obstacle":
                class_id = 6
            elif class_name == "Win":
                class_id = 7
            obs[i] = [x1, y1, x2, y2, class_id]

        return np.array(obs, dtype=np.float32)
    
    def close(self, *args, **kwargs):
        """
        Close the environment and release resources.
        """
        print("[INFO] Environment closed " + self.config["agent"])
        pass
