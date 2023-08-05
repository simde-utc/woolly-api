"""woolly_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.contrib import admin
from core.views import api_root

# Admin site configuration
admin.site.site_header = "Woolly Administration"
admin.site.site_title  = "Woolly Admin"
admin.site.index_title = "General administration"


urlpatterns = [
	re_path(r'^$',		api_root, name="root"),				# Api Root pour la documentation
	re_path(r'^admin/',	admin.site.urls),					# Administration du site en backoffice
	re_path(r'^',		include('authentication.urls')),	# Routes d'authentification
	re_path(r'^',		include('sales.urls')),				# Routes pour les assos, les ventes et autres
	re_path(r'^',		include('payment.urls')),			# Routes pour les paiements
]
