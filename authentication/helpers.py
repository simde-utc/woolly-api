from authlib.specs.rfc7519 import JWTError
from .models import User, UserType
from .serializers import UserSerializer


def get_jwt_from_request(request):
	"""
	Helper to get JWT from request
	Return None if no JWT
	"""
	jwt = request.META.get('HTTP_AUTHORIZATION', None)	# Traité automatiquement par Django
	if not jwt or jwt == '':
		return None
	if jwt[:7] != 'Bearer ':
		raise JWTError("Authorization header doesn't begin with 'Bearer '")
	return jwt[7:]		# substring : Bearer ...


def find_or_create_user(user_infos):
	"""
	Helper to fetch or create user in Woolly database from user_infos (email)
	"""
	try:
		# Try to find user
		user = User.objects.get(email = user_infos['email'])
	except User.DoesNotExist:
		user = create_user(user_infos)
		if 'error' in user:
			print(user_infos)
			print(user)
			raise User.DoesNotExist("Erreur lors de la création de l'utilisateur")

	# Mise à jour des attributs de l'user si besoin
	madeChanges = False

	# UserType
	userType = UserType.EXTERIEUR
	if user_infos['is_cas'] == True:
		userType = UserType.NON_COTISANT
	if user_infos['is_contributorBde'] == True:
		userType = UserType.COTISANT

	if user.usertype.name != userType:
		try:
			user.usertype = UserType.objects.get(name=userType)
		except UserType.DoesNotExist:
			raise UserType.DoesNotExist("Met à jour les users_types avec UserType.init_values() pardi !!!")
		madeChanges = True

	# Admin
	if user.is_admin != user_infos['is_admin']:
		user.is_admin = user_infos['is_admin']
		madeChanges = True

	# Sauvegarde si besoin
	if madeChanges:
		user.save()

	return user


def create_user(user_infos):
	# Create user
	# TODO : birthdate, login
	serializer = UserSerializer(data = {
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