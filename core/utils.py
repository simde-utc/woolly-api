import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import HorizontalBarChart

from woolly_api import settings
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template


def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=fetch_resources)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


# ===============================================================================
# HELPERS
# ===============================================================================
def fetch_resources(uri, rel):
	"""
	Callback to allow xhtml2pdf/reportlab to retrieve Images,Stylesheets, etc.
	`uri` is the href attribute from the html link element.
	`rel` gives a relative path, but it's not used here.
	"""
	if settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
		path = os.path.join(settings.MEDIA_ROOT,
							uri.replace(settings.MEDIA_URL, ""))
	elif settings.STATIC_URL and uri.startswith(settings.STATIC_URL):
		path = os.path.join(settings.STATIC_ROOT,
							uri.replace(settings.STATIC_URL, ""))
	if not os.path.exists(path):
		for d in settings.STATICFILES_DIRS:
			path = os.path.join(d, uri.replace(settings.STATIC_URL, ""))
			if os.path.exists(path):
				break
	elif uri.startswith("http://") or uri.startswith("https://"):
		path = uri
	return path


class MyBarcodeDrawing(Drawing):
	def __init__(self, text_value, *args, **kw):
		barcode = createBarcodeDrawing('Code128', value=text_value, barHeight=10 * mm, humanReadable=True)
		Drawing.__init__(self, barcode.width, barcode.height, *args, **kw)
		self.add(barcode, name='barcode')


if __name__ == '__main__':
	# use the standard 'save' method to save barcode.gif, barcode.pdf etc
	# for quick feedback while working.
	MyBarcodeDrawing("HELLO WORLD").save(formats=['gif', 'pdf'], outDir='.', fnRoot='barcode')