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
        return self.get_value_from_data("token", "astrometry")

    def get_home_dir(self):
        """
        Retrieves the home directory from the configuration settings.

        Returns:
            str: The home directory.

        Raises:
            KeyError: If the home directory is not found in the configuration settings.

        """
        return self.get_value_from_data("home_dir")

    def get_value_from_data(self, key="home_dir", category="data"):
        """
        Retrieves a value from the data section of the configuration settings.

        Args:
            key (str): The key of the value to retrieve.

        Returns:
            str: The value associated with the specified key.

        Raises:
            KeyError: If the specified key is not found in the data section of the configuration settings.

        """
        config = self.load_config()
        if category in config and key in config[category]:
            return config[category][key]
        else:
            raise KeyError(f"Key '{key}' or Category '{category}' not found in the data section of config.toml")