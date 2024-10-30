import os
import tomli
import tomli_w
import re
import json
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
        

class EditConfig:
    """
    A class for editing the configuration settings in a TOML file.

    Args:
        file_path (str): The path to the TOML configuration file. Default is "config.toml".

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.

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
        
    def save_config(self, config):
        """
        Saves the configuration settings to the TOML file.

        Args:
            config (dict): The configuration settings to save.

        """
        with open(self.file_path, mode="wb") as fp:
            tomli_w.dump(config, fp)

    def remove_key(self, key, category="data"):
        """
        Removes a key from the configuration settings.

        Args:
            key (str): The key to remove.

        """
        config = self.load_config()
        if key in config[category]:
            del config[category][key]
            self.save_config(config)
        else:
            print(f"Key '{key}' not found in the configuration settings.")

    def set_value(self, key, value, category="data"):
        """
        Sets a value in the configuration settings.

        Args:
            key (str): The key to set.
            value (str): The value to associate with the key.

        """
        config = self.load_config()
        config[category][key] = value
        self.save_config(config)

class ParseData:
    """Parse from data.txt file, meteor and stars coordinates
    
    Args:
        data_path (str): data.txt file path

    Usage:
        Create ParseData object and call get_meteor_start_end_coordinates() and get_stars_coordinates() methods
        ```python
        PD = ParseData("data/data.txt")
        meteor = PD.get_meteor_start_end_coordinates()
        stars = PD.get_stars_coordinates()```

    Returns:
        list[float]: Meteor and stars coordinates
        list[float]: Stars coordinates
    """
    def __init__ (self, data_path):
        self.data_path = data_path
        self.data = self._read_file()
        self.parsed_data = self.parse_data()

    def parse_data(self):
        self.get_meteor_start_end_coordinates()
        self.get_stars_coordinates()

    def get_meteor_start_end_coordinates(self) -> list[float]:
        """Get meteor coordinates from data.txt file
        
        Args:
            path (str): data.txt file path

        Returns:
            tuple(): Meteor coordinates
        """
        file = open(self.data_path, 'r')
        for line in file:
            if line.startswith("#Meteor 1:"):
                match = re.search(r'start \(([^)]+)\) end \(([^)]+)\)', line)
                if match:
                    start = tuple(map(float, match.group(1).split(', ')))
                    end = tuple(map(float, match.group(2).split(', ')))
                    return start, end
        return None, None  # Return the coordinates of the meteor
    
    def get_stars_coordinates(self):
        star_pattern = re.compile(r"#\d+ position \((\d+\.?\d*), (\d+\.?\d*)\)")
        stars = star_pattern.findall(self.data)
        return [(float(x), float(y)) for x, y in stars]

    def _read_file(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"File {self.data_path} not found")
        
        with open(self.data_path, 'r') as f:
            data = f.read()
        return data
    
class cache():
    def __init__(self):
        self.dirname = os.path.dirname(__file__)
        self.cache_path = os.path.join(self.dirname, "cache")
        self.cache_file = os.path.join(self.cache_path, "cache.json")
        if not os.path.exists(self.cache_path):
            self.create_cache()
        self.load_cache()

    def create_cache(self):
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)
            self.cache = {}
            self.save_cache()
        else:
            print("Cache already exists")

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as file:
                self.cache = json.load(file)
        else:
            self.cache = {}
    
    def save_cache(self):
        with open(self.cache_file, "w") as file:
            json.dump(self.cache, file)

    def get(self, key):
        return self.cache.get(key)
    
    def search(self, ident, obs):
        for key, value in self.cache.items():
            if value[0] == ident and value[1] == obs:
                return key
        return None
    
    def set_key(self, key, value, observatory):
        # each key have two values, id and observatory
        self.cache[key] = (value, observatory)
        self.save_cache()

    def delete(self, key):
        if self.cache.get(key):
            del self.cache[key]
        self.save_cache()
    
    def print_cache(self):
        print(self.cache)

    def clear_cache(self):
        self.cache = {}
        self.save_cache()


if __name__ == "__main__":
    print(ParseData("data/data.txt").get_meteor_start_end_coordinates())
    print(ParseData("data/data.txt").get_stars_coordinates())