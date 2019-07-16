from django.contrib.admin.apps import AdminConfig as DefaultAdminConfig
from django.contrib.admin import AdminSite as DefaultAdminSite
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.urls import reverse

class AdminConfig(DefaultAdminConfig):
	"""
	Woolly customized administration configuration
	"""
	default_site = 'woolly_api.admin.AdminSite'
	verbose_name = "Woolly Administration"

class AdminSite(DefaultAdminSite):
	"""
	Woolly customized administration site
	"""
	site_header = "Woolly Administration"
	site_title  = "Woolly Admin"
	index_title = "General administration"
	site_url = '/'

	def has_permission(self, request):
		"""
		Check if user can access the admin site
		"""
		return request.user.is_authenticated and request.user.is_admin

	def login(self, request, extra_context=None):
		"""
		Redirect to API Login and Check Permissions
		"""
		# Login if needed
		if not request.user.is_authenticated:
			url = reverse('login') + '?redirection=' + request.get_full_path()
			return redirect(url)

		# Check if allowed to login to the admin site
		if self.has_permission(request):
			return redirect(request.GET.get('next', 'admin'))
		else:
			return redirect('root')

	def logout(self, request, extra_context=None):
		"""
		Redirect to API Logout
		"""
		return redirect('logout')
