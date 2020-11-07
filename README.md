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

Generate all static files with:
```bash
pipenv run python manage.py collectstatic
```

Check this deployment checklist: https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
Deploy server using: https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/

Here, for deployment with use Apache to run the server. Run the following commands:
```bash
# Install mod_wsgi
sudo apt-get install libapache2-mod-wsgi-py3
# Restart apache for mod_wsgi to be effective
sudo systemctl restart apache2
```

In an Apache config file (like `/etc/apache2/apache2.conf`), replace `BASE_FOLDER` with the path to where you installed Woolly:
```ini
ServerName YOUR_SERVER_NAME
WSGIScriptAlias / BASE_FOLDER/woolly_api/wsgi.py
WSGIDaemonProcess woolly-api python-home=BASE_FOLDER/venv python-path=BASE_FOLDER
WSGIProcessGroup woolly-api
WSGIPassAuthorization On

<Directory BASE_FOLDER>
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>
```
And restart Apache:
```bash
sudo systemctl restart apache2
```

You have to restart Apache each time you modify your application for the changes to be applied.

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
