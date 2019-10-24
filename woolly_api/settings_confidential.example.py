DEBUG = False
HTTPS_ENABLED = True
ALLOWED_HOSTS = (
	'assos.utc.fr',
)
CORS_ORIGIN_WHITELIST = (
	'https://assos.utc.fr',
)

# Secret Keys
SECRET_KEY = ''
PAYUTC_KEY = ''
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
