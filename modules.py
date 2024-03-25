import os
import tomli


class ConfigLoader:
    def __init__(self, file_path="config.toml"):
        self.file_path = file_path

    def load_config(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, mode="rb") as fp:
                config = tomli.load(fp)
            return config
        else:
            raise FileNotFoundError(
                f"Config file '{self.file_path}' not found. Create it and add astrometry token"
            )

    def get_astrometry_key(self):
        config = self.load_config()
        if "astrometry" in config and "token" in config["astrometry"]:
            return config["astrometry"]["token"]
        else:
            raise KeyError("Astrometry token not found in config.")
