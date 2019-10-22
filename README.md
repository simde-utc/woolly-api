# Woolly - API

Woolly is the online shop of all the [clubs of the Université de Technologie de Compiègne](https://assos.utc.fr/woolly/).


## Prerequisites

First of all, you need to set up the environment.
You will need [python 3.7](https://www.python.org/downloads/) and [pip](https://pypi.org/project/pip/) (a python packages manager).


Then we will set up the virtual environment with `virtualenv`.
```bash
pip install virtualenv
```

Create the `venv` folder:
```bash
# On Linux:
virtualenv -p python3.7 "venv"
# On Windows:
virtualenv "venv"
```

Now activate the virtual environment. You have to do this every time you want to work with Woolly and don't see the `(venv)` on the left of your terminal prompt.
```bash
# On Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```


## Installation

With the virtual environment activated, install all the required libraries:
```bash
pip install -r requirements.txt
```


Now ask a responsible person for the `settings_confidential.py` file containing the external APIs identification keys. The file is to be placed next to the `settings.py` file. There is a placeholder file called `settings_confidential.example.py`, you can copy and fill it.


Create your database named `woolly`, set charset to UTF-8 with:
```sql
ALTER DATABASE `woolly` CHARACTER SET utf8;
```

Then you need to migrate, and initialize the database:
```bash
# Create migrations file
python manage.py makemigrations
# Apply migrations to the database
python manage.py migrate
# Create default user types
python manage.py shell --command="from authentication.models import UserType; UserType.init_defaults()"
# Get all associations in cache
python manage.py shell --command="from sales.models import Association; Association.objects.get_with_api_data()"
```

You also need to generate all static files:
```bash
python manage.py collectstatic
```

Finally, you can launch the development server:
```bash
python manage.py runserver
```

You can now play with the server on http://localhost:8000

You can find [the documentation of the API here](./documentation/api.md).

## Deployment

Check this deployment checklist: https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/
Deploy server using: https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/

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
# Run a interactive shell to interact with Woolly
python manage.py shell_plus
# Check the defined models
python manage.py inspectdb
# Check all TODOs, FIXME, ...
python manage.py notes
```

Don't forget to check the `./documentation/` folder for more documentation on Woolly.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details
