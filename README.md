# OV2024

## Requirements and Installation

```shell
git clone https://github.com/foglar/ov2024.git

cd ov2024

pip3 install -r requirements.txt
```

> [!TIP]
> It is recommended practice to use a virtual environment.
> Download **[conda][conda]** and create a venv `conda -n ov2024`.
> Activate it with a command `conda activate ov2024`

- get an API key on the [astrometry.net][astrometryapi] and add it into the file **config.toml** as a variable *token* into astrometry category

```toml
[astrometry]

token = "your token in double quotes"

[data]

home_dir = "/home/foglar/Documents/Programming/Projects/OV2024-Project/meteory"
```

```shell
.
├── "Observatory A"
│  └── 2024-01-08-21-35-44
│     ├── 2024-01-08-21-35-44.jpg
│     └── data.txt
└── "Observatory B"
   └── 2024-01-08-21-35-44
      ├── 2024-01-08-21-35-44.jpg
      └── data.txt
```

## Files

- `astrometry.py` - get **ra** and **dec** from astrometry api
- `compare.py` - finds and compares same meteors from two observatories
- `modules.py` - modules for loading config and etc...
- `main.py` - runs astrometry for each observation from both observatories in file tree
- `coordinates.py` - converts coordinates from pixels to **ra** and **dec**
- `trajectory.py` - calculates meteor trajectory

# Usage

## Station instance setup

A Station class instance is used to store information about the stations used for meteor trajectory calculation. It stores the station location, time, time zone and WCS file used for calculations without astrometry.

### WCS updating

The WCS file to be used for calculations without astrometry is stored in a .wcs file created by the `download_wcs_file()` function in `coordinates.py`. To perform these calculations, the time for which the astrometry used for camera alignment is needed. To update both of these, use the `set_wcs()` function, which takes the WCS file path and time as arguments. The time should be passed as a string in [one of the formats used by astropy.][astropy_times]

### Time updating

Time must be updated for each meteor, since it is used in the calculation. To update the time of the station, use `set_time()` function, which takes the time as string as an argument. The time should again be passed in [in one of the supported formats.][astropy_times] The time zone of the station can also be updated with this function, simply pass in the offset in hours from GMT in as `time_zone` to update it while updating the time.

### Time updating

## Meteor calculation

Meteor calculation is handled by the `trajectory.py` code using the `Meteor` class.

### Performing calculations

The calculation can be performed automatically - when requesting specific data about the meteor (e. g. the radiant), the Meteor instance will perform all the required calculations to calculate the requested data. (e. g. the `Meteor.get_radiant function` will calculate the radiant), or manually, by using the specific function (e. g. `Meteor.calculate_radiant`).

[astrometryapi]: https://nova.astrometry.net/api_help
[conda]: https://www.anaconda.com/download/
[astropy_times]: https://docs.astropy.org/en/stable/time/index.html#time-format
