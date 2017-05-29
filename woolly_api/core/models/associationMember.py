
from django.db import models
from django.contrib.auth import get_user_model

from core.models.association import Association


class AssociationMember(models.Model):
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	#association = models.ForeignKey(Association, on_delete=models.CASCADE)
	role = models.CharField(max_length=50)
	rights = models.CharField(max_length=50)
