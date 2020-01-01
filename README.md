# waarnemingkaart
[![Build Status](https://travis-ci.org/bartromgens/waarnemingkaart.svg?branch=master)](https://travis-ci.org/bartromgens/waarnemingkaart) [![Coverage Status](https://coveralls.io/repos/github/bartromgens/waarnemingkaart/badge.svg?branch=master)](https://coveralls.io/github/bartromgens/waarnemingkaart?branch=master)

A visualization of animal and plant observations on an interactive map. 

Observation data is created by users of http://waarneming.nl.

waarnemingkaart is a web-application based on Django, Bootstrap and OpenLayers. 

Requires Python 3.5+ and Django 1.11+

## Demo

http://waarnemingkaart.nl

## Installation (Linux)

#### Get the code and install dependencies
Get the code and enter the project directory,
```bash
git clone --recursive https://github.com/bartromgens/waarnemingkaart.git
cd waarnemingkaart
```

Create a virtualenv,
```bash
virtualenv -p python3 env
```

Activate the virtualenv (always do this before working on the project),
```bash
source env/bin/activate
```

Install dependencies,
```bash
pip install -r requirements.txt
```

Compile external (C++)-module,
```bash
make -C maps/modules
```

#### Create local settings and database
Create local user settings, you can optionally change settings here, default database is sqlite,
```bash
python create_local_settings.py
```

Create the database and tables, 
```bash
python manage.py migrate
```

#### Create a superuser (optional)
This allows you to login at the website as superuser and view the admin page,
```bash
python manage.py createsuperuser
```

#### Run a developement webserver
Run the Django dev web server in the virtualenv (don't forget to active the virtualenv),
```bash
python manage.py runserver
```

The website is now available at http://127.0.0.1:8000 and admin http://127.0.0.1:8000/admin.

## Configuration (optional)

#### local_settings.py

The local settings are defined in `website/local_settings.py`. 
These are not under version control and you are free change these for your personal needs.
This is also the place for secret settings. An example, on which this file is based, is found in `website/local_settings_example.py`.

#### Daily backups (cronjob)
This project has a django-cronjob that makes daily backups of the raw database (includes everything), and a json dump of the data.
These are defined in `website/cron.py`. The location of the backup files is defined in `website/local_settings.py`. 
Create the following cronjob (Linux) to kickstart the `django-cron` jobs,
```text
*/5 * * * * source /home/<username>/.bashrc && source /home/<path-to-project>/env/bin/activate && python /home/<path-to-project>/website/manage.py runcrons > /home/<path-to-project>/log/cronjob.log
```

## Data

### Load data
Load waarneming.nl scraped observation data,
```bash
python manage.py loaddata <MAPS_DATA_DIR>/observations.json.gz
```
Where `MAPS_DATA_DIR` is the directory set in `local_settings.py`.

### Scrape data

### Export data
Run the following command to create a compressed json data dump, `observations.json.gz` in the `settings.MAPS_DATA_DIR` directory, of all observations,
```bash
python manage.py create_json_dump
```

## Commands

Create a species map,
```bash
python manage.py create_map --species="grutto"
```

Create maps for all groups, families and species, or a specific group,
```bash
python manage.py create_maps [--group="vogels"] [--skip-groups] [--skip-families] [--skip-species]
```

## Development

### Webpack bundles (JavaScript and CSS)

Install webpack and some plugins and loaders,
```bash
sudo npm install webpack -g
npm install
```

Webpack config is found in `webpack.config.js`.

Watch for changes and compile bundle if found,
```bash
webpack --progress --colors --watch
```

Generate minified production files,
```bash
webpack -p
```

### Testing

Run all tests,
```bash
python manage.py test
```

Run specific tests (example),
```bash
python manage.py test website.tests.TestCaseAdminLogin
```
