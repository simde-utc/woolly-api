from .models import User, UserType


def find_or_create_user(user_infos):
	"""
	Helper to fetch or create user in Woolly database from user_infos (email)
	"""
	try:
		# Try to find user
		user = User.objects.get(email = user_infos['email'])
	except User.DoesNotExist:
		user = create_user(user_infos)
		if type(user) is dict and 'error' in user:
			print(user_infos)
			print(user)
			raise User.DoesNotExist("Erreur lors de la création de l'utilisateur")

	# Mise à jour des attributs de l'user si besoin
	madeChanges = False

	# UserType
	userType = UserType.EXTERIEUR
	if user_infos['types']['cas'] == True:
		userType = UserType.NON_COTISANT
	if user_infos['types']['contributorBde'] == True:
		userType = UserType.COTISANT

	if user.usertype.name != userType:
		try:
			user.usertype = UserType.objects.get(name=userType)
		except UserType.DoesNotExist:
			raise UserType.DoesNotExist("Met à jour les users_types avec UserType.init_values() pardi !!!")
		madeChanges = True

	# Admin
	if user.is_admin != user_infos['types']['admin']:
		user.is_admin = user_infos['types']['admin']
		madeChanges = True

	# Sauvegarde si besoin
	if madeChanges:
		user.save()

	return user


def create_user(user_infos):
	# Create user
	# TODO : birthdate, login
	from .serializers import UserSerializer
	serializer = UserSerializer(data={
		'email': user_infos['email'],
		'first_name': user_infos['firstname'],
		'last_name': user_infos['lastname'],
		'login': user_infos.get('login', None),
		# 'associations': '',
		# 'birthdate': ''
	})
	if not serializer.is_valid():
		# TODO : Exceptions
		print("================== ERROORRRRS ==================")
		print(serializer.errors)
		return {
			'error': 'Invalid serialization',
			'errors': serializer.errors
		}
	user = serializer.save()
	return user