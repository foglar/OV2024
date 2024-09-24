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

## Usage

## Meteor calculation

Meteor calculation is handled by the `trajectory.py` code using the `Meteor` class.

### Performing calculations

The calculation can be performed automatically - when requesting specific data about the meteor (e. g. the radiant), the Meteor instance will perform all the required calculations to calculate the requested data. (e. g. the `Meteor.get_radiant function` will calculate the radiant), or manually, by using the specific function (e. g. `Meteor.calculate_radiant`).

[astrometryapi]: https://nova.astrometry.net/api_help
[conda]: https://www.anaconda.com/download/
