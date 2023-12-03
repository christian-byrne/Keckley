import json


class Config:
    def __init__(self, config_file_path):
        """Initialize the config object."""
        self.config_file_path = config_file_path
        self.config = self.load_config()

    def get(self, key):
        """Return the value of the key."""
        return self.config[key]

    def set(self, key, value):
        """Set the value of the key."""
        self.config[key] = value
        self.save_config()

    def load_config(self):
        """Load the config file and return the config object."""
        with open(self.config_file_path) as config_file:
            config_dict = json.load(config_file)
        return dict(config_dict)

    def save_config(self):
        """Save the config file."""
        with open(self.config_file_path, "w") as config_file:
            json.dump(self.config, config_file, indent=4)
