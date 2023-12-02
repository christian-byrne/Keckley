import json
import os

class Config:
    def __init__(self, root, dev=False):
        """Initialize the config object."""
        self.dev = dev
        self.root = root
        self.config_folder = f"{self.root}/config"
        self.config_path = self.get_correct_config()
        self.config = self.load_config()

    def get_correct_config(self):
        """Return the correct config file based on the DEV flag."""
        if self.dev:
            return f"{self.config_folder}/dev-config.json"
        elif os.path.getsize("./config/user-profile-1.json") > 0:
            return f"{self.config_folder}/user-profile-1.json"
        else:
            return f"{self.config_folder}/defaults.json"

    def load_config(self):
        """Load the config file and return the config object."""
        with open(self.config_path) as config_file:
            config = json.load(config_file)
        return dict(config)

    def get(self, key):
        """Return the value of the key."""
        return self.config[key]
