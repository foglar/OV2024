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
> Activate it with a command `conda activate ~/.conda/envs/ov2024`

- get an API key on the [astrometry.net][astrometryapi] and add it into the file **config.toml** as a variable *token* into astrometry category

```toml
[astrometry]

token = "your token in double quotes"
```

## Files

- `astrometry-client.py` - get **ra** and **dec** from astrometry api
- `compare.py` - finds and compares same meteors from two observatories
- `modules.py` - modules for loading config and etc...

## Documentation

### class AstronomyClient()

#### authenticate()

- Authenticate user and obtain session key
- self.session

#### upload_image()

- self, path
- Upload image and return submission_ID
- return submission_id

#### check_job_status()

- self, submission_ID

#### get_calibration()

#### get_wcs_file_url()

#### download_wcs_file()

[astrometryapi]: https://nova.astrometry.net/api_help
[conda]: https://www.anaconda.com/download/
