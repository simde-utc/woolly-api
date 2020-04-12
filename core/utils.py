from rest_framework.renderers import BrowsableAPIRenderer as BaseAPIRenderer
from django.conf import settings

import os
import qrcode
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template

import logging

logger = logging.getLogger(f"woolly.{__name__}")


class BrowsableAPIRenderer(BaseAPIRenderer):
	"""
	Renders the Browsable API with or without forms
	"""
	def get_rendered_html_form(self, *args, **kwargs):
		if settings.BROWSABLE_API_WITH_FORMS:
			return super().get_rendered_html_form(*args, **kwargs)
		else:
			return None

	def get_context(self, *args, **kwargs):
			ctx = super().get_context(*args, **kwargs)
			ctx['display_edit_forms'] = settings.BROWSABLE_API_WITH_FORMS
			return ctx


# ===============================================================================
# 		PDF & QR Code utils
# ===============================================================================

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=fetch_assets)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

def fetch_assets(uri, rel):
	"""
	Callback to allow xhtml2pdf/reportlab to retrieve Images,Stylesheets, etc.
	`uri` is the href attribute from the html link element.
	`rel` gives a relative path, but it's not used here.
	"""
	if settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
		path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
	elif settings.STATIC_URL and uri.startswith(settings.STATIC_URL):
		path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
	if not os.path.exists(path):
		for d in settings.STATICFILES_DIRS:
			path = os.path.join(d, uri.replace(settings.STATIC_URL, ""))
			if os.path.exists(path):
				break
	elif uri.startswith("http://") or uri.startswith("https://"):
		path = uri
	return path

def data_to_qrcode(data):
	""" Return a qrcode image from data """
	# Add border to improve readability
	qrc = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q,
						box_size=8,
						border=2)

	# Remove all - in uuid to comply to Weezevent
	qrc.add_data(str(data).replace("-", ""))
	qrc.make(fit=True)
	return qrc.make_image()
