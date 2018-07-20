from django.conf.urls import url


from . import views # import views so we can use them in urls.


urlpatterns = [

    url(r'^payutc/createTransaction', views.createTransaction), # "/store" will call the method "index" in "views.py"
    url(r'^payutc/getTransactionInfo', views.getTransactionInfo),
    url(r'^payutc/getFundations', views.getFundations), # "/store" will call the method "index" in "views.py"
    url(r'^payutc/returnTransaction', views.returnTransaction), # "/store" will call the method "index" in "views.py"

]
