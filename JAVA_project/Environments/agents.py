import numpy as np
from gymnasium import spaces
import json
import fcntl
import time
from gymnasium import Env
import use_obj

from utils import COM_FILES, ABSOLUTE_PATH, reset_files, distance

DEBUG = True


class KillerVictimEnv(Env):
    def __init__(self, config=None, debug=True):
        DEBUG = debug

        # Set the configuration
        self.config = config or {}

        model_path = ABSOLUTE_PATH + "/Object_detection/CNN/checkpoints/best_model.pth"
        dataset_path = ABSOLUTE_PATH + "/Object_detection/CNN/Dataset_3"
        
        self.detector = use_obj.ObjectDetector(model_path, dataset_path)

        # Agent selection
        self.agent = self.config["agent"]  # "killer" o "victim"

        if DEBUG:
            print(f"[ENV] KillerVictimEnv initialized with agent: {self.agent}")

        self.min_dist = 10000

        self.info = {
            "status": "visible",
            "end-game": False,
            "map": self.config["map"],
            "slow": False,
            "speed": False,
            "win": False,
            "finished": False,
            "dead": False,
            "sub_map": 0,
            "distance_1_x": 0,
            "distance_1_y": 0,
            "distance_2_x": 0,
            "distance_2_y": 0,
            "battery": False,
            "phone": False,
            "killer_visible": False,
            "victim_visible": False,
            "killer_distance": False,
            "num_obstacle": 0,
            "num_win": 0,
            "num_hide": 0,
            "num_interaction": 0,
            "num_slow": 0,
            "agent_x": 0,
            "agent_y": 0,
        }

        self.timer_sub_map = 0
        self.timer = 0
        self.timer_map = 0
        self.global_timer = 0
        self.prev_rew = 0
        self.step_back = 0
        self.step_forward = 0
        self.focus = self.config["focus"]
        self.pre_submap = 0

        self.observation_space = spaces.Box(
            low=0, high=100, shape=(10, 5), dtype=np.float32
        )
        self.action_space = (
            spaces.Discrete(5) if self.agent == "killer" else spaces.Discrete(6)
        )
        super().__init__()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed, options=options)

        self.info = {
            "status": "visible",
            "end-game": False,
            "map": self.config["map"],
            "slow": False,
            "speed": False,
            "win": False,
            "finished": False,
            "dead": False,
            "sub_map": 0,
            "distance_1_x": 0,
            "distance_1_y": 0,
            "distance_2_x": 0,
            "distance_2_y": 0,
            "battery": False,
            "phone": False,
            "killer_visible": False,
            "victim_visible": False,
            "killer_distance": False,
            "num_obstacle": 0,
            "num_win": 0,
            "num_hide": 0,
            "num_interaction": 0,
            "num_slow": 0,
            "agent_x": 0,
            "agent_y": 0,
        }

        self.timer_sub_map = 0
        self.timer = 0
        self.timer_map = 0
        self.global_timer = 0
        self.step_back = 0
        self.step_forward = 0
        self.pre_submap = 0

        obs = np.zeros((10, 5), dtype=np.float32)

        reset_files(self.agent)

        if DEBUG:
            print("[ENV] Reset chiamato")
        return obs, self.info

    def step(self, action):
        obs = {}
        rew = 0.0
        terminated = False
        truncated = False

        obs, rew, terminated = self.move(self.agent, action, obs, rew, terminated)
        truncated = False

        # Se obs non è un array (cioè non è stato aggiornato da move), restituisci un array vuoto
        if not isinstance(obs, np.ndarray):
            obs = np.zeros((10, 5), dtype=np.float32)

        if terminated and DEBUG:
            print(f"[DEBUG] Episodio terminato")

        return obs, rew, terminated, truncated, self.info
    
    def victim_reward_jason(self, obs, action, info):
        pass

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

        if DEBUG:
            print(str(distance) + " class id: " + str(obj_2[0][4]))

        return distance

    def move(self, agent, action, obs, rew, terminated):
        action_meaning = ["up", "down", "right", "left", "interact", "dash"]
        sub_map = self.info["sub_map"]

        # Save distance from houses

        if self.focus != "jason":
            if (
                agent == "victim"
                and self.info["map"] == 0
                and self.info["phone"] == False
                and self.info["status"] != "hide"
            ):
                home_1 = distance(
                    self.info["agent_x"],
                    self.info["agent_y"],
                    self.info["distance_1_x"],
                    self.info["distance_1_y"],
                )

            if (
                agent == "victim"
                and self.info["map"] == 0
                and self.info["battery"] == False
                and self.info["status"] != "hide"
            ):
                home_2 = distance(
                    self.info["agent_x"],
                    self.info["agent_y"],
                    self.info["distance_2_x"],
                    self.info["distance_2_y"],
                )

            # Save distance from battery and phone
            if (
                agent == "victim"
                and self.info["map"] == 1
                and self.info["battery"] == False
                and self.info["status"] != "hide"
            ):
                ds_1 = distance(
                    self.info["agent_x"],
                    self.info["agent_y"],
                    self.info["distance_1_x"],
                    self.info["distance_1_y"],
                )
            elif (
                agent == "victim"
                and self.info["map"] == 2
                and self.info["phone"] == False
                and self.info["status"] != "hide"
            ):
                ds_2 = distance(
                    self.info["agent_x"],
                    self.info["agent_y"],
                    self.info["distance_2_x"],
                    self.info["distance_2_y"],
                )

            # Save distance from exit door
            if (
                agent == "victim"
                and self.info["map"] == 1
                and self.info["battery"]
                and self.info["status"] != "hide"
            ):
                exit_1 = distance(
                    self.info["agent_x"],
                    self.info["agent_y"],
                    self.info["distance_1_x"],
                    self.info["distance_1_y"],
                )
            elif (
                agent == "victim"
                and self.info["map"] == 2
                and self.info["phone"]
                and self.info["status"] != "hide"
            ):
                exit_2 = distance(
                    self.info["agent_x"],
                    self.info["agent_y"],
                    self.info["distance_2_x"],
                    self.info["distance_2_y"],
                )
            if (
                agent == "victim"
                and self.info["map"] == 0
                and any(obj[4] == 5 for obj in obs)
                and action_meaning[action] == "interact"
                and (home_2 < 33.0)
            ):
                rew += 0.1
            elif (
                agent == "victim"
                and self.info["map"] == 0
                and any(obj[4] == 5 for obj in obs)
                and action_meaning[action] != "interact"
                and (home_1 < 33.0 or home_2 < 33.0)
            ):
               rew -= 0.01

            if (
                agent == "victim"
                and self.info["map"] != 0
                and any(obj[4] == 7 for obj in obs)
                and action_meaning[action] == "interact"
                and (ds_1 < 33.0)
            ):
                rew += 0.1
            elif (
                agent == "victim"
                and self.info["map"] != 0
                and any(obj[4] == 7 for obj in obs)
                and action_meaning[action] != "interact"
                and (ds_1 < 33.0)
            ):
                rew -= 0.1

        # INITIAL REWARD

        # If the victim saw the killer and he is daashing gave a small reward

        if self.focus == "jason":
            if agent == "victim" and any(obj[4] == 1 for obj in obs) and action_meaning[action] == "dash":
                print("[STEP] Victim saw the killer and is dashing")
                rew += 1


        if agent == "victim":
            battery = True if self.info["battery"] else False
            phone = True if self.info["phone"] else False
            prev_map = self.info["map"]

        # If the agent is the killer and sees a victim, give a small reward
        if agent == "killer" and action_meaning[action] == "interact":
            killer_boxes = [obj for obj in obs if obj[4] == 1]
            victim_boxes = [obj for obj in obs if obj[4] == 2]

            if killer_boxes and victim_boxes:
                ds = self.distance(killer_boxes, victim_boxes)
                if ds > 0.4:
                    rew += ds

        # ACTION

        if action != "":
            # Send Action
            self.send_action_to_java(
                {"get-game": False, "agent": agent, "action": action_meaning[action]}
            )

            # Get Game State
            self.get_game_state(agent)

            # Object Detection of new vision of the agent
            obs = self.extract_features(self.object_detection(agent), max_objects=10)

            if self.agent == "victim" and self.info["killer_visible"]:
                killer_boxes = [obj for obj in obs if obj[4] == 1]
                victim_boxes = [obj for obj in obs if obj[4] == 2]

                if killer_boxes and victim_boxes:
                    self.info["killer_distance"] = self.distance(
                        victim_boxes, killer_boxes
                    )

        # REWARD

        if self.info["finished"]:
            # rew -= 20
            terminated = True

            if DEBUG:
                print(f"[INFO] {agent} has finished the game!")

        if self.info["win"]:
            rew += 1.0 * self.global_timer if 1.0 * self.global_timer else 100
            terminated = True

            if DEBUG:
                print(f"[INFO] {agent} has won the game!")

        if agent == "victim" and self.info["dead"] and self.global_timer != 0:
            rew -= (100 - (self.global_timer)) if self.global_timer < 80 else 20
            terminated = True

            if DEBUG:
                print(
                    f"[INFO] Victim is dead, ending game {(100 - (self.global_timer)) if self.global_timer > 80 else 20}."
                )

        self.global_timer += 1

        if self.agent == "victim" and self.info['slow'] and self.timer > 40 and self.focus != "jason":
            rew -= 0.01

        if self.agent == "killer" and action == "":
            rew -= 0.1
            if agent == "killer" and self.info["end-game"]:
                rew -= 0.1

        # VICTIM

        if agent == "victim" and prev_map != self.info["map"]:
            self.timer_map = 0

        if self.focus != "jason":
            if agent == "victim" and battery != self.info["battery"] and self.focus == "exit_battery":
                print("Battery taked reward pre: " + str(rew))
                rew += 10
                print("Battery taked reward aft: " + str(rew))
                self.timer_map = 0

            if agent == "victim" and phone != self.info["phone"] and self.focus == "exit_phone":
                print("Phone taked reward pre: " + str(rew))
                rew += 10
                print("Phone taked reward aft: " + str(rew))
                self.timer_map = 0

            # If the victim is not hide
            if agent == "victim" and self.info["status"] != "hide":
                if (
                    prev_map != self.info["map"]
                    and self.info["map"] == 1
                    and self.info["battery"] == False
                    and self.focus == "exit_battery"
                ):
                    print("Enter house reward pre: " + str(rew))
                    rew += 10
                    print("Enter house reward aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 0
                    and self.info["battery"]
                    and prev_map == 1
                    and self.focus == "exit_battery"
                ):
                    print("Exit house reward pre: " + str(rew))
                    rew += 10
                    print("Exit house reward aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 0
                    and self.info["battery"] == False
                    and prev_map == 1
                    and self.focus == "exit_battery"
                ):
                    print("Exit house no battery pre: ")
                    rew -= 10
                    print("Exit house no battery aft: ")
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 1
                    and self.info["battery"]
                    and self.focus == "exit_battery"
                ):
                    print("Enter if battery true reward pre: " + str(rew))
                    rew -= 15
                    print("Enter if battery true reward aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 2
                    and self.info["phone"] == False
                    and self.focus == "exit_phone"
                ):
                    print("Enter house reward pre: " + str(rew))
                    rew += 10
                    print("Enter house reward aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 0
                    and self.info["phone"]
                    and prev_map == 2
                    and self.focus == "exit_phone"
                ):
                    print("Exit house reward pre: " + str(rew))
                    rew += 10
                    print("Exit house reward aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 0
                    and self.info["phone"] == False
                    and prev_map == 2
                    and self.focus == "exit_phone"
                ):
                    print("Exit house no phone pre: ")
                    rew -= 10
                    print("Exit house no phone aft: ")
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 1
                    and self.info["phone"]
                    and self.focus == "exit_phone"
                ):
                    print("Enter if phone true reward pre: " + str(rew))
                    rew -= 15
                    print("Enter if phone true reward aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 1
                    and self.info["phone"] == False
                    and self.focus == "exit_phone"
                ):
                    print("Enter in the wrong house pre: " + str(rew))
                    rew -= 1
                    print("Enter in the wrong house aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 1
                    and self.info["phone"] == False
                    and self.focus == "exit_phone"
                ):
                    print("Exit from the wrong house pre: " + str(rew))
                    rew += 1
                    print("Exit from the wrong house aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 2
                    and self.info["battery"] == False
                    and self.focus == "exit_battery"
                ):
                    print("Enter in the wrong house pre: " + str(rew))
                    rew -= 1
                    print("Enter in the wrong house aft: " + str(rew))
                elif (
                    prev_map != self.info["map"]
                    and self.info["map"] == 2
                    and self.info["battery"] == False
                    and self.focus == "exit_battery"
                ):
                    print("Exit from the wrong house pre: " + str(rew))
                    rew += 1
                    print("Exit from the wrong house aft: " + str(rew))
                    

                if self.info["map"] == 0:
                    try:
                        new_dis_1 = distance(
                            self.info["agent_x"],
                            self.info["agent_y"],
                            self.info["distance_1_x"],
                            self.info["distance_1_y"],
                        )
                        new_dis_2 = distance(
                            self.info["agent_x"],
                            self.info["agent_y"],
                            self.info["distance_2_x"],
                            self.info["distance_2_y"],
                        )
                        if (
                            new_dis_1 < home_1
                            and self.info["phone"] == False
                            and self.focus == "exit_phone"
                        ):
                            if DEBUG:
                                print("Distance home 1")

                            self.timer_map += 1

                            print("[STEP] Distance home 1 pre: " + str(rew))
                            rew += 0.05
                            print("[STEP] Distance home 1 aft: " + str(rew))
                        elif (
                            new_dis_1 >= home_1
                            and self.info["phone"] == False
                            and self.focus == "exit_phone"
                        ):
                            if DEBUG:
                                print("Distance home 1 decrease")

                            self.timer_map = 0

                            print("[STEP] Distance home 1 decrease pre: " + str(rew))
                            rew -= 0.05
                            print("[STEP] Distance home 1 decrease aft: " + str(rew))
                        elif (
                            new_dis_2 < home_2
                            and self.info["battery"] == False
                            and self.focus == "exit_battery"
                        ):
                            if DEBUG:
                                print("Distance home 2")

                            self.timer_map += 1
                            rew += 0.05
                        elif (
                            new_dis_2 >= home_2
                            and self.info["battery"] == False
                            and self.focus == "exit_battery"
                        ):
                            self.timer_map = 0
                            if DEBUG:
                                print("Distance home 2 decrease")

                            rew -= 0.05
                    except UnboundLocalError:
                        pass

                try:
                    new_dis_1 = distance(
                        self.info["agent_x"],
                        self.info["agent_y"],
                        self.info["distance_1_x"],
                        self.info["distance_1_y"],
                    )
                    new_dis_2 = distance(
                        self.info["agent_x"],
                        self.info["agent_y"],
                        self.info["distance_2_x"],
                        self.info["distance_2_y"],
                    )
                    if (
                        self.info["map"] == 1
                        and self.info["battery"] == False
                        and new_dis_1 < ds_1
                        and self.focus == "exit_battery"
                    ):
                        if DEBUG:
                            print("Distance Battery")

                        self.timer_map += 1
                        rew += 0.05
                    elif (
                        self.info["map"] == 1
                        and self.info["battery"] == False
                        and new_dis_1 >= ds_1
                        and self.focus == "exit_battery"
                    ):
                        rew -= 0.05
                        self.timer_map = 0
                    elif (
                        self.info["map"] == 2
                        and self.info["phone"] == False
                        and new_dis_2 < ds_2
                        and self.focus == "exit_phone"
                    ):
                        if DEBUG:
                            print("Distance Phone")

                        self.timer_map += 1
                        rew += 0.05
                    elif (
                        self.info["map"] == 2
                        and self.info["phone"] == False
                        and new_dis_2 >= ds_2
                        and self.focus == "exit_phone"
                    ):
                        rew -= 0.05
                        self.timer_map = 0
                except UnboundLocalError:
                    pass

                try:
                    new_dis_1 = distance(
                        self.info["agent_x"],
                        self.info["agent_y"],
                        self.info["distance_1_x"],
                        self.info["distance_1_y"],
                    )
                    new_dis_2 = distance(
                        self.info["agent_x"],
                        self.info["agent_y"],
                        self.info["distance_2_x"],
                        self.info["distance_2_y"],
                    )
                    if (
                        self.info["map"] == 1
                        and (self.info["battery"]
                        and new_dis_1 < exit_1
                        and self.focus == "exit_battery")
                    ):
                        if DEBUG:
                            print("Distance exit")

                        self.timer_map += 1
                        rew += 0.05
                    elif (
                        self.info["map"] == 1
                        and (self.info["battery"]
                        and new_dis_1 >= exit_1
                        and self.focus == "exit_battery")
                    ):
                        rew -= 0.05
                        self.timer_map = 0
                    elif (
                        self.info["map"] == 2
                        and self.info["phone"]
                        and new_dis_2 < exit_2
                        and self.focus == "exit_phone"
                    ):
                        if DEBUG:
                            print("Distance exit")

                        self.timer_map += 1
                        rew += 0.05
                    elif (
                        self.info["map"] == 2
                        and self.info["phone"]
                        and new_dis_2 >= exit_2
                        and self.focus == "exit_phone"
                    ):
                        rew -= 0.05
                        self.timer_map = 0
                except UnboundLocalError:
                    pass

        if self.focus == "jason":
            if any(obj[4] == 1 for obj in obs) and self.agent == "victim":
                self.timer = 0

                victim_boxes = [obj for obj in obs if obj[4] == 2]
                killer_boxes = [obj for obj in obs if obj[4] == 1]

                if victim_boxes and killer_boxes:
                    dist = self.distance(victim_boxes, killer_boxes)
                    if dist > 0.3:
                        rew -= dist

            elif not any(obj[4] == 1 for obj in obs):
                self.timer += 1

            if agent == "victim" and self.info["status"] == "hide":
                if self.timer < 15:  # Ha visto il killer di recente
                    rew += 0.5
            elif agent == "victim" and self.info["slow"]:
                print("[STEP] Victim is slow")
                rew += 0.02

        # KILLER

        if agent == "killer":
            killer_boxes = [obj for obj in obs if obj[4] == 1]
            victim_boxes = [obj for obj in obs if obj[4] == 2]

            if victim_boxes and killer_boxes:
                ds = self.distance(victim_boxes, killer_boxes)

                rew += 0.05
                if ds > 0.4:
                    rew += ds
                self.timer = 0
            
            if not any(obj[4] == 2 for obj in obs):
                self.timer += 1

            # if self.timer > 15 and self.timer < 40:
            #    rew -= 0.01 * self.timer if 0.01 * self.timer < 0.2 else 0.2
            #    self.timer += 1

            # if self.info['end-game'] == False and (self.info['sub_map'] == 2 or self.info['sub_map'] == 4):
            #   rew += 0.01
            #    killer_boxes = [obj for obj in obs if obj[4] == 1]
            #    interaction_boxes = [obj for obj in obs if obj[4] == 5]
            #    if killer_boxes and interaction_boxes:
            #        ds = self.distance(killer_boxes, interaction_boxes)
            #        rew += 0.05

        if agent == "killer" and self.info["sub_map"] != sub_map and self.info["sub_map"] != self.pre_submap:
            self.pre_submap = sub_map

        if self.timer > 10:
            # Stessa sub_map
            if agent == "killer" and sub_map == self.info["sub_map"]:
                self.timer_map += 1
                if self.timer_map > 15:
                    rew -= 0.05 * self.timer_map if 0.05 * self.timer_map < 0.2 else 0.2
            elif (
                agent == "killer"
                and self.info["sub_map"] == self.pre_submap
            ):
                rew -= 0.1
            # Cambio sub_map
            elif (
                agent == "killer"
                and sub_map != self.info["sub_map"]
                and self.timer_map > 10
            ):
                self.timer_map = 0
                rew += 0.3
            # Cambio sub_map troppo presto
            elif (
                agent == "killer"
                and sub_map != self.info["sub_map"]
            ):
                self.timer_map = 0
                rew -= 0.2

        # If the agent is the killer and interacts with a object, give a small reward
        if agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact") and (any(obj[4] == 5 for obj in obs) or any(obj[4] == 3 for obj in obs)) and self.timer < 10 and self.info['end-game'] == False:
            rew += 0.3
        elif agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact") and (any(obj[4] == 5 for obj in obs) or any(obj[4] == 3 for obj in obs)) and self.info['end-game'] == True:
            rew += 0.1
        elif agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact") and (any(obj[4] == 2 for obj in obs)):
            rew += 0.2
        elif agent == "killer" and ((self.info['status'] == "interact") or action_meaning[action] == "interact"):
            rew -= 0.4

        if DEBUG:
            print(str(rew) + " reward for action: " + str(action_meaning[action]))

        return obs, rew, terminated

    def wait_for_ack(self, path):
        while True:
            try:
                with open(path, "r+") as f:
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
                    with open(
                        COM_FILES + "game_state_" + self.config["agent"] + ".json", "r+"
                    ) as f:
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

        return response  # Return the response from the Java server

    # Function to get the current game state from the Java server
    def get_game_state(self, agent):
        """
        Get the current game state from the Java game server for a specific agent.
        Args:
            agent (str): The agent for which to get the game state ("killer" or "victim").
        """
        # Send a request to the Java game server to get the current game state
        game_state = self.send_action_to_java(
            {"get-game": True, "agent": agent, "action": "get-game"}
        )

        # Update agent states based on the game state
        if agent == "victim":
            self.info = {
                "status": game_state[agent][
                    "status"
                ],  # Status of the agent (hide, visible, interact)
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
                "distance_1_x": game_state[agent]["distance_1_x"],
                "distance_1_y": game_state[agent]["distance_1_y"],
                "distance_2_x": game_state[agent]["distance_2_x"],
                "distance_2_y": game_state[agent]["distance_2_y"],
                "killer_distance": False,
                "num_obstacle": 0,
                "num_win": 0,
                "num_hide": 0,
                "num_interaction": 0,
                "num_slow": 0,
                "killer_visible": False,
                "agent_x": game_state[agent]["agent_x"],
                "agent_y": game_state[agent]["agent_y"],
            }
        else:
            self.info = {
                "status": game_state[agent]["status"],
                "map": game_state[agent]["map"],
                "slow": game_state[agent]["slow"],
                "win": game_state[agent]["win"],
                "end-game": game_state[agent]["end-game"],
                "finished": game_state[agent]["finished"],
                "sub_map": game_state[agent]["sub_map"],
                "victim_visible": False,
                "num_obstacle": 0,
                "num_win": 0,
                "num_hide": 0,
                "num_interaction": 0,
                "num_slow": 0,
                "agent_x": game_state[agent]["agent_x"],
                "agent_y": game_state[agent]["agent_y"],
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

        output = []
        output_path = ABSOLUTE_PATH + f"/Object_detection/detections_{"jason" if agent == "killer" else "panam"}.json"
        image_path = ABSOLUTE_PATH + f"/Object_detection/{"jason" if agent == "killer" else "victim"}_view.png"

        while True:
            try:
                with open(image_path, "r") as f:
                    try:
                        fcntl.flock(
                            f, fcntl.LOCK_SH
                        )  # shared lock, waits for exclusive release by Java
                        detections = self.detector.predict_single_image(image_path, conf_threshold=0.5)
                        break  # Exit loop if successful
                    finally:
                        fcntl.flock(f, fcntl.LOCK_UN)
            except Exception as e:
                print(f"[ERROR] Failed to read image file {image_path}: {e}")
                time.sleep(0.2)

        print(f"[INFO] {agent} object detection completed.")

        if detections:
            for r in detections:
                cls = r["class_name"]
                # Convert bbox values to native Python float
                x1 = float(r["bbox"][0])
                y1 = float(r["bbox"][1])
                x2 = float(r["bbox"][2])
                y2 = float(r["bbox"][3])
                conf = float(r["confidence"])
                output.append(
                    {
                        "class": cls,  # "killer" o "victim"
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
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
                if self.agent == "victim":
                    self.info["killer_visible"] = True
            elif class_name == "Victim":
                class_id = 2
                if self.agent == "killer":
                    self.info["victim_visible"] = True
            elif class_name == "Hide":
                class_id = 3
                self.info["num_hide"] += 1
            elif class_name == "Slow":
                class_id = 4
                self.info["num_slow"] += 1
            elif class_name == "Interaction":
                class_id = 5
                self.info["num_interaction"] += 1
            elif class_name == "Obstacle":
                class_id = 6
                self.info["num_obstacle"] += 1
            elif class_name == "Win":
                class_id = 7
                self.info["num_win"] += 1
            else:
                class_id = 0
            obs[i] = [x1, y1, x2, y2, class_id]

        return np.array(obs, dtype=np.float32)
    
    def set_focus(self, focus):
        """
        Set the focus of the agent.
        Args:
            focus (str): The focus of the agent ("exit_battery", "exit_phone", or "jason").
        """
        self.focus = focus
        print(f"[INFO] Focus set to {self.focus} for agent {self.config['agent']}")

    def close(self, *args, **kwargs):
        """
        Close the environment and release resources.
        """
        print("[INFO] Environment closed " + self.config["agent"])
        pass
