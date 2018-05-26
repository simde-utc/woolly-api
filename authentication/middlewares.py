from .backends import JWTBackend

class JWTMiddleware:
	"""
	Middleware to log user from JWT into request.user using JWTBackend
	"""
	def __init__(self, get_response):
		self.get_response = get_response
		self.backend = JWTBackend()

	def __call__(self, request):
		request.user = self.backend.authenticate(request)
		return self.get_response(request)

