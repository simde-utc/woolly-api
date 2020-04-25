import os
from io import BytesIO
from base64 import b64encode

from rest_framework.renderers import BrowsableAPIRenderer as BaseAPIRenderer
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_Q


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


# --------------------------------------------
#   Tickets
# --------------------------------------------

def link_asset(uri: str) -> str:
    """
    Callback to allow xhtml2pdf/reportlab to retrieve Images,Stylesheets, etc.
    `uri` is the href attribute from the html link element.
    """
    if settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif settings.STATIC_URL and uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))

    if not os.path.exists(path):
        for folder in settings.STATICFILES_DIRS:
            path = os.path.join(folder, uri.replace(settings.STATIC_URL, ""))
            if os.path.exists(path):
                return path
    elif uri.startswith("http://") or uri.startswith("https://"):
        return uri
    return path


def render_to_pdf(template_src: str, context_dict: dict={}) -> HttpResponse:
    html = get_template(template_src).render(context_dict)

    pdf_buffer = BytesIO()
    html_buffer = BytesIO(html.encode('UTF-8'))
    pdf = pisa.pisaDocument(html_buffer, pdf_buffer, link_callback=link_asset)

    if not pdf.err:
        return HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    return None


def base64_qrcode(data: str) -> str:
    """
    Return a qrcode image from data
    """
    # Add border to improve readability
    qr_code = QRCode(error_correction=ERROR_CORRECT_Q, box_size=8, border=2)
    qr_code.add_data(data)
    qr_code.make(fit=True)

    image_buffer = BytesIO()
    qr_code.make_image().save(image_buffer)
    return b64encode(image_buffer.getvalue()).decode('utf-8')
