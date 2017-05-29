# woolly-api
The brand new online ticket office for UTC student organizations

# Deployment instructions
Libraries : 
'''sh
pip install django==1.11.1
pip install djangorestframework==3.6.3
pip install django-cas-client==1.3.0
pip install djangorestframework-jsonapi==2.0.0-beta.1
'''
            
Choose DB in general settings.py DATABASES (see https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-DATABASES)

init DB : 
'''sh
python manage.py shell
>>> from core.models import WoollyUserType
>>> WoollyUserType.init_values()
'''
     
Check deployment checklist : https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
Deploy server using : https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/

