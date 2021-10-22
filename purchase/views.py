from django.shortcuts import render_to_response
from django.http import JsonResponse
from django.http import HttpResponse
# from django.views.generic import TemplateView
from purchase.models import deliverynote,deliveryitem,factoryaddr
from django.http import StreamingHttpResponse
# coding=utf-8
from django.contrib.admin import site
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
import os

def hello(c):
    c.drawString(100, 100, "Hello World")

def printbill(request,object_id):
    """
    入库操作
    :param request:
    :param object_id:
    :return:id=int(object_id)
    """
    print('testasdfasd',object_id)
    title = "你确认？"
    obj = deliverynote.objects.get()
    opts = obj._meta
    objects_name = force_text(opts.verbose_name)
    print('XXXok')


    print('asdfasdfsdfasdfasdf',os.getcwd())
    c = canvas.Canvas("hello.pdf")
    filename="hello.pdf"
    hello(c)
    c.showPage()
    c.save()
    # obj.test(request)

    def file_iterator(filename, chuck_size=512):
        with open(filename, "rb") as f:
            while True:
                c = f.read(chuck_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(filename))

    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{}"'.format("hello.pdf")
    # return response
    print('UUUUUok')
    #
    #
    return render_to_response('admin/readpdf.html', {})
    # return TemplateResponse(request,'admin/readpdf.html', {'filename': filename})


def printbillid(request,object_id):
    """
    入库操作
    :param request:
    :param object_id:
    :return:id=int(object_id)
    """
    title = "你确认？"
    obj = deliverynote.objects.get()
    opts = obj._meta
    objects_name = force_text(opts.verbose_name)



