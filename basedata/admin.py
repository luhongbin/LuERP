# coding=utf-8
#from admin_totals.admin import ModelAdminTotals
from django.contrib import admin,messages
from django.forms import fields, TextInput, Textarea,models,ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from common import generic
from basedata.models import ValueList,ValueListItem,Address,Partner,BankAccount,Project,Measure,Material,Brand,\
    Category,Warehouse,TechnicalParameterName,TechnicalParameterValue,Trade,ExpenseAccount,Employee,Family,Education,\
    WorkExperience,ExtraParam,DataImport,Document,apca_t,Pmdnlog,Pmdnt200,pmdg,pmdgfile,ApbacodeSummary
from purchase.models import factoryaddr
from common.generic import apba_t,week_pmdnt200,code_pmdnt200,code_apba
from django import forms
from django.http import HttpResponseRedirect
from .forms import SetTypeForm
from django.shortcuts import render,HttpResponse,redirect
#from daterange_filter.filter import DateRangeFilter
import cx_Oracle
import xlwt
from io import BytesIO
from django.db.models import Sum, Q, Count, DateTimeField,DateField,Min,Max
import time,os,datetime
from django.utils.text import capfirst
from collections import OrderedDict as SortedDict
from django.views.generic import ListView
from import_export import resources
from import_export.admin import ImportExportModelAdmin,ImportExportActionModelAdmin
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.db.models.functions import ExtractYear, ExtractMonth,ExtractWeek,ExtractDay

def find_model_index(name):
    count = 0
    for model, model_admin in admin.site._registry.items():
        if capfirst(model._meta.verbose_name_plural) == name:
            return count
        else:
            count += 1
    return count


def index_decorator(func):
    def inner(*args, **kwargs):
        template_response = func(*args, **kwargs)
        for app in template_response.context_data['app_list']:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return template_response

    return inner


registry = SortedDict()
registry.update(admin.site._registry)
admin.site._registry = registry
admin.site.index = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)
from django.db.models.functions import Coalesce
from django.db import connection
from django.core.exceptions import ValidationError

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'



