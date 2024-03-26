# OV2024

## Requirements and Installation

```bash
git clone https://github.com/foglar/ov2024.git

cd ov2024

pip3 install -r requirements.txt
```

> [!TIP]
> It is recommended practice to use a virtual enviroment.
> Download **[conda][conda]** and create a venv `conda -n ov2024`.
> Activate it with a command `conda activate ov2024`

- get an API key on the [astrometry.net][astrometryapi] and add it into the file **config.toml** as a variable *token* into astrometry category

```toml
[astrometry]

token = "your token in double quotes"
```

## Files

- `astrometry.py` - get **ra** and **dec** from astrometry api
- `compare.py` - finds and compares same meteors from two observatories
- `modules.py` - modules for loading config and etc...
- `main.py` - runs astrometry for each observation from both observatories in file tree

[astrometryapi]: https://nova.astrometry.net/api_help
[conda]: https://www.anaconda.com/download/
