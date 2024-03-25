# MAIA

## Requirements and Installation

```bash
git clone https://github.com/foglar/maia.git

cd maia

pip3 install -r requirements.txt
python3 main.py
```

> [!TIP]
> It is recommended practice to use a virtual enviroment.
> Download **[conda][conda]** and create a venv `conda -n maia`.
> Activate it with a command `conda activate ~/.conda/envs/maia`

- get an API key on the [astrometry.net][astrometryapi] and add it into the file **secret.py** as a variable *A_TOKEN*

```bash
# secret.py
A_TOKEN = "your_token"
```

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