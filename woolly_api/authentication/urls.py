from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from authentication.views import CreateWoollyUserView

# from .views import CreateOrderView, CreateItemView, ItemDetailsView, OrderDetailsView, CreateWoollyUserView
import cas.views

# API endpoints
urlpatterns = {
	url(r'^auth/', include('rest_framework.urls',
	                       namespace='rest_framework')),
	url(r'^users/', CreateWoollyUserView.as_view(), name="users"),
	url(r'^login/$', cas.views.login, name='login'),
	url(r'^logout/$', cas.views.logout, name='logout'),
}


urlpatterns = format_suffix_patterns(urlpatterns)
