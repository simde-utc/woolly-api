from django.http import JsonResponse

def errorResponse(message, errors, httpStatus):
	resp = {
		'message': message,
		'errors': [ {'detail': e} for e in errors ]
	}
	return JsonResponse(resp, status=httpStatus)
