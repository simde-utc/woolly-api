from django.contrib.auth.models import BaseUserManager




class WoollyUserManager(BaseUserManager):
	
	#required by Django
	def create_user(self, login, password = None, **other_fields):
		if not login :
			raise ValueError('The given login must be set')
		user = self.model(login = login,
                         **other_fields)
		user.set_password(password)
		user.save(using = self._db)
		return user
		
	#required by Django
	def create_superuser(self, login, password, **other_fields):
		user = self.create_user(login, 
								password = password,
								**other_fields,
							)
		user.is_admin = True
		user.save(using = self._db)
		return user