class pmdgForm(ModelForm):
    def clean_pmdgua007(self):
        value = self.cleaned_data.get('pmdgua006')
        value1 = self.cleaned_data.get('pmdgua007')
        if value == 1:
            if value1 is None:
                raise ValidationError("必须输入正确的产品报价含税")
                return self.cleaned_data.get('pmdgua007')
            if value1 <= 0:
                raise ValidationError("必须输入正确的产品报价含税")
                return self.cleaned_data.get('pmdgua007')
        return value1


    def clean_attach1(self):
        content = self.cleaned_data['attach1']
        # print('update:',content.size)
        if content is None:
            return

        # content_type = content.content_type.split('/')[0]
        # if content_type in settings.CONTENT_TYPES:
        if content.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('文件必须小于 %s. 当前文件大小 %s' % (
            filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        # else:
        #     raise forms.ValidationError(_('File type is not supported'))
        return content
    def clean_attach2(self):
        content = self.cleaned_data['attach2']
        if content is None:
            return
        if content.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('文件必须小于 %s. 当前文件大小 %s' % (
            filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content

    def clean_attach3(self):

        content = self.cleaned_data['attach3']
        if content is None:
            return
        if content.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('文件必须小于 %s. 当前文件大小 %s' % (
            filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content

    def clean_pmdgud013(self):

        value = self.cleaned_data.get('pmdgua006')
        value2 = self.cleaned_data.get('pmdgud013')

        if value2 is None:
            value2=0
        if value == 2:
            if value2 <= 0:
                raise ValidationError("必须输入理论重量首次报价[按g]" )
                return self.cleaned_data.get('pmdgud013')
        return value2
    class Meta:
        model = pmdg
        exclude = ("id",)

class  pmdgInline(admin.StackedInline):#TabularInline
    model = pmdgfile
    fields = ('attach',)
    extra=0
    #max_num = 5
    def get_readonly_fields(self,request, obj=None, instance_obj=None):
        print(obj.status)
        if obj.status == '2'  or obj.status == '3' :
            return ['attach',]
        return []
    def has_add_permission(self, request, obj=None):
        if obj.status == '2' or obj.status == '3':
            return False
        if request.user.username==obj.pmdf002:
            return False
        return True

    def clean_attach(self):
        content = self.cleaned_data['attach']
        print(content.size)
        if content is None:
            return
        if content.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('文件必须小于 %s. 当前文件大小 %s' % (
            filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))


    # def latest_comments(self, obj):
    #     return '<br/>'.join(c.title for c in obj.pmdgfile_set.order_by('-.title')[:3])
    #
    # latest_comments.allow_tags = True

def get_t10():
    import psycopg2.extras
    import cx_Oracle
    DBNAME1 = 'CIMS'
    DBHOST1 = '192.168.0.2'
    DBUSER1 = 'openpg'
    DBPASS1 = 'openpgpwdlhb'
    DBPORT1 = 5432
    my_sender = 'system@umenb.com'  # 发件人邮箱账号
    my_pass = 'seqhsqumamnxcafa'  # 发件人邮箱密码(当时申请smtp给的口令)

    conn1 = psycopg2.connect(
        "host=%s port=%s dbname=%s user=%s password=%s" % (DBHOST1, DBPORT1, DBNAME1, DBUSER1, DBPASS1))
    openpg = conn1.cursor()
    conn2 = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
    cur = conn2.cursor()

    ##########从T100询价单中获取数据转让POSTGRESQL
    #xxx = "select pmdgsite 公司别,pmdgdocno 询价单号,pmdgseq 项次,decode(pmdg001,'Y','外加工','采购') 属性,pmdg002 供应商编号,pmaal004 供应商简称,pmdg003 品号,imaal003 品名,imaal004 规格,pmdgua006 报价分类, pmdg007 询价数量,pmdg008 询价单位,pmdg009 分量计价否,pmdg011 税率,pmdgud014 最小包装量,pmdg013 最低采购量,pmdgua007 产品报价含税,pmdgud013 理论重量首次报价,pmdgud012 模具费报价含税,pmdg017 有效日期,pmdg030 计价公式及备注,pmdf002 工号,ooag011 姓名,pmdgud017,pmdgud005,pmdgud018,pmdgud019,pmdgud020 from dsdata.pmdg_t left join dsdata.pmdf_t on pmdfent=pmdgent and pmdfdocno=pmdgdocno left join dsdata.pmaal_t on pmaalent=pmdgent and pmaal001=pmdg002 and pmaal002='zh_CN' left join dsdata.imaal_t on imaal001 =pmdg003 and imaalent=pmdgent  and imaal002='zh_CN' left join dsdata.ooag_t  on pmdf002=ooag001 and ooagent=pmdgent where pmdgent ='60' and  pmdfstus='N' and pmdg003 is not null and pmdg002 is not null and pmdfud002='Y'"
    xxx = "select pmdgsite 公司别,pmdgdocno 询价单号,pmdgseq 项次,decode(pmdg001,'Y','外加工','采购') 属性,pmdg002 供应商编号,pmaal004 供应商简称,pmdg003 品号,imaal003 品名,imaal004 规格,pmdgua006 报价分类, pmdg007 询价数量,pmdg008 询价单位,pmdg009 分量计价否,pmdg011 税率,pmdgud014 最小包装量,pmdg013 最低采购量,pmdgua007 产品报价含税,pmdgud013 理论重量首次报价,pmdgud012 模具费报价含税,pmdg017 有效日期,pmdg030 计价公式及备注,pmdf002 工号,ooag011 姓名,pmdgud017,pmdgud005,pmdgud018,pmdgud019,pmdgud020,imaa016 毛重,imaaua113 抗UV ,imaaua114 阻燃等级 ,imaaua142 材质要求 from dsdata.pmdg_t left join dsdata.pmdf_t on pmdfent=pmdgent and pmdfdocno=pmdgdocno left join dsdata.pmaal_t on pmaalent=pmdgent and pmaal001=pmdg002 and pmaal002='zh_CN' left join dsdata.imaal_t on imaal001 =pmdg003 and imaalent=pmdgent  and imaal002='zh_CN' left join dsdata.ooag_t  on pmdf002=ooag001 and ooagent=pmdgent  left join dsdata.imaa_t on imaa001 =pmdg003 and imaaent=pmdgent  where pmdgent ='60' and  pmdfstus='N' and pmdg003 is not null and pmdg002 is not null and pmdfud002='Y'"
    cur.execute(xxx)
    res = cur.fetchall()
    for tao in res:
        r0 = tao[0]
        if r0 == 'Y1':
            r0 = 'Y1-耀泰'
        if r0 == 'Y3':
            r0 = 'Y3-颐道'
        r1 = tao[1]
        r2 = str(tao[2])
        print(r0, r1, r2)
        r4 = tao[4]
        r3 = tao[3]
        r5 = tao[5]
        r6 = tao[6]
        r7 = tao[7]
        if r7 is None:
            r7 = ''
        r8 = tao[8]
        if r8 is None:
            r8 = ''
        r9 = tao[9]
        if r9 is None:
            r9 = 1
        if r9 == '0':
            r9 = 1
        else:
            r9 = 2

        sql = "select pmdgsite from  basedata_pmdg  where  pmdgsite=('%s') and pmdgdocno=('%s') and  pmdgseq=('%s')  and  pmdg002=('%s')" % (
        r0, r1, r2, r4)
        openpg.execute(sql)
        # conn1.commit()  # 执行插入
        res = openpg.fetchone()
        if not res:

            sql = "insert into basedata_pmdg (pmdgsite,  pmdgdocno, pmdgseq,pmdg002,status) values ('%s','%s','%s','%s','0')" % (
            r0, r1, r2, r4)
            openpg.execute(sql)
            conn1.commit()  # 执行插入
            # try:
            print("邮件开始")
            sql = "select id from  basedata_pmdg  where  pmdgsite=('%s') and pmdgdocno=('%s') and  pmdgseq=('%s') and  pmdg002=('%s')" % (
                r0, r1, r2, r4)
            openpg.execute(sql)
            # conn1.commit()  # 执行插入
            row = openpg.fetchone()
            if row == None:
                product_id = str(row[0])
            else:
                product_id = str(row[0])
            from email.mime.text import MIMEText
            from email.utils import formataddr
            import smtplib
            sql = "select email from  auth_user  where  username=('%s')" % (r4)
            openpg.execute(sql)
            res = openpg.fetchall()
            for tao1 in res:
                ttx = tao1[0]
                if ttx == None:
                    ttx = ''
                print(ttx)
            my_user = 'finance@lutec.net'  # 收件人邮箱账号，我这边发送给自己
            my_sender = 'system@umenb.com'  # 发件人邮箱账号
            my_pass = 'seqhsqumamnxcafa'  # 发件人邮箱密码(当时申请smtp给的口令)
            try:
                msg = MIMEText(
                    '亲爱的供应商【' + r5 + '】你好：<br><p>我们邀请您使用LUTEC供应商管理平台：</p><p><a href="http://www.umenb.com:8000/admin/basedata/pmdg/' + product_id + '">宁波耀泰(集团)管理平台</a><br>对品名：' + r7 + '，规格：' + r8 + '<br>及时报价。<br><hr>技术支持：宁波耀泰(集团)，<a href=mailto:finance@lutec.net>客服邮箱</a></p>',
                    'html', 'utf-8')
            except Exception:
                print(
                    '亲爱的供应商【' + r5 + '】你好：<br><p>我们邀请您使用LUTEC供应商管理平台：</p><p><a href="http://www.umenb.com:8000/admin/basedata/pmdg/' + product_id + '">宁波耀泰(集团)管理平台</a><br>对品名：' + r7 + '，规格：' + r8 + '<br>及时报价。<br><hr>技术支持：宁波耀泰(集团)，<a href=mailto:finance@lutec.net>客服邮箱</a></p>')
            msg['From'] = formataddr(["发件人昵称", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['Subject'] = "LUTEC供应商平台通知："  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            if len(ttx) > 5:
                my_user = my_user + ';' + ttx
            else:
                msg = MIMEText('供应商【' + r4 + '】邮箱不存在，请T100修改邮箱后，手动发送邮件给供应商登录平台</p>', 'html', 'utf-8')
            msg['To'] = formataddr(["收件人昵称", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
            print('email ok')

            r10 = tao[10]
            r11 = tao[11]
            r12 = tao[12]
            r19 = tao[19].strftime("%Y%m%d")
            r20 = tao[20]
            r21 = tao[21]
            r22 = tao[22]
            r23 = tao[23]
            if r23 is None:
                r23 = 0
            r24 = tao[24]
            r25 = tao[28]
            r26 = tao[26]
            r27 = tao[27]
            r28 = tao[28]
            if r28 is None:
                r28 = ''
            r29 = tao[29]
            if r29 is None:
                r29 = ''
            r30 = tao[30]
            if r30 is None:
                r30 = ''
            r23=r30.strip() + ',' + r29.strip() + ','+ r28.strip()
            print(r19, r20, r21, r22, r23, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r0, r1, r2)
            sql = "update basedata_pmdg set pmdg008=('%s'), pmdg009=('%s'), pmdg001=('%s'),  pmaal004=('%s'), pmdg003=('%s'), imaal003=('%s'), imaal004=('%s'), pmdgua006=('%d'), pmdg007=('%f'), pmdg017=('%s'),  pmdg030=('%s'), pmdf002=('%s'), ooag011=('%s'),pmdgud017=('%d'),pmdgud005=('%s'),pmdgud018=('%f'),pmdgud019=('%f'),pmdgud020=('%f')  WHERE pmdgsite=('%s') and pmdgdocno=('%s') and  pmdgseq=('%s')  and  pmdg002=('%s')" % (
            r11, r12, r3, r5, r6, r7, r8, r9, r10, r19, r20, r21, r22, r23, r24, r25, r26, r27, r0, r1, r2, r4)
            openpg.execute(sql)
            conn1.commit()  # 执行插入

            r13 = tao[13]
            r14 = tao[14]
            r15 = tao[15]
            r16 = tao[16]
            r17 = tao[17]
            r18 = tao[18]
            if r13 is None:
                r13 = 0
            if r14 is None:
                r14 = 0
            if r15 is None:
                r15 = 0
            if r16 is None:
                r16 = 0
            if r17 is None:
                r17 = 0
            if r18 is None:
                r18 = 0
            print(r13, r14, r15, r16, r17, r18)
            sql = "update basedata_pmdg set creator=pmdf002,pmdg011=('%f'), pmdgud014=('%d'), pmdg013=('%d'), pmdgua007=('%f'), pmdgud013=('%f'), pmdgud012=('%f') WHERE pmdgsite=('%s') and pmdgdocno=('%s') and  pmdgseq=('%s')  and  pmdg002=('%s')" % (
            r13, r14, r15, r16, r17, r18, r0, r1, r2, r4)
            openpg.execute(sql)
            conn1.commit()
@admin.register(pmdg)

class pmdgAdmin(generic.BOAdmin):
    CODE_PREFIX = 'XJD'

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    list_display = ['pmdgsite','pmaal004','short_name','pmdgua006','pmdgua007','pmdgud012','status','pmdg017','ooag011','creation'] #,,'pmdg001','pmdg002','pmdgdocno','pmdgseq'
    list_display_links = ['pmaal004']
    search_fields = list_display
    ordering = ['status','-creation']

    list_filter = ['ooag011','pmdgsite','status']
    fieldsets = [
        ('不可修改信息', {'fields': [('pmdg001',  'pmdg003', 'imaal003','imaal004',),( 'pmdg011', 'pmdg007', 'pmdg008', 'pmdgud020', 'pmdgud005')]}),
        #('采购员填写', {'fields': [ 'pmdgud011', 'pmdgud015']}),#('attach1','attach2','attach3'),,'pmdgud019'
        ('供应商填写', {'fields': ['pmdgua006',('pmdg009','pmdgua007','pmdgud017','pmdgud014','pmdgud018','pmdgud012',),('pmdguaqt','pmdgud013'),'pmdg030']})]
    radio_fields = {'pmdgua006':admin.HORIZONTAL}
    date_hierarchy = 'pmdg017'
    inlines = [pmdgInline]
    form = pmdgForm

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if request.user.username==obj.pmdf002:
            # if obj.status=='1' or obj.status=='0':'pmdgua007',
                return ['pmdg001', 'pmdg003','pmdgud020','pmdgud005','imaal003','imaal004','pmdg011', 'pmdg007','pmdg008','pmdgua006','pmdgud018','pmdgud019','pmdg009','pmdgud017','pmdgud014','pmdgud013','pmdgud012','pmdg030', 'pmdgud011', 'pmdgud015']
            # else:
            #     return ['pmdg001', 'pmdg003','pmdgud020','pmdgud005','imaal003','imaal004','pmdg011', 'pmdg007','pmdg008','pmdgua006','pmdgud018','pmdgud019','pmdg009','pmdgud017','pmdgud014','pmdg013','pmdgua007','pmdgud013','pmdgud012','pmdg030','attach1','attach2','attach3','attach']
        else:
            # if obj.status=='1' or obj.status=='0':,'pmdgua007'
                return ['pmdg001', 'pmdg003','imaal003','imaal004','pmdg011','pmdg007','pmdg008','pmdgud020','pmdgud005','attach1','attach2','attach3', 'pmdgud011', 'pmdgud015']
            # else:
            #     return ['pmdg001', 'pmdg003','pmdgud020','pmdgud005','imaal003','imaal004','pmdg011', 'pmdg007','pmdg008','pmdgua006','pmdgud018','pmdgud019','pmdg009','pmdgud017','pmdgud014','pmdg013','pmdgua007','pmdgud013','pmdgud012','pmdg030','attach1','attach2','attach3', 'pmdgud011', 'pmdgud015','attach']

    def get_queryset(self, request):
        get_t10()
        pmdg = super().get_queryset(request)
        if request.user.is_superuser:
            return pmdg
        if request.user.username[:1] == 'Y':
            return pmdg #.filter(pmdf002=request.user.username)
        else:
            return pmdg.filter(pmdg002=request.user.username)#.exclude(status__lt ='1')

    def save_model(self, request, obj, form, change):
        if form.is_valid():  # 更改的时候
            super(pmdgAdmin, self).save_model(request, obj, form, change)
            if obj.pmdgud013 > 0:
                if obj.pmdguaqt is None:
                    obj.pmdguaqt=0
                ttt = obj.pmdguaqt + obj.pmdgud018 * obj.pmdgud013
                print('obj.pmdgua006',obj.pmdgua006,obj.pmdguaqt,obj.pmdgud018,obj.pmdgud013,ttt)
                pmdg.objects.filter(pk=obj.pk).update(pmdgua007=ttt)
            import datetime
            from common.utility import getip

            sdate = obj.pmdg017
            snote = obj.pmaal004+'|'+obj.imaal003+'|'+obj.imaal004+'|'+obj.status
            billno = obj.pmdgdocno+'|'+obj.pmdgseq
            ip, country, subdivision, City = getip(request)
            USER = request.user.username
            USERT = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = {'redate': sdate,
                    'renote': snote,
                    'billno': billno,
                    'ip': ip,
                    'country':country,
                    'prov': subdivision,
                    'city':  City,
                    'action':'供应商询价单',
                    'environ':request.environ.get("HTTP_USER_AGENT"),
                    'reman': USER,
                    'retime': USERT}
            Pmdnlog.objects.create(**data)  # 创建日志

    # return pmdg.filter(Q(pmdg002=request.user.username) | Q(pmdf002=request.user.username))

class SubInputText(forms.TextInput):
    class Media:
        css = {
            'all': ('input.css',)
        }

class Pmdnt200Form(forms.ModelForm):
    class Meta:
        model = Pmdnt200
        fields = ['name', 'spec', 'quan', 'predate']
        widgets = {
            'name': forms.Textarea(attrs={'cols': '20', 'rows': '1'}),
            'spec': forms.Textarea(attrs={'cols': '20', 'rows': '1'}),
            'predate': SubInputText(),
            'quan': forms.RadioSelect,
        }

class ChkListFilter(admin.SimpleListFilter):
    title = '采购单确认'
    parameter_name = 'sdate'

    def lookups(self, request, model_admin):
        return (
            ('0', '交期未确认'),
            ('1', '已确认交期'),
            # ('2', '超期交货'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(sdate__isnull=True)
        if self.value() == '1':
            return queryset.filter(sdate__isnull=False)
        # if self.value() == '2':
        #     return queryset.filter(sdate__gt=predate)

@admin.register(Pmdnt200)
class Pmdnt200Admin(admin.ModelAdmin):
    list_select_related = False
    # form = Pmdnt200Form
    # actions = ['update_pmdnt200']

    # def getlog(self,t100):
    #
    #     t100=super(Pmdnt200, self).get_queryset(request).filter(供方编号=request.user.username[1:]).exclude(采购单别='3399')
    #     for t in range(len(t100)):
    #         cc = t100[t].采购单号序号
    #         t100[t].供方回复交期=t100[t].预交日
    #         t100[t].供方说明 = cc
    #         tlog=Pmdn.objects.all().filter(billno=cc).order_by('retime').distinct()#[0]
    #         if tlog.exists():
    #             for l in tlog:
    #                 t100[t].供方回复交期 = l.redate
    #                 t100[t].供方说明 = l.renote
    #                 #yxhst20190325.objects.filter(采购单号序号=cc).update(**{'供方回复交期':x1, '供方说明':x2})
    #                 # t100[t].save(update_fields=['供方回复交期','供方说明'])
    #                 # t100[t].save()
    #                 print('1123', l.redate,l.renote)
    #     return t100        # return Pmdn.redate
    #
    # getlog.short_description = '供方回复'
    # getlog.allow_tags = True
    # getlog.admin_order_field = '供方回复'

    # 定制Action行为具体方法
    # def ChangeReDate(self, request, queryset):
    #     print(self, request, queryset)
    #     print(request.POST.getlist('_selected_action'))
    #     # XXX=预交日
    #     queryset.update(sdate='p')
    #
    # def print_pmdnt200(self, request, queryset):
    #     for qs in queryset:
    #         print(qs)
    # 导出excel数据
    def export_excel(self, request, queryset):
        # 设置HTTPResponse的类型
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=供应商交期确认.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('order-sheet')

        # 设置文件头的样式,这个不是必须的可以根据自己的需求进行更改
        style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """)
        style_time_s = xlwt.easyxf("""
              font:
                name Microsoft YaHei,
                colour_index black,
                bold off,
                height 200;
              align:
                wrap off,
                vert center,
                horiz center;
              pattern:
                pattern solid,
                fore-colour white;
              borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
              """, num_format_str='YYYY-MM-DD')  # 设置时间格式样式为 2019-03-01
        # 写入文件标题
        sheet.write(0, 0, '采购单号序号', style_heading)
        sheet.write(0, 1, '来源单号', style_heading)
        sheet.write(0, 2, '品号', style_heading)
        sheet.write(0, 3, '品名', style_heading)
        sheet.write(0, 4, '规格', style_heading)
        sheet.write(0, 5, '计量单位', style_heading)
        sheet.write(0, 6, '备注', style_heading)
        sheet.write(0, 7, '采购量', style_heading)
        sheet.write(0, 8, '未交量', style_heading)
        sheet.write(0, 9, '要求到货日', style_heading)
        sheet.write(0, 10, '供方回复到货日', style_heading)
        sheet.write(0, 11, '供方说明', style_heading)

        # 写入数据
        data_row = 1
        for i in queryset:
            sheet.write(data_row, 0, i.billno)
            sheet.write(data_row, 1, i.sbill)
            sheet.write(data_row, 2, i.code)
            sheet.write(data_row, 3, i.name)
            sheet.write(data_row, 4, i.spec)
            sheet.write(data_row, 5, i.unit)
            sheet.write(data_row, 6, i.note)
            sheet.write(data_row, 7, i.quan)
            sheet.write(data_row, 8, i.noquan)
            sheet.write(data_row, 9, i.predate,style_time_s)
            sheet.write(data_row, 10, i.sdate,style_time_s)
            sheet.write(data_row, 11, i.snote)
            data_row = data_row + 1

        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response


    def set_type_action(self, request, queryset):
        # if request.POST.get('post'):
            # form = SetTypeForm(request.POST)
            # if form.is_valid():
                # type = form.cleaned_data['type']
        import datetime
        from common.utility import getip

        for qs in queryset:
            qs.sdate = qs.predate
            qs.save()
            ip, country, subdivision, City = getip(request)
            USER = request.user.username
            USERT = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = {'redate': qs.predate,
                    'renote': '批量',
                    'billno': qs.billno,
                    'ip': ip,
                    'country':country,
                    'prov': subdivision,
                    'city':  City,
                    'action': '采购单交期确认',
                    'environ': request.environ.get("HTTP_USER_AGENT"),
                    'reman': USER,
                    'retime': USERT}
            try:
                Pmdnlog.objects.create(**data)  # 创建日志
            except:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            xxx = "update pmdn_t set pmdnua004=to_date(('%s'),'YYYY-MM-DD'),pmdnua005=('%s'),pmdnua006=sysdate ,pmdnua007=('%s') where pmdndocno||'-'||pmdnseq=('%s')" % (qs.sdate, qs.snote, USER, qs.billno)
            #xxx = "update pmdn_t set pmdnua007=('%s') where pmdndocno||'-'||pmdnseq=('%s')" % (USER, billno)

            cur = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD').cursor()
            cur.execute(xxx)
            cur.execute('commit')
            cur.close
        # 设置友好的修改提示
        message_bit = "%s 张单据的确认日期" % len(queryset)
        self.message_user(request, "%s 已成功更改为要求交货日." % message_bit)

    actions = [set_type_action,export_excel]
    set_type_action.short_description = "批量修改确认交期为要求交货日"
    export_excel.short_description = "导出Excel文件"

        # self.message_user(request, "{0}poems were changed with type:{1}".format(len(queryset), type))
        #     return None
        # else:
        #     return render(request, 'batch_update.html'
        #                   , {'form':
        #             SetTypeForm(
        #                 initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        #                       , 'objects': queryset})

    # 单个类型里面删除操作
    # def get_actions(self, request):
    #     actions = super(Pmdnt200Admin, self).get_actions(request)
    #     if 'hello' in actions:
    #         del actions['hello']
    #     return actions

    # 将print_poem和set_type_action注册到admin中
    #
    # 禁用actions
        # actions = None

    # def update_pmdnt200(modeladmin, request, queryset):
    #     form = None
    #     if 'cancel' in request.POST:
    #         modeladmin.message_user(request, u'已取消')
    #         return
    #     elif 'pmdnt200' in request.POST:
    #         form = modeladmin.pmdnt200_form(request.POST)
    #         if form.is_valid():
    #             pmdnt200 = form.cleaned_data['pmdnt200']
    #             for case in queryset:
    #                 case.pmdnt200 = pmdnt200
    #                 case.save()
    #             modeladmin.message_user(request, "%s 成功修改." % queryset.count())
    #             return HttpResponseRedirect(request.get_full_path())
    #         else:
    #             messages.warning(request, u"请选择待确认的交期")
    #             form = None
    #
    #     if not form:
    #         form = modeladmin.pmdnt200_form(
    #             initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    #     return render(request,'batch_update.html',
    #                               {'objs': queryset, 'form': form, 'path': request.get_full_path(),
    #                                'action': 'update_data_src', 'title': u'批量修改确认交期为预交货日'}
    #                               )

    # update_pmdnt200.short_description = u'批量修改确认交期为预交货日'
    #
    # ChangeReDate.short_description = "用预交期作为回复交期"
    # actions = [ChangeReDate, ]
    #
    # # Action选项都是在页面上方显示
    # actions_on_top = True
    # # Action选项都是在页面下方显示
    # actions_on_bottom = False
    #
    # # 是否显示选择个数
    # actions_selection_counter = True

    # 显示多对多字段
    # 定义一个方法，遍历book的authors，然后用列表返回
    # def show_all_author(self, obj):
    #     return [a.name for a in obj.authors.all()]
    #
    # list_display = ['title', 'publisher', 'show_all_author']  # 用刚刚定义的方法的返回值替换authors的值

    def save_model(self, request, obj, form, change):

        if form.is_valid():  # 更改的时候
            import datetime
            from common.utility import getip
            import cx_Oracle

            sdate = request.POST.get('sdate')#self.model.objects.get(pk=obj.pk).供方回复交期
            snote = request.POST.get('snote')
            billno = obj.billno
            super().save_model(request, obj, form, change)
            ip, country, subdivision, City = getip(request)
            USER=request.user.username
            USERT=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = {'redate': sdate,
                    'renote': snote,
                    'billno': billno,
                    'ip': ip,
                    'country':country,
                    'prov': subdivision,
                    'city':  City,
                    'action':'采购单交期确认',
                    'environ':request.environ.get("HTTP_USER_AGENT"),
                    'reman': USER,
                    'retime': USERT}
            Pmdnlog.objects.create(**data)  # 创建日志
            # xxx = "update pmdn_t set pmdnua004=%s,pmdnua005=%s,pmdnua006=%s,pmdnua007=%s where pmdndocno||'-'||pmdnseq=%s" % (
            #     sdate, snote, USERT, USER, billno)
            xxx = "update pmdn_t set pmdnua004=to_date(('%s'),'YYYY-MM-DD'),pmdnua005=('%s'),pmdnua006=sysdate ,pmdnua007=('%s') where pmdndocno||'-'||pmdnseq=('%s')" % (sdate, snote, USER, billno)
            #xxx = "update pmdn_t set pmdnua007=('%s') where pmdndocno||'-'||pmdnseq=('%s')" % (USER, billno)

            conc=cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
            cur =conc.cursor()
            cur.execute(xxx)
            conc.commit
            cur.close
            conc.close
            cur.execute('commit')

    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100.exclude(bclass='3399').order_by('-ok','zc')
            # return t100#super(yxhst20190325Admin, self).get_queryset(request)
        return t100.filter(Q(sno=request.user.username) | Q(buyercode=request.user.username )).exclude(bclass='3399').order_by('-ok','zc')

    # def get_readonly_fields(self, request, obj=None):
    #     if not request.user.is_superuser and request.user.has_perm('basedata.view_pmdnt200'):
    #         return [f.name for f in self.model._meta.fields]

    def expired(self, ps):
        """自定义列表字段, 根据数据单截止日期和当前日期判断是否过期,并对数据库进行更新"""
        import datetime
        from django.utils.html import format_html
        end_date = ps.sdate
        if ps.ok==True:
            ret = '完成'
            color_code = 'blue'
        elif end_date is None or ps.predate is None:
            ret = '未确认'
            color_code = 'black'
        elif ps.predate >= end_date:
            ret = '准时'
            color_code = 'green'
        else:
            ret = '超期'
            color_code = 'red'
            Pmdnt200.objects.filter(pk=ps.pk).update(is_expired=ret)
        return format_html(
            '<span style="color: {};">{}</span>',
            color_code,
            ret,
        )
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    expired.short_description = '确认状态'

    model_icon = 'fa  fa-home'
    list_display = ("expired","billno",'sbill',"code","short_name","short_spec","unit","note","quan","noquan","short_predate","sdate","snote") #界面上展示的列，对应Model的字段
    save_as_continue = True
    save_on_top = True
    search_fields = ("billno",'sbill',"code","name","spec","unit","note","quan","noquan","predate","sdate","snote")
    list_display_links = ('billno',)
    date_hierarchy = 'sdate'  # 详细时间分层筛选　  采购单号序号
    list_per_page = 1000
#    list_filter = (ChkListFilter,'company','zc', 'sclass','jc', 'buyer', ('predate', DateRangeFilter), )
    list_filter = (ChkListFilter,'company','zc', 'sclass','jc', 'buyer', 'predate', )
    #exclude = ('birth_date',)
    fieldsets = [
        ('确认交期', {'fields': ['sdate', 'snote']}),
        ('基本信息', {'fields': ["buydate","jc",'code', 'name', 'spec', 'quan',"okquan","noquan", 'predate', 'billno',"note"]}),
        ('详细信息', {'fields': ["currenct", "price", "rate", "notex", "tex", "allchash", "sclass", "sbill", "PO", "buyer", "checker", "tao", "company", "sno"]})
    ]
    readonly_fields = ("buydate","jc",'code', 'name', 'spec', 'quan',"okquan","noquan", 'predate', 'billno',"note","currenct", "price", "rate", "notex", "tex", "allchash", "sclass", "sbill", "PO", "buyer", "checker", "tao", "company", "sno")
    list_editable = ['sdate','snote']
    ordering = ['-predate', 'billno']

def __str__(self):
    """返回模型的字符串表示"""
    small_text = self.text[:50]
    if small_text == self.text:
        return self.text
    else:
        return self.text[:50] + "..."

from import_export.fields import Field

class apba_tResource(resources.ModelResource):
#    full_title = Field()
#     def get_export_headers(self):
#         # 是你想要的导出头部标题headers
#         return ['员工号', '员工姓名', '公司名称']
    jhrq = Field(attribute='jhrq', column_name='进货日期')
    paybill = Field(attribute='paybill', column_name='对账单号')
    xc = Field(attribute='xc', column_name='项次')
    cgdh = Field(attribute='cgdh', column_name='采购单号')
    lwmc = Field(attribute='lwmc', column_name='货物劳务名称')
    ggxh = Field(attribute='ggxh', column_name='规格型号')
    sl = Field(attribute='sl', column_name='数量')
    price = Field(attribute='price', column_name='单价')
    dw = Field(attribute='dw', column_name='单位')
    cash = Field(attribute='cash', column_name='金额')
    tax = Field(attribute='tax', column_name='税额')
    slv = Field(attribute='slv', column_name='税率')
    totalcash = Field(attribute='totalcash', column_name='合计')
    jhdh = Field(attribute='jhdh', column_name='进货单号')
    ddhm = Field(attribute='ddhm', column_name='订单号')
    note = Field(attribute='note', column_name='备注')
    gsb = Field(attribute='gsb', column_name='公司别')
    sname = Field(attribute='sname', column_name='供应商简称')
    sno = Field(attribute='sno', column_name='供方编号')


class Meta:
        model = apba_t
        export_order = ("jhrq", "paybill", "xc", "cgdh", "lwmc", "ggxh", "sl", "price", "dw", "cash", "tax", "slv",
                    "totalcash", "jhdh", "ddhm", "note",'gsb', "sname")
@admin.register(apba_t)
class apba_tAdmin(admin.ModelAdmin):#ImportExportActionModelAdmin):
    model_icon = 'fa  fa-home'
    list_display = ("jhrq", "paybill", "xc", "cgdh", "lwmc", "ggxh", "sl", "price", "dw", "rjust_cash", "tax", "slv",
                    "rjust_totalcash", "jhdh", "ddhm", "note",'gsb', "sname") #界面上展示的列，对应Model的字段
    search_fields = list_display
    # fieldsets = [
    #     ('单据信息', {'fields': ['billno','redate', 'renote']}),
    #     ('操作信息', {'fields': [('ip', 'action'),('reman','retime')]}),
    #     ('跟踪信息', {'fields': [ ('country', 'prov', 'city'), 'environ']}),
    # ]
    date_hierarchy = 'jhrq'  # 详细时间分层筛选　  采购单号序号
    ordering = ['-jhrq']
    #list_display_links = ('paybill',)
    list_filter = ('gsb','paybill' )
    resource_class = apba_tResource
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super(apba_tAdmin, self).changelist_view(request, extra_context)

        filtered_query_set = response.context_data["cl"].queryset
        cash = filtered_query_set.aggregate(tot1=Sum('cash'))['tot1']
        tax = filtered_query_set.aggregate(tot2=Sum('tax'))['tot2']
        totalcash = filtered_query_set.aggregate(tot3=Sum('totalcash'))['tot3']
        print('xxxxx',cash,tax,totalcash)
        my_context = {  'cash': cash ,'tax': tax ,'totalcash': totalcash , }
        return super(apba_tAdmin, self).changelist_view(request, extra_context=my_context)

    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100
        return t100.filter(sno=request.user.username)  # .exclude(ok=True)

#        return t100.filter(Q(sno=request.user.username) | Q(cgybm=request.user.username))#.exclude(ok=True)

from import_export.fields import Field

class ApbacodeSummaryResource(resources.ModelResource):
    paybill = Field(attribute='paybill', column_name='对账单号')
    lwmc = Field(attribute='lwmc', column_name='货物劳务名称')
    ggxh = Field(attribute='ggxh', column_name='规格型号')
    sl = Field(attribute='sl', column_name='数量')
    dw = Field(attribute='dw', column_name='单位')
    cash = Field(attribute='cash', column_name='金额')
    tax = Field(attribute='tax', column_name='税额')
    slv = Field(attribute='slv', column_name='税率')
    totalcash = Field(attribute='totalcash', column_name='合计')
    gsb = Field(attribute='gsb', column_name='公司别')


class Meta:
        model = code_apba
        export_order = ("paybill","lwmc", "ggxh", "dw", "sl", "cash", "tax", "totalcash", "gsb")

def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return '日'
    if date_hierarchy + '__month' in request.GET:
        return '日'
    if date_hierarchy + '__year' in request.GET:
        return '周'
    return '月'

@admin.register(ApbacodeSummary)
class ApbacodeSummaryAdmin(ImportExportActionModelAdmin):
    change_list_template = 'admin/basedata/Apbacode_summary_change_list.html'
    date_hierarchy = 'jhrq'
    list_filter = ['ok','sname','gsb','jhdh']
    search_fields =  ['sname','cgdh','lwmc','ggxh','jhdh','ddhm','gsb']
    resource_class = ApbacodeSummaryResource

    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100
            # return t100#super(yxhst20190325Admin, self).get_queryset(request)
        return t100.filter(sno=request.user.username)  # .exclude(ok=True)


    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context,)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
            'total_sl': Sum('sl'),
            'total_tax': Sum('tax'),
            'total_cash': Sum('cash'),
            'total_totalcash': Sum('totalcash'),
            'total_per': Sum('totalcash'),
        }
        # response.context_data['summary'] = list(qs.values('lwmc','ggxh','dw',) .annotate(**metrics) .order_by('-total_totalcash') )
        # return response
        # #
        # if not hasattr(response, 'context_data') or 'cl' not in response.context_data:
        #     return response

        # filtered_query_set = response.context_data["cl"].queryset
        summary_total = dict(qs.aggregate(**metrics))
        summary = list(qs.values('lwmc','ggxh','dw',).annotate(**metrics) .order_by('-total_totalcash'))#totsl=Sum('sl'), tottax=Sum('tax'), tottotalcash=Sum('totalcash'))
        summary_count = len(summary)
        totl = qs.aggregate(tot=Sum('totalcash'))['tot']

        print('total',summary)
        for i in range(len(summary)):
            summary[i]['total_per'] = round(summary[i]['total_per']/totl*100,2)

        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        periodid = period

        from django.db.models.functions import Trunc
        if periodid == '日':
            summary_over_time = qs.annotate(period=Trunc( 'jhrq', 'day',  output_field=DateField(),)).values('period').annotate(total=Sum('totalcash')).order_by('period')
        elif periodid == '月':
            summary_over_time = qs.annotate(period=ExtractMonth('jhrq')).values('period').annotate(total=Sum('totalcash')).order_by('period')
        elif periodid == '周':
            summary_over_time = qs.annotate(period=ExtractWeek('jhrq')).values('period').annotate(total=Sum('totalcash')).order_by('period')
        else:
            summary_over_time = qs.annotate(period=ExtractYear('jhrq')).values('period').annotate(total=Sum('totalcash')).order_by('period')

        summary_range = summary_over_time.aggregate(low=Min('total'), high=Max('total'), )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        print('low:',low,'high',high)
        summary_over_time = [{ 'period': x['period'], 'total': x['total']  or 0,  'pct': ((x['total'] - low) / (high - low)) * 100  if high > low else 0, } for x in summary_over_time]

        # response.context_data['summary_total'] = dict(qs.aggregate(**metrics))
        print('summary_over_time',summary_over_time)
        # return response
        my_context = { 'summary': summary,'summary_total':summary_total,'summary_count':summary_count,'summary_over_time':summary_over_time,'periodid':periodid,}
        return super(ApbacodeSummaryAdmin, self).changelist_view(request, extra_context=my_context)

        # response.context_data['summary_total'] = dict(qs.aggregate(**metrics))
        # print('summary_total',summary_total)
        # return response
        # summary_total = filtered_query_set.annotate(**metrics)#totsl=Sum('sl'), tottax=Sum('tax'), tottotalcash=Sum('totalcash'))
        #
        # my_context = { 'summary_total': summary_total}
        # return super(ApbacodeSummaryAdmin, self).changelist_view(request, extra_context=my_context)
# @admin.register(code_apba)
# class code_apbaAdmin(ImportExportActionModelAdmin):
#     model_icon = 'fa  fa-home'
#     list_display = ("paybill","lwmc", "ggxh", "dw", "sl", "rjust_cash", "tax", "rjust_totalcash", "gsb") #界面上展示的列，对应Model的字段
#     search_fields = list_display
#     # fieldsets = [
#     #     ('单据信息', {'fields': ['billno','redate', 'renote']}),
#     #     ('操作信息', {'fields': [('ip', 'action'),('reman','retime')]}),
#     #     ('跟踪信息', {'fields': [ ('country', 'prov', 'city'), 'environ']}),
#     # ]
#     ordering = ['lwmc']
#     list_filter = ('gsb', 'paybill')
#     resource_class =code_apbaResource
#
#     list_display_links = None
#
#     def has_add_permission(self, request):
#         return False
#     def has_delete_permission(self, request, obj=None):
#         return False
#     def has_change_permission(self, request, obj=None):
#         return False
#
#
#     def get_queryset(self, request):
#         t100 = super().get_queryset(request)
#         if request.user.is_superuser:
#             return t100
#             # return t100#super(yxhst20190325Admin, self).get_queryset(request)
#         return t100.filter(sno=request.user.username)

# from import_export.fields import Field
#
# class apca_tResource(resources.ModelResource):
#     paybill = Field(attribute='paybill', column_name='应付单号')
#     fphm = Field(attribute='fphm', column_name='发票号码')
#     fprq = Field(attribute='fprq', column_name='发票日期')
#     paytj = Field(attribute='paytj', column_name='付款条件')
#     zlts = Field(attribute='zlts', column_name='账期天数')
#     paydate = Field(attribute='paydate', column_name='计划付款日')
#     cash = Field(attribute='cash', column_name='应付/预付金额')
#     note = Field(attribute='note', column_name='备注')
#     sname = Field(attribute='sname', column_name='供应商简称')
#     gsb = Field(attribute='gsb', column_name='公司别')
#     cgy = Field(attribute='cgy', column_name='采购员')
#     zc = Field(attribute='zc', column_name='周次')
#     cgybm = Field(attribute='cgybm', column_name='采购员编码')
#
#
# class Meta:
#         model = apca_t
#         export_order = ("paybill", "fphm",  "fprq","paytj", "zlts", "paydate", "cash", "note",  "sname","gsb","cgy",  "zc","cgybm")

@admin.register(apca_t)
class apca_tAdmin(generic.BOAdmin): #(ModelAdminTotals,ImportExportActionModelAdmin):
    # change_list_template = 'admin/basedata/apca/apca_t_summary_change_list.html'
    context_object_name = 'posts'
    model_icon = 'fa  fa-home'
    list_display = ("paybill", "short_fp",  "fprq","paytj", "zlts", "paydate", "rjust_cash", "note",  "sname","gsb") #, "status", "cgybm","gsb", "cgy"界面上展示的列，对应Model的字段,
    list_totals = [('cash', Sum)]#, ('col_c', Avg)
    search_fields = list_display
    fieldsets = [
        ('发票信息', {'fields': ['paybill','fphm', 'fprq']}),
        ('操作信息', {'fields': [('paytj', 'zlts'),('paydate','cash')]}),
        ('其他信息', {'fields': [ 'note', 'sname', 'gsb', 'status']}),
    ]
    date_hierarchy = 'paydate'  # 详细时间分层筛选　  采购单号序号
    ordering = ['-paydate']
    list_filter = ('ok','gsb','cgy','sname', )


    def changelist_view(self, request, extra_context=None):
        from django.contrib.admin.utils import label_for_field
        response = super(apca_tAdmin, self).changelist_view(request, extra_context)
        filtered_query_set = response.context_data["cl"].queryset
        if not hasattr(response, 'context_data') or 'cl' not in response.context_data:
            return response
        filtered_query_set = response.context_data["cl"].queryset
        total = filtered_query_set.aggregate(tot=Sum('cash'))['tot']

        my_context = {  'total': total  }
        return super(apca_tAdmin, self).changelist_view(request, extra_context=my_context)


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100
            # return t100#super(yxhst20190325Admin, self).get_queryset(request)
        return t100.filter(Q(sno=request.user.username) | Q(cgybm=request.user.username ))#.exclude(ok=True)

from import_export.fields import Field

class code_pmdnt200Resource(resources.ModelResource):
    jc = Field(attribute='jc', column_name='供应商')
    code = Field(attribute='code', column_name='品号')
    name = Field(attribute='name', column_name='名称')
    spec = Field(attribute='spec', column_name='规格')
    unit = Field(attribute='unit', column_name='单位')
    quan = Field(attribute='quan', column_name='数量')
    okquan = Field(attribute='okquan', column_name='已交数量')
    noquan = Field(attribute='noquan', column_name='未完成数量')

class Meta:
        model = code_pmdnt200
        export_order = ("jc","code", "name", "spec", "unit", "quan", "okquan", "noquan")

@admin.register(code_pmdnt200)
class code_pmdnt200Admin(ImportExportActionModelAdmin):
    name_columns_by_row=('供应商','品号','名称','规格','单位','数量','已交数量','未完成数量')

    model_icon = 'fa  fa-home'
    list_display = ("jc","code", "name", "spec", "unit", "quan", "okquan", "noquan") #界面上展示的列，对应Model的字段
    search_fields = list_display

    ordering = ['code']
    list_filter = ('company','jc' )
    resource_class = code_pmdnt200Resource

    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100
        return t100.filter(sno=request.user.username)


from import_export.fields import Field

class week_pmdnt200Resource(resources.ModelResource):
    jc = Field(attribute='jc', column_name='供应商')
    zc = Field(attribute='zc', column_name='周次')
    code = Field(attribute='code', column_name='品号')
    name = Field(attribute='name', column_name='名称')
    spec = Field(attribute='spec', column_name='规格')
    unit = Field(attribute='unit', column_name='单位')
    quan = Field(attribute='quan', column_name='数量')
    okquan = Field(attribute='okquan', column_name='已交数量')
    noquan = Field(attribute='noquan', column_name='未完成数量')

    class Meta:
        model = week_pmdnt200
        export_order = ("jc", "zc", "code", "name", "spec", "unit", "quan", "okquan", "noquan")


@admin.register(week_pmdnt200)
class week_pmdnt200Admin(ImportExportActionModelAdmin):
    model_icon = 'fa  fa-home'
    list_display = ("jc","zc", "code", "name", "spec", "unit", "quan", "okquan", "noquan") #界面上展示的列，对应Model的字段
    search_fields = list_display
    # fieldsets = [
    #     ('单据信息', {'fields': ['billno','redate', 'renote']}),
    #     ('操作信息', {'fields': [('ip', 'action'),('reman','retime')]}),
    #     ('跟踪信息', {'fields': [ ('country', 'prov', 'city'), 'environ']}),
    # ]
    ordering = ['zc','code']
    list_filter = ('company','jc')
    resource_class = week_pmdnt200Resource

    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100
            # return t100#super(yxhst20190325Admin, self).get_queryset(request)
        return t100.filter(sno=request.user.username)

from import_export.fields import Field

class PmdnlogResource(resources.ModelResource):
    billno = Field(attribute='billno', column_name='单号')
    redate = Field(attribute='redate', column_name='日期')
    renote = Field(attribute='renote', column_name='备注')
    retime = Field(attribute='retime', column_name='回复时间')
    reman = Field(attribute='reman', column_name='回复人')
    country = Field(attribute='country', column_name='国家')
    prov = Field(attribute='prov', column_name='省份')
    city = Field(attribute='city', column_name='城市')
    action = Field(attribute='action', column_name='动作')
    environ = Field(attribute='environ', column_name='环境')

    class Meta:
        model = Pmdnlog
        export_order = ("billno", "redate", "renote", "retime", "reman", "ip", "country", "prov",
                    "city", "action", "environ")

@admin.register(Pmdnlog)
class PmdnlogAdmin(ImportExportActionModelAdmin):
    name_columns_by_row=('单号','日期','回复时间','回复人','IP','国家','省份','城市','动作','环境')
    model_icon = 'fa  fa-home'
    list_display = ("billno", "redate", "renote", "retime", "reman", "ip", "country", "prov",
                    "city", "action", "environ") #界面上展示的列，对应Model的字段
    search_fields = list_display
    fieldsets = [
        ('单据信息', {'fields': ['billno','redate', 'renote']}),
        ('操作信息', {'fields': [('ip', 'action'),('reman','retime')]}),
        ('跟踪信息', {'fields': [ ('country', 'prov', 'city'), 'environ']}),
    ]
    date_hierarchy = 'redate'  # 详细时间分层筛选　  采购单号序号
    ordering = ['-retime']
    list_display_links = ('billno',)
    list_filter = ('prov', 'city', )
    resource_class = PmdnlogResource

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100
            # return t100#super(yxhst20190325Admin, self).get_queryset(request)
        return t100.filter(reman=request.user.username)

    # def change_view(self, request, object_id, extra_context=None):
        # if not request.user.is_superuser:
        #     extra_context = extra_context or {}
        #     extra_context['readonly'] = True

        # return super(PmdnlogAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def get_readonly_fields(self, request, obj=None):
        # if not request.user.is_superuser and request.user.has_perm('basedata.view_pmdnlog'):
            return [f.name for f in self.model._meta.fields]

class ValueListItemInline(admin.TabularInline):
    model = ValueListItem
    exclude = ['group_code']
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 3

class ValueListAdmin(generic.BOAdmin):
    CODE_NUMBER_WIDTH = 3
    CODE_PREFIX = 'S'
    list_display = ['code', 'name', 'module', 'status']
    fields = (('code',),('name',),('module',),('status','init','locked',),('locked_by','lock_time',))
    raw_id_fields = ['module']
    readonly_fields = ['locked_by','lock_time']
    inlines = [ValueListItemInline]
    search_fields = ['code','name']

    def save_model(self, request, obj, form, change):
        super(ValueListAdmin,self).save_model(request,obj,form,change)
        obj.valuelistitem_set.update(group_code=obj.code)


class AddressAdmin(generic.BOAdmin):
    list_display = ['address','phone','contacts']
    exclude = ['content_type','object_id','creator','modifier','creation','modification','begin','end']


class AddressInline(GenericTabularInline):
    model = Address
    exclude = ['content_type','object_id','creator','modifier','creation','modification','begin','end']
    extra = 1


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    fields = ['account','title','memo']

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


class PartnerForm(models.ModelForm):
    tax_address = fields.CharField(widget=TextInput(attrs={'size': 119,}),required=False,label="开票地址/电话")
    memo = fields.CharField(widget=Textarea(attrs={'rows':3,'cols':85}),required=False,label="备注")

    class Meta:
        model = Partner
        fields = '__all__'


class PartnerAdmin(generic.BOAdmin):
    list_display = ['code','name','partner_type','level']
    list_display_links = ['code','name']

    fields = (('code','name',),('short','pinyin',),('partner_type','level'),('tax_num','tax_account',),
              ('tax_address',),('contacts','phone',),('memo',),)
    search_fields = ['code','name','pinyin']
    form = PartnerForm
    save_on_top = True
    inlines = [AddressInline,BankAccountInline]

    def get_queryset(self, request):
        if request.user.is_superuser or (request.user.has_perm('basedate.view_all_customer') and request.user.has_perm('basedate.view_all_supplier')):
            return super(PartnerAdmin,self).get_queryset(request)
        elif request.user.has_perm('basedata.view_all_customer'):
            return super(PartnerAdmin, self).get_queryset(request).filter(partner_type='C')
        else:
            return super(PartnerAdmin, self).get_queryset(request).filter(partner_type='S')


# class ProjectForm(models.ModelForm):
#     income = fields.DecimalField(required=False, widget=TextInput(attrs={'readonly': 'true'}))
#     expand = fields.DecimalField(required=False, widget=TextInput(attrs={'readonly': 'true'}))
#
#     class Meta:
#         model = Project
#         fields = '__all__'

class ProjectAdmin(generic.BOAdmin):
    CODE_PREFIX = 'PJ'
    list_display = ['code','name','status','income','expand']
    list_display_links = ['code','name']
    fields = (
        ('code','name',),('short','pinyin',),
        ('partner',),('status','prj_type',),
        ('description',),
        ('budget','income','expand',),('blueprint',),('offer',),('business',),('users',),
    )
    search_fields = ['code','name']
    readonly_fields = ['status']
    raw_id_fields = ['partner']
    filter_horizontal = ['users']
    #form = ProjectForm


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['code','name','location']
    filter_horizontal = ['users']

    def save_model(self, request, obj, form, change):
        super(WarehouseAdmin,self).save_model(request,obj,form,change)
        try:
            code = getattr(obj,'code')
            if not code:
                obj.code = '%s%02d' % ('A',obj.id)
                obj.save()
        except Exception as e:
            self.message_user(request,'ERROR:%s' % e,level=messages.ERROR)


class BrandAdmin(admin.ModelAdmin):
    list_display = ['name','pinyin']


class MeasureAdmin(admin.ModelAdmin):
    list_display = ['code','name','status']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code','name','path']

    def save_model(self, request, obj, form, change):
        super(CategoryAdmin,self).save_model(request,obj,form,change)
        try:
            code = getattr(obj,'code')
            if not code:
                obj.code = '%s%02d' % ('F',obj.id)
                obj.save()
            if obj.parent:
                if obj.parent.path:
                    obj.path = obj.parent.path + '/'+obj.parent.name
                else:
                    obj.path = obj.parent.name
                obj.save()
        except Exception as e:
            self.message_user(request,'ERROR:%s' % e,level=messages.ERROR)


class MaterialForm(models.ModelForm):
    name = fields.CharField(widget=TextInput(attrs={"size":"119"}),label="物料名称")
    spec = fields.CharField(widget=TextInput(attrs={"size":"119"}),required=False,label="规格型号")

    class Mata:
        model = Material
        fields = '__all__'


class ExtraParamInline(admin.TabularInline):
    model = ExtraParam
    fields = ['name','data_type','data_source']

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


class MaterialAdmin(generic.BOAdmin):
    CODE_PREFIX = 'IT'
    CODE_NUMBER_WIDTH = 5
    list_display = ['code','name','spec','tp']
    list_display_links = ['code','name']
    list_filter = ['brand','tp']
    search_fields = ['code','name']
    fields = (
        ('code','barcode'),('name',),('spec',),
        ('brand',),('category',),('status','is_equip','can_sale','is_virtual',),
        ('warehouse',),('tp',),('measure',),('stock_price','purchase_price','sale_price',),
    )
    filter_horizontal = ['measure']
    inlines = [ExtraParamInline]
    form = MaterialForm


class TechParamValueInline(admin.TabularInline):
    model = TechnicalParameterValue


class TechParamNameAdmin(admin.ModelAdmin):
    list_display = ['name','category']
    inlines = [TechParamValueInline]


class TradeAdmin(admin.ModelAdmin):
    list_display = ['code','name','parent']


class ExpenseAdmin(generic.BOAdmin):
    CODE_PREFIX = 'FC'
    list_display = ['code','name','category']
    list_display_links = ['code','name']
    list_filter = ['category']
    search_fields = ['name']


class FamilyForm(models.ModelForm):
    name = fields.CharField(widget=TextInput(attrs={"size":"25"}),label="姓名")
    phone = fields.CharField(widget=TextInput(attrs={"size":"25"}),label="电话")

    class Meta:
        model = Family
        fields = '__all__'


class FamilyInline(admin.TabularInline):
    model = Family
    exclude = ['creator','modifier','creation','modification','begin','end']
    form = FamilyForm
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    exclude = ['creator','modifier','creation','modification']
    extra = 0


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    exclude = ['creator','modifier','creation','modification']
    extra = 1


class EmployeeAdmin(generic.BOAdmin):
    CODE_PREFIX = '1'
    list_display = ['code','name','position','gender','idcard','age','work_age','literacy','phone','email']
    search_fields = ['code','name','idcard','pinyin']
    fieldsets = [
        (None,{'fields':[('code','phone',),('name','pinyin',),('gender','birthday',),('idcard','country',),
                         ('position',),('rank','category'),('status','ygxs',),('workday','startday',)]}),
        (_('other info'),{'fields':[('hometown','address',),('banknum','bankname',),('email','office',),
        ('emergency','literacy',),('religion','marital',),('party','nation',),('spjob','health',),
        ('major','degree',),('tag1','tag2',),('tag3','tag4',),('user',),],'classes':['collapse']}),
    ]
    readonly_fields = ['status','ygxs','rank','category']
    inlines = [FamilyInline,EducationInline,WorkExperienceInline]
    raw_id_fields = ['user']

    def get_queryset(self, request):
        if request.user.is_superuser or request.user.has_perm('basedata.view_all_employee'):
            return super(EmployeeAdmin,self).get_queryset(request)
        else:
            return super(EmployeeAdmin,self).get_queryset(request).filter(user=request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return ['status','ygxs','rank','category','position','user']


class DataImportAdmin(generic.BOAdmin):
    list_display = ['imp_date','title','status']
    list_display_links = ['imp_date','title']
    raw_id_fields = ['content_type']
    readonly_fields = ['status']
    extra_buttons = [{'href':'action','title':"导入"}]

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            obj = DataImport.objects.get(id=object_id)
            if obj.status == '1':
                extra_context = extra_context or {}
                extra_context.update(dict(readonly=True))
        return super(DataImportAdmin,self).changeform_view(request,object_id,form_url,extra_context)


class DocumentForm(models.ModelForm):
    title = fields.CharField(widget=TextInput(attrs={"size":"119"}),label=_("title"))
    keywords = fields.CharField(widget=TextInput(attrs={"size":"119"}),label=_("keywords"))

    class Meta:
        model = Document
        fields = '__all__'


class DocumentAdmin(generic.BOAdmin):
    CODE_PREFIX = 'FD'
    CODE_NUMBER_WIDTH = 4
    list_display = ['code','title','keywords','tp','business_domain','status','creation']
    list_display_links = ['code','title']
    fields = (('code','status',),('title',),('keywords',),('description',),('business_domain','tp',),('attach',))
    readonly_fields = ['status']
    list_filter = ['tp','business_domain']
    search_fields = ['title','keywords','code']
    form = DocumentForm
    actions = ['publish']
    date_hierarchy = 'begin'

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status=='1':
            return ['code','status','title','keywords','description','business_domain','tp','attach',]
        else:
            return ['status']

    def publish(self,request,queryset):
        import datetime
        cnt = queryset.filter(status='0').update(status='1',pub_date=datetime.datetime.now())
        self.message_user(request,u'%s 个文档发布成功'%cnt)

    publish.short_description = _('publish selected %(verbose_name_plural)s')

class factoryaddrAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'address']
    fields = (('code',),('name',),('address',),)
    readonly_fields = list_display

# admin.site.register(Address,AddressAdmin)
admin.site.register(ValueList,ValueListAdmin)
# admin.site.register(Partner,PartnerAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(factoryaddr,factoryaddrAdmin)
# admin.site.register(Warehouse,WarehouseAdmin)
# admin.site.register(Brand,BrandAdmin)
# admin.site.register(Measure,MeasureAdmin)
# admin.site.register(Category,CategoryAdmin)
# admin.site.register(TechnicalParameterName,TechParamNameAdmin)
# admin.site.register(Trade,TradeAdmin)
# admin.site.register(ExpenseAccount,ExpenseAdmin)
# admin.site.register(Employee,EmployeeAdmin)
# admin.site.register(DataImport,DataImportAdmin)
# admin.site.register(Document,DocumentAdmin)

# admin.site.register(apca_t)
# admin.site.register(apba_t)