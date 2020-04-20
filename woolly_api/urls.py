from django.conf.urls import url, include
from django.contrib import admin

from core.views import api_root

urlpatterns = [
    url(r'^$',       api_root,        name='root'),     # Api Root pour la documentation
    url(r'^admin/',  admin.site.urls, name='admin'),    # Administration du site en backoffice
    url(r'^',        include('authentication.urls')),   # Routes d'authentification
    url(r'^',        include('sales.urls')),            # Routes pour les ventes
    url(r'^',        include('payment.urls')),          # Routes pour les paiements
]
