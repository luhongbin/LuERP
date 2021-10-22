from django.contrib import admin
from .models import appalarmset,getsmm

@admin.register(getsmm)
class getsmmAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("ID", "Command",  "HostName", "PostTime", "LoginName") #界面上展示的列，对应Model的字段
    list_display = ("creatdate", "name", "price","aver","today") #界面上展示的列，对应Model的字段
    list_filter = ('name',) #带链接可点击的字段，点击会进入编辑界面
    search_fields = ('name', 'price')
    date_hierarchy = 'creatdate'  # 详细时间分层筛选　
    ordering = ['-creatdate']

@admin.register(appalarmset)

class appalarmsetAdmin(admin.ModelAdmin):
    model_icon = 'fa  fa-home'
    #list_display = ("ID", "Command",  "HostName", "PostTime", "LoginName") #界面上展示的列，对应Model的字段
    list_display = ("sn","devname","mobname", "action", "mobtype", "Country", "creatdate","password") #界面上展示的列，对应Model的字段
    list_filter = ('action','mobid','mobtype',) #带链接可点击的字段，点击会进入编辑界面
    search_fields = ('sn', 'action', "Country", 'devname')
    date_hierarchy = 'creatdate'  # 详细时间分层筛选　
    ordering = ['-creatdate']
    fieldsets = [
        ('动作信息', {'fields': ['sn', 'snid','action','creatdate', 'password']}),
        ('基本信息', {'fields': ["devname","mobname",'mobtype', 'mobver', 'mobid','mobidver','uuid','firmver']}),
        ('详细信息', {'fields': ["longitude", "latitude", "speed", "altitude"]})
    ]
    def get_readonly_fields(self, request, obj=None):
        # black5.view_ad_campaing  black5 为app名字
        if not request.user.is_superuser and request.user.has_perm('appalarmset.view_appalarmset'):
            return [f.name for f in self.model._meta.fields]

# Register your models here.
