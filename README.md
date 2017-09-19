# Woolly-api

The brand new online ticket office for UTC student organizations

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

First of all, you need to set up the environement. Put yourself in the directory of your choice and follow the following instructions : 

If you don't have it yet, install python3
```
pip install pip3
```
Then the virtual environement :
```
pip install virtualenv
```
Create a virtualenv :
```
virtualenv -p python3 "name"
source venv/bin/activate
```
Installing Django and the useful librairies
```
pip install django==1.11.1
pip install djangorestframework==3.6.3
pip install django-cas-client==1.3.0
pip install django-cors-headers==2.1.0
pip install djangorestframework-jsonapi==2.2.0
```

### Installing

Once you have your virtual environment up and running, you can clone this repo

```
git clone https://github.com/simde-utc/woolly-api.git
```

Then you will need to go into the woolly_api app

```
cd woolly-api
cd woolly_api
```

Now you will need to initialise the database, like this :

```
python manage.py shell
>>> from authentication.models import WoollyUserType
>>> WoollyUserType.init_values()
>>> exit()
```

Finally you can migrate the database and launch the server

```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

You can now play with the server on [localhost:8000](http://localhost:8000)

## Routes

You can have the routes list in the sales app, under sales/url.py.
To connect through the CAS, please use [localhost:8000/login](http://localhost:8000/login) and [localhost:8000/logout](http://localhost:8000/logout) to logout.

By default, your user has default rights, you will need to modify the WoollyUser table in the db.sqlite3 file in order to set yourself as an admin and use the [admin pannel](http://localhost:8000/admin).


## Deployment

Choose a database system in general settings.py DATABASES (see https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-DATABASES)

Check deployment checklist : https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

Deploy server using : https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/

## Built With

* [Django](https://www.djangoproject.com) - The web framework used
* [Django Rest Framework](http://www.django-rest-framework.org) - Toolkit for building Web APIs using Django
* [Django CAS Client](https://pypi.python.org/pypi/django-cas-client/) - Used to call the UTC CAS
* [Django Rest Framework JSON API](https://github.com/django-json-api/django-rest-framework-json-api) - Used to forma the JSON files according to the JSON API


## Authors

* **[Thomas Barizien](https://github.com/tbarizien)** - *Initial work*
* **[Florian Cartier](https://github.com/FCartier)** - *Initial work*

See also the list of [contributors](https://github.com/simde-utc/woolly-api/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

