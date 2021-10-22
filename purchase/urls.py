from django.conf.urls import include, url, static,re_path
import purchase.views

#
# urlpatterns = [
# 	path('', views.index, name='index'),
#
#     #url('', include('views.urls')),
# ]
from django.urls import path

from . import views

urlpatterns = [
    # url(r'^purchase', include('purchase.urls')),
    re_path(r"^deliverynote/(?P<object_id>\d+)", purchase.views.printbill),
    re_path(r"^deliverynote/(?P<object_id>\d+)/pbillid", purchase.views.printbillid),

    #path('', views.index, name='index'),
]
#from django.conf.urls import url
# from Areas import views
#
# app_name = 'Areas'
# urlpatterns = [
#     url(r'^choose/province/$', views.choose_province),
#     url(r'^choose/city/$', views.choose_city),
#     url(r'^choose/area/$', views.choose_area),
# ]