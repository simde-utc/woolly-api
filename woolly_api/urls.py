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
from django.conf.urls import url, include
from django.contrib import admin
from core.views import api_root

urlpatterns = [
	url(r'^$', api_root),								# Api Root pour la documentation
	url(r'^admin/', admin.site.urls),					# Administration du site en backoffice
	url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),		# OAuth
	url(r'^',       include('authentication.urls')),	# Routes d'authentification
	url(r'^',       include('sales.urls')),				# Routes pour les assos, les ventes et autres
	url(r'^',       include('payutc.urls')),			# Routes pour payutc
]
