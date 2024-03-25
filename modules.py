import os
import tomli


class ConfigLoader:
    """
    A class for loading and retrieving configuration settings from a TOML file.

    Args:
        file_path (str): The path to the TOML configuration file. Default is "config.toml".

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        KeyError: If the required configuration settings are not found in the file.

    """

    def __init__(self, file_path="config.toml"):
        self.file_path = file_path

    def load_config(self):
        """
        Loads the configuration settings from the TOML file.

        Returns:
            dict: The loaded configuration settings.

        Raises:
            FileNotFoundError: If the specified configuration file does not exist.

        """
        if os.path.exists(self.file_path):
            with open(self.file_path, mode="rb") as fp:
                config = tomli.load(fp)
            return config
        else:
            raise FileNotFoundError(
                f"Config file '{self.file_path}' not found. Create it and add astrometry token"
            )

    def get_astrometry_key(self):
        """
        Retrieves the astrometry token from the configuration settings.

        Returns:
            str: The astrometry token.

        Raises:
            KeyError: If the astrometry token is not found in the configuration settings.

        """
        config = self.load_config()
        if "astrometry" in config and "token" in config["astrometry"]:
            return config["astrometry"]["token"]
        else:
            raise KeyError("Astrometry token not found in config.toml")

    def get_home_dir(self):
        """
        Retrieves the home directory from the configuration settings.

        Returns:
            str: The home directory.

        Raises:
            KeyError: If the home directory is not found in the configuration settings.

        """
        config = self.load_config()
        if "data" in config and "home_dir" in config["data"]:
            return config["data"]["home_dir"]
        else:
            raise KeyError("Home directory not found in config.toml")
