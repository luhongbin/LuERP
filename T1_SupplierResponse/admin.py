from django.contrib import admin
#from daterange_filter.filter import DateRangeFilter
from django.http import HttpResponseRedirect
#from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from common import utility
#from T1_SupplierResponse import models
from .models import pmdn_t,pmdl_t,ooag_t,pmaal_t,imaal_t,pmdo_t,oofc_t
import datetime
from django.contrib import admin, messages
from django import forms
from django.db import connection
from itertools import chain


admin.site.register(pmdo_t)

#admin.site.register(pmdbuc_t)
# Register your models here.
import logging



@admin.register(oofc_t)
class oofc_tAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("ID", "Command",  "HostName", "PostTime", "LoginName") #界面上展示的列，对应Model的字段
    list_display = ("oofccrtdt", "oofc003", "oofcstus", "oofc008", "oofc011", "oofc012") #界面上展示的列，对应Model的字段
    search_fields = list_display
    list_display_links = ('oofccrtdt', 'oofc003')
    #date_hierarchy = 'oofccrtdt'  # 详细时间分层筛选　

@admin.register(ooag_t)
class ooag_t_tAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("ID", "Command",  "HostName", "PostTime", "LoginName") #界面上展示的列，对应Model的字段
    list_display = ("ooagent", "ooag001", "ooag003", "ooag004", "ooag005", "ooag006","ooag007", "ooag011","ooagstus") #界面上展示的列，对应Model的字段
    search_fields =  ('ooag001', 'ooag011')
    date_hierarchy = 'ooagmoddt'  # 详细时间分层筛选　
    list_display_links = ('ooag001',)
    #list_per_page = 20
#admin.site.register(ooag_t,ooag_t_tAdmin)
@admin.register(pmaal_t)

    #list_per_page = 20
class pmaal_t_tAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("ID", "Command",  "HostName", "PostTime", "LoginName") #界面上展示的列，对应Model的字段
    list_display = ("pmaal001", "pmaal002", "pmaal003", "pmaal004", "pmaalent") #界面上展示的列，对应Model的字段
    list_per_page = 20
    #list_editable = ['machine_room_id', 'temperature']
    # 设置哪些字段可以点击进入编辑界面
    #list_display_links = ('id', 'caption')
    search_fields =  ('pmaal002', 'pmaal001')
class BookInline(admin.TabularInline):
    model = pmdn_t
@admin.register(pmdl_t)
class pmdl_t_tAdmin(admin.ModelAdmin):
    list_select_related = True

    def get_queryset(self, request):
        """函数作用：使当前登录的用户只能看到自己负责的服务器"""
        qs = super(pmdl_t_tAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs#qs.filter(user=UserInfo.objects.filter(user_name=request.user))

    model_icon = 'fa  fa-home'
    list_display = ("pmdldocno", "pmdldocdt", "pmdlstus", "pmdl004", "pmdl002", "pmdl005", "pmdl044") #界面上展示的列，对应Model的字段
    search_fields =  ('pmdldocdt', 'pmdldocno')
    readonly_fields = ["pmdldocdt", "pmdldocno", "pmdlstus"]
    date_hierarchy = 'pmdldocdt'  # 详细时间分层筛选　
    #list_filter = ('pmdlstus', 'pmdl005' )
    fk_fields = ('pmdl002',)
    #list_filter = ('pmdlstus', 'pmdl005',('pmdldocdt', DateRangeFilter), )
    list_filter = ('pmdlstus', 'pmdl005',('pmdldocdt'), )
    inlines = [
        BookInline,
    ]

#admin.site.register(models.pmdbuc_t, pmdbuc_tAdmin)  # 注册报警日志到后台管理


@admin.register(imaal_t)
class imaal_tAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("ID", "Command",  "HostName", "PostTime", "LoginName") #界面上展示的列，对应Model的字段
    list_display = ("imaal001", "imaal003",  "imaal004", "imaalent") #界面上展示的列，对应Model的字段
    #list_filter = ('sn', 'action', "Country", 'creatdate') #带链接可点击的字段，点击会进入编辑界面
    search_fields = ('imaal001', 'imaal003')

@admin.register(pmdn_t)
class pmdn_tAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("pmdnseq", 'pmdn001') #界面上展示的列，对应Model的字段
    list_display = ("pmdn002","pmdnseq", "pmdn001", 'pmdn012', 'pmdn005',"pmdn007", "pmdn006", "pmdn015", "pmdn045", "pmdn020") #界面上展示的列，对应Model的字段
    #list_filter = ('sn', 'action', "Country", 'creatdate') #带链接可点击的字段，点击会进入编辑界面
    search_fields =  ('pmdn002', 'pmdn001')

class pmdn_tAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("pmdnseq", 'pmdn001') #界面上展示的列，对应Model的字段
    list_display = ("pmdn002","pmdnseq", "pmdn001", 'pmdn012', 'pmdn005',"pmdn007", "pmdn006", "pmdn015", "pmdn045", "pmdn020") #界面上展示的列，对应Model的字段
    #list_filter = ('sn', 'action', "Country", 'creatdate') #带链接可点击的字段，点击会进入编辑界面
    search_fields =  ('pmdn002', 'pmdn001')

#admin.site.register(pmdn_t,pmdn_tAdmin)  # 注册报警日志到后台管理

LOG = logging.getLogger("boss")

