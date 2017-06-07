import re

from django.utils.text import compress_string
from django.utils.cache import patch_vary_headers

from django import http

try:
	import settings

	XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
	XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
except:
	XS_SHARING_ALLOWED_ORIGINS = {'*', }
	XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']


class XsSharing(object):
	"""
		This middleware allows cross-domain XHR using the html5 postMessage API.


		Access-Control-Allow-Origin: http://foo.example
		Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
	"""

	def process_request(self, request):

		if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
			response = http.HttpResponse()
			if 'HTTP_ORIGIN' in request.META:
				for origin in XS_SHARING_ALLOWED_ORIGINS:
					if origin == request.META['HTTP_ORIGIN']:
						response['Access-Control-Allow-Origin'] = origin
						break
			response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)

			return response

		return None

	def process_response(self, request, response):
		# Avoid unnecessary work
		if response.has_header('Access-Control-Allow-Origin'):
			return response

		if 'HTTP_ORIGIN' in request.META:
			for origin in XS_SHARING_ALLOWED_ORIGINS:
				if origin == request.META['HTTP_ORIGIN']:
					response['Access-Control-Allow-Origin'] = origin
					break
		response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)

		return response
