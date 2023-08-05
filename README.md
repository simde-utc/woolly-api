# Woolly - API

Woolly is the online shop of all the clubs of the Université de Technologie de Compiègne: https://assos.utc.fr/woolly/.

## Prerequisites

You will need to install:
- [pyenv](https://github.com/pyenv/pyenv): to manage Python versions
- [pipenv](https://github.com/pypa/pipenv): to manage dependencies

## Installation

Simply run the following commands to install all dependencies for deployment and development:
```bash
make init
make init-dev
```

Now copy `example.env` to `.env` and fill the secrets within.

Make sure the database you are using is set to UTF-8 with:
```sql
ALTER DATABASE woolly CHARACTER SET utf8;
```

Finally you need to migrate models into the database:
```bash
make db-migrate
```

## Development

You can launch the development server on http://localhost:8000 with:
```bash
make run
```

You can find [the documentation of the API here](./documentation/api.md).

## Using Docker

If you are using [Docker](https://docker.com/) you can skip Installation and Development, but you will still need to copy and fill your `.env` file.

Build the docker image with:
```bash
make build
```

Run it with:
```bash
docker run --rm -it --env-file .env -p 8000:8000 woolly-api:dev
```

You can run other commands with:
```bash
docker run --rm -it --env-file .env -p 8000:8000 woolly-api:dev <command>
```

If you have trouble accessing your database from the container, replace `localhost` by `host.docker.internal` in `DATABASE_URL`.

## Deployment

For deployment it is easier to install the virtual environment in the same folder:
```bash
export PIPENV_VENV_IN_PROJECT="enabled"
pipenv install --deploy
```

Generate all static files with:
```bash
pipenv run python manage.py collectstatic
```

Read Django instructions here: https://docs.djangoproject.com/en/3.1/howto/deployment/

In the following configuration, `/path_to_woolly` corresponds to the absolute file path to where you installed the Woolly API git repository and `/url_to_woolly` to the base url where you want to deploy the API.

### Deploy static files with Apache

Add this to a Apache config file (like `/etc/apache2/apache2.conf`):
```ini
Alias /url_to_woolly/static /path_to_woolly/static
<Directory /path_to_woolly/static>
    Require all granted
</Directory>
```

### Deploy app using mod_wsgi and Apache

Documentation: https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/modwsgi/

First, install mod_wsgi and restart apache:
```bash
sudo apt-get install libapache2-mod-wsgi-py3
sudo systemctl restart apache2
```

In the Apache config:
```ini
ServerName YOUR_SERVER_NAME
WSGIScriptAlias /url_to_woolly /path_to_woolly/woolly_api/wsgi.py
WSGIDaemonProcess woolly-api python-home=/path_to_woolly/.venv python-path=/path_to_woolly
WSGIProcessGroup woolly-api
WSGIPassAuthorization On

<Directory /path_to_woolly>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>
```

And reload Apache configuration:
```bash
sudo systemctl reload apache2
```

You have to reload Apache each time you modify your application for the changes to be applied.

### Deploy app using ProxyPass and Apache

If you are running Djanog behind a reverse proxy you might need to add the following lines to your `.env`:
```
RUN_THROUGH_PROXY=True
BASE_URL=/url_to_woolly
```

Then in the Apache config:
```ini
ProxyPreserveHost On
ProxyPassMatch ^/url_to_woolly/static !
ProxyPass /url_to_woolly http://localhost:8444
ProxyPassReverse /url_to_woolly http://localhost:8444
```

## Need help ?

Here are some useful commands:
```bash
# Activate the pipenv environment
pipenv shell
# Run a interactive shell to interact with Woolly
python manage.py shell_plus
# Check the defined models
python manage.py inspectdb
# Check all TODOs, FIXME, ...
python manage.py notes
```

Don't forget to check the [./documentation/](./documentation/) folder for more documentation on Woolly.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](./LICENSE) file for details