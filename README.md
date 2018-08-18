# Woolly - API

Woolly is the online shop of all the [associations of the Université de Technologie de Compiègne](https://assos.utc.fr).


## Installation

### Prerequisites

First of all, you need to set up the environment.
You will need [Python version 3](https://www.python.org/downloads/) and [pip (a Python packages manager)](https://pypi.org/project/pip/).


Then we will set up the virtual environment with `virtualenv`.
```sh
pip install virtualenv
```

Create the `venv` folder :
On Linux :
```sh
virtualenv -p python3 "venv"        # python3 is the name of python executable
```
On Windows :
```sh
virtualenv "venv"
```

Now activate the virtual environment. You have to do this everytime you want to work with Woolly and don't see the `(venv)` on the left of your terminal prompt.
```sh
# On Linux :
source venv/bin/activate
# On Windows :
venv\Scripts\activate
```


### Installation

With the virtual environment activated, install all the required librairies :
```sh
pip install -r requirements.txt
```


Now ask a responsible person for the `settings_confidential.py` file containing the foreign APIs identification keys. The file is to be placed next to the `settings.py` file. There is a placeholder file called `settings_confidential.example.py`, you can copy and fill it. 


Create your database named `woolly`, set charset to UTF-8 with :
```sql
ALTER DATABASE `woolly` CHARACTER SET utf8;
```

Then you need to migrate, and initialize the database :
```sh
python manage.py migrate
python manage.py loaddata usertypes
```

You also need to generate all static files :
```sh
python manage.py collectstatic
```

Finally, you can launch the server.
```sh
python manage.py runserver
```

You can now play with the server on http://localhost:8000

You can find (the documentation of the API here)[./documentation/api.md].


## Deployment

Check this deployment checklist : https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

Deploy server using : https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/

Here, on deployment with use Apache to run the server.
Install `mod_wsgi` : `sudo apt-get install libapache2-mod-wsgi-py3`
Restart apache for mod_wsgi to be effective : `sudo systemctl restart apache2`

In an Apache config file (like `/etc/apache2/apache2.conf`), replace `BASE_FOLDER` with the path to where you installed Woolly :
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
And restart Apache : `sudo systemctl restart apache2`.

You have to restart Apache each time you modify your application for the changes to be applied.

## Need help ?

Don't forget to check the `./documentation/` folder for more documentation on Woolly.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

