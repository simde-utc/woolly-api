DEBUG = False
ALLOWED_HOSTS = (
	'woolly.etu-utc.fr',
	'assos.utc.fr',
	'localhost',
)


# SECRET KEYS
JWT_SECRET_KEY = ""
SECRET_KEY = ""
GINGER_KEY = ""
PAYUTC_KEY = ""
PORTAL = {
	'id': 	1,
	'key': 	'Y0sUCdZ8oGpxdBZwVgV2aAQghUMtrcDAHiOAm5qN'
}

# MAIN DATABASE
DATABASE = {
	'ENGINE': 'django.db.backends.mysql',	# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
	'NAME': 'woolly',						# Or path to database file if using sqlite3.
	'USER': 'root',							# Not used with sqlite3.
	'PASSWORD': '',							# Not used with sqlite3.
	'HOST': '',								# Set to empty string for localhost. Not used with sqlite3.
	'PORT': '',								# Set to empty string for default. Not used with sqlite3.
}