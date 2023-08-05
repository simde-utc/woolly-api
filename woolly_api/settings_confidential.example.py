DEBUG = False
ALLOWED_HOSTS = (
	'woolly.etu-utc.fr',
	'assos.utc.fr',
	'localhost',
)
CSRF_ALLOWED_HOSTS= (
	'https://assos.utc.fr',
)

HTTPS_ENABLED = True

# Secret Keys
JWT_SECRET_KEY = ''
SECRET_KEY = ''
GINGER_KEY = ''
PAYUTC_KEY = ''

# OAuth
PORTAL = {
	'id': 	0,
	'key': 	'',
	'callback': ''
}

# Main Database
DATABASE = {
	'ENGINE': 'django.db.backends.mysql',	# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
	'NAME': 'woolly',						# Or path to database file if using sqlite3.
	'USER': '',								# Not used with sqlite3.
	'PASSWORD': '',							# Not used with sqlite3.
	'HOST': '',								# Set to empty string for localhost. Not used with sqlite3.
	'PORT': '',								# Set to empty string for default. Not used with sqlite3.
	'OPTIONS': {
		'sql_mode': 'traditional'
	}
}

# SMTP server
EMAIL = {
	'host': 'localhost',
	'port': 25,
	'user': '',
	'pwd':  '',
	'tls':  False,
	'ssl':  False,
}
# To send from a UTC email address : https://5000.utc.fr/front/knowbaseitem.form.php?id=59
# EMAIL = {
# 	'host': 'smtps.utc.fr',
# 	'port': 465,
# 	'user': 'user@AD',
# 	'pwd':  '',
# 	'tls':  False,
# 	'ssl':  True,
# }
