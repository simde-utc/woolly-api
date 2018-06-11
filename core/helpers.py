from django.http import JsonResponse
from rest_framework import status

def errorResponse(message, errors = tuple(), httpStatus = status.HTTP_400_BAD_REQUEST):
	resp = {
		'message': message,
		'errors': [ {'detail': e} for e in errors ]
	}
	return JsonResponse(resp, status=httpStatus)
