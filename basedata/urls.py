from django.conf.urls import include, url,static
import basedata.views

urlpatterns = [
    url("dataimport/(?P<object_id>\d+)/action", basedata.views.action_import),

]
