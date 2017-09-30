# waarnemingkaart

Requires Python 3.4+ and Django 1.11+


## Installation (Linux)

Get the code and enter the project directory,
```
$ git clone --recursive https://github.com/bartromgens/waarnemingkaart.git
$ cd waarnemingkaart
```
Install dependencies that you will need
```
$ apt-get install virtualenv
```
or
```
$ pip install virtualenv
```
Install via the install script (creates a Python 3 virtualenv with dependencies, a local_settings.py file, and a sqlite database),
```
$ ./install.sh
```

Activate the virtualenv (always do this before working on the project),
```
$ source env/bin/activate
```

#### Create a superuser (optional)
This allows you to login at the website as superuser and view the admin page,
```
(env)$ python manage.py createsuperuser
```

#### Run a developement webserver
Run the Django dev web server in the virtualenv (don't forget to active the virtualenv),
```
(env)$ python manage.py runserver
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
```
$ crontab -e
*/5 * * * * source /home/<username>/.bashrc && source /home/<path-to-project>/env/bin/activate && python /home/<path-to-project>/website/manage.py runcrons > /home/<path-to-project>/log/cronjob.log
```

## Data

### Load data
Load waarneming.nl scraped observation data,
```
$ python manage.py loaddata <MAPS_DATA_DIR>/observations.json.gz
```
Where `MAPS_DATA_DIR` is the directory set in `local_settings.py`.

### Scrape data

### Export data
Run the following command to create a compressed json data dump, `observations.json.gz` in the `settings.MAPS_DATA_DIR` directory, of all observations,
```bash
$ python manage.py create_json_dump
```

## Commands

Create a species map,
```bash
$ python manage.py create_map --species="grutto"
```

Create maps for all groups, families and species, or a specific group,
```bash
$ python manage.py create_maps [--group="vogels"] [--skip-groups] [--skip-families] [--skip-species]
```

## Development

### Webpack bundles (JavaScript and CSS)

Install webpack and some plugins and loaders,
```bash
$ sudo npm install webpack -g
$ npm install webpack path webpack-manifest-plugin webpack-cleanup-plugin extract-text-webpack-plugin css-loader style-loader babel-core babel-loader babel-preset-es2015
```

Webpack config is found in `webpack.config.js`.

Watch for changes and compile bundle if found,
```bash
$ webpack --progress --colors --watch
```

Generate minified production files,
```bash
$ webpack -p
```

### Testing

Run all tests,
```
$ python manage.py test
```

Run specific tests (example),
```
$ python manage.py test website.tests.TestCaseAdminLogin
```
