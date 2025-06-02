from ray.rllib.algorithms.callbacks import DefaultCallbacks

class MyCallbacks(DefaultCallbacks):
    """
    Custom callback class for RLlib to handle specific events during training.
    This class can be extended to implement custom behavior for various training events.
    """

    def __init__(self, num_episodes = 1, **kwargs):
        """
        Initialize the custom callbacks.
        """
        super().__init__(**kwargs)
        self.total_episodes = 0
        self.num_episodes = num_episodes

    def on_episode_end(self, *, worker, base_env, policies, episode, env_index, **kwargs):
        """
        Called when an episode ends.
        """
        # Custom logic can be added here
        self.total_episodes += 1
        if self.total_episodes >= self.num_episodes:
            print(f"Reached the target number of episodes: {self.num_episodes}. Stopping training.")
            worker.stop()