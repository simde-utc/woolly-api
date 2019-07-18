from django.contrib.admin.apps import AdminConfig as DefaultAdminConfig
from django.contrib.admin import AdminSite as DefaultAdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib import auth as django_auth

from django.http import HttpResponseNotFound, HttpResponseForbidden
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
		Try login user, redirect to API Login if needed
		and check Permissions
		There is no form
		"""
		# Try to authenticate from session directly as there is no form
		user = django_auth.authenticate(request)

		# No user in session, redirect to API Login
		if not user:
			url = reverse('login') + '?redirection=' + request.get_full_path()
			return redirect(url)

		# Login user from backend
		request.user = user
		django_auth.login(request, user)

		# Check if allowed to access to the admin site
		if self.has_permission(request):
			return redirect(request.GET.get('next', 'admin:index'))
		else:
			return HttpResponseForbidden()

	def logout(self, request, extra_context=None):
		"""
		Redirect to API Logout
		"""
		return redirect('logout')

	def password_change(self, request, extra_context=None):
		"""No password change"""
		return HttpResponseNotFound()

	def password_change_done(self, request, extra_context=None):
		"""No password change"""
		return HttpResponseNotFound()
