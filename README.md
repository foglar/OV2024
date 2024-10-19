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

## Examples

### Station instance setup

A Station instance can be created by the following code:

```python
from station.py import Station

ondrejov = Station(lat=49.970222,
                   lon=14.780208,
                   height=524,
                   label='Ondřejov')
```

With this code, we create a station instance representing the station in Ondřejov. Since the times in observations from this station are given in GMT, we can leave the `time_zone` argument unset, defaulting to 0 (GMT), even though geographically it should be -1 (CET).

We can add WCS information using the `set_wcs` function, or whilst creating the station instance in the past example by passing in the wcs path and time as arguments.

```python
ondrejov.set_wcs(wcs_path='path/to/wcs/file',
                 wcs_time='2024-01-08 23:52:57')
```

### WCS download for fixed camera astrometry

To get a WCS file for fixed camera astrometry, we can use the `get_fixed_wcs` function. It takes an `AstrometryClient` instance and an image path as arguments. Additionally, a job_id can be given to download an already calculated WCS file, or the prep argument can be set `True` to preprocess the image before performing the astrometry.

```
get_fixed_wcs(client,
              img_path,
              job_id=None,
              prep=False)
```

### Meteor calculations

We can then use the station instance in meteor calculations. To create a Meteor instance from astrometry, we use the `Meteor.from_astrometry()` function.

```python
from trajectory.py import Meteor
from astropy import Time

img_paths = [
   'path/to/img_a.jpg',
   'path/to/img_b.jpg',
]

data_paths = [
   'path/to/data_a.txt',
   'path/to/data_b.txt',
]

time = Time('2024-01-08 23:52:57')

meteor = Meteor.from_astrometry('test',
                                [station_a, station_b],
                                img_paths,
                                data_paths,
                                time)
```

With this snippet, we create a Meteor instance from astrometry using images and data.txt files. The `Meteor.from_astrometry()` function attempts to get an astrometry solution from the given images and data.txt files through the [astrometry.net api][astrometryapi]. If the astrometry fails, it attempts to get a solution from the fixed camera alignment set for each station. For faster but rougher calculation, we can use the `Meteor.from_astrometry_fixed()` function, which skips the astrometry step and calculates only the fixed camera solution.

To perform calculations on this meteor, we call the desired functions to get the information we need. All required calculations are performed when calling the getter functions, or we can perform them implicitly by calling the required `calculate` functions.

```python
meteor.get_radiant()
```

[astrometryapi]: https://nova.astrometry.net/api_help
[conda]: https://www.anaconda.com/download/
[astropy_times]: https://docs.astropy.org/en/stable/time/index.html#time-format
