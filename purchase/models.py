# coding=utf-8
import datetime
import os
import xlrd
import decimal
from django.db import transaction
from django.db import models
from django.db.models.aggregates import Sum
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from LUERP import settings
from common import generic
from common import const
from django import forms
from basedata.models import Pmdnt200
from reportlab.pdfgen import canvas


class filterpmdn200(models.Model):

    statusid=((True,'完成'),(False,'未完成'))

    id = models.AutoField(id, primary_key=True)
    allname = models.CharField('全称',max_length=140, null=True)
    bbill = models.CharField('采购单号',max_length=40, null=True)
    bclass = models.CharField('采购单别',max_length=20, null=True)
    bnum = models.IntegerField('序号',null=True)
    buydate = models.DateField('采购日期',null=True)
    jc = models.CharField('简称',max_length=40,null=True)
    code = models.CharField('品号',max_length=20,null=True)
    name = models.CharField('品名     .',max_length=520,null=True)
    spec = models.CharField('规格     .',max_length=520,null=True)
    unit = models.CharField('计量单位',max_length=6,null=True)
    quan = models.DecimalField('采购量',max_digits=14,decimal_places=0,null=True)
    okquan = models.DecimalField('已交数量',max_digits=14,decimal_places=0,null=True)
    noquan = models.DecimalField('未交量',max_digits=14,decimal_places=0,null=True)
    currenct = models.CharField('币别',max_length=10,null=True)
    price = models.DecimalField('采购单价',max_digits=14,decimal_places=6,null=True)
    rate = models.DecimalField('税率',max_digits=14,decimal_places=0,null=True)
    notex = models.DecimalField('未交未税金额',max_digits=14,decimal_places=2,null=True)
    tex = models.DecimalField('税额',max_digits=14,decimal_places=0,null=True)
    allchash = models.DecimalField('未交含税金额',max_digits=14,decimal_places=2,null=True)
    sclass = models.CharField('分类',max_length=20,null=True)
    predate = models.DateField('要求到货日',null=True)
    sbill = models.CharField('来源单号',max_length=40,null=True)
    PO = models.CharField('PO',max_length=20,null=True)
    buyer = models.CharField('采购人员',max_length=20,null=True)
    checker = models.CharField('审核者',max_length=20,null=True)
    tao = models.CharField('tao料号',max_length=40,null=True)
    company = models.CharField('公司',max_length=40,null=True)
    sno = models.CharField('供方编号',max_length=40,null=True)
    billno = models.CharField('采购单号序号',max_length=60,unique=True)
    note = models.TextField('备注',null=True)
    sdate = models.DateField('供方回复到货日',null=True)
    snote = models.CharField('供方说明',max_length=20,blank=True,null=True)
    retime = models.DateTimeField('回复时间',null=True)
    reman =  models.CharField('回复人 ',max_length=20,null=True)
    zc =  models.CharField('周次 ',max_length=7,null=True)
    buyercode =  models.CharField('采购员编码',max_length=20,null=True)

    ok = models.BooleanField('状态',choices=statusid)

    class Meta:
        managed = False
        db_table = 'filterpmdn200'
        #unique_together = (("采购单号", "采购单别", "序号"),)
        verbose_name = "采购交期供应商确认"
        verbose_name_plural = verbose_name
        ordering = ['-predate','billno']

    def short_predate(self):
        gw = self.predate.strftime("%W")

        return str(self.predate) +'('+ gw + '周)'

    short_predate.allow_tags = True
    short_predate.short_description = '要求到货日'

    def short_name(self):
        if len(str(self.name)) > 30:
            return '{}...'.format(str(self.name)[0:30])
        else:
            return str(self.name)

    short_name.allow_tags = True
    short_name.short_description = '品名　　　 .'

    def short_spec(self):
        if len(str(self.spec)) > 30:
            return '{}...'.format(str(self.spec)[0:30])
        else:
            return str(self.spec)

    short_spec.allow_tags = True
    short_spec.short_description = '规格　　　 .'


class factoryaddr(models.Model):
    id = models.AutoField(id, primary_key=True)
    code = models.CharField('代码', max_length=10,unique=True)
    name = models.CharField('名称代码', max_length=20)
    address = models.CharField('收货地址', max_length=220)
    def __str__(self):
        return self.name

    class Meta:
        # managed = True
        # app_label = 'default'
        # db_table = 'factoryaddr'
        verbose_name = "供应商送货地址"
        verbose_name_plural = verbose_name
        ordering = ['code']

class test():
    def hello(c):
        c.drawString(100, 100, "Hello World")

    print('asdfasdfsdfasdfasdf')
    c = canvas.Canvas("hello.pdf")
    hello(c)
    c.showPage()
    c.save()

class deliverynote(generic.BO):
    STATUS = (
        ('0', '制单'),
        ('1', '发货'),
        ('4', '作废'),
        ('9', '收货'),
        ('12', '检验'),
    )
    id = models.AutoField('发货单号码', primary_key=True)
    usercode = models.CharField('供应商代码',max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    username = models.CharField('供应商简称',max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    order_date = models.DateTimeField('送货时间')
    arrive_date = models.DateTimeField('确认送达时间')
    buycode = models.CharField('采购员代码',max_length=const.DB_CHAR_NAME_20,blank=True, null=True)
    buyname = models.CharField('采购员', max_length=const.DB_CHAR_NAME_20, blank=True, null=True)
    company = models.ForeignKey(factoryaddr, on_delete=models.CASCADE, verbose_name='收货单位', null=True)
    unitcode = models.CharField('收货单位名称', max_length=const.DB_CHAR_NAME_20 ,blank=True, null=True)
    unitaddr = models.CharField('收货地址', max_length=200, blank=True, null=True)
    description = models.TextField("送货单描述", blank=True, null=True)
    status = models.CharField('状态', max_length=const.DB_CHAR_CODE_2, default='0', choices=STATUS)

    def __unicode__(self):
        return u'%s %s' % (self.code,self.title)

    class Meta:
        verbose_name = '送货单'
        verbose_name_plural = verbose_name



class deliveryitem(models.Model):

    po = models.ForeignKey(deliverynote,on_delete=models.CASCADE,verbose_name='发货单主表', null=True)
    bill = models.ForeignKey(filterpmdn200,on_delete = models.CASCADE,verbose_name='采购单', null=True,limit_choices_to={'ok': False},)#,limit_choices_to={'is_staff': True}
    crop = models.CharField('公司别',max_length=3,blank=True,null=True)
    jc = models.CharField('简称',max_length=40,null=True)
    bbill = models.CharField('采购单号',max_length=40, null=True)
    bclass = models.CharField('采购单别',max_length=20, null=True)
    bnum = models.IntegerField('序号',null=True)
    buydate = models.DateField('采购日期',null=True)
    code = models.CharField('品号',max_length=20,null=True)
    name = models.CharField('品名',max_length=520,null=True)
    spec = models.CharField('规格',max_length=520,null=True)
    unit = models.CharField('计量单位',max_length=6,null=True)
    quan = models.DecimalField('采购量',max_digits=14,decimal_places=2,null=True)
    okquan = models.DecimalField('已交数量',max_digits=14,decimal_places=2,null=True)
    noquan = models.DecimalField('未交量',max_digits=14,decimal_places=2,null=True)
    sendquan = models.DecimalField('发货数量',max_digits=14,decimal_places=2,null=True)
    arrive_date = models.DateTimeField('检验完成时间')
    jokquan = models.DecimalField('验收数量', max_digits=14, decimal_places=2, null=True)
    jcnoquan = models.DecimalField('验退数量', max_digits=14, decimal_places=2, null=True)
    sdate = models.DateField('供方回复到货日',null=True)
    sbill = models.CharField('来源单号',max_length=40,null=True)
    description = models.CharField('备注描述',max_length=140,null=True)

    def vender(self):
        return u'%s' % (self.po.username)

    vender.short_description = '供应商'

    class Meta:
        verbose_name = '发货单细节'
        verbose_name_plural = '发货单细节'

# class deliveryitemForm(forms.ModelForm):
#
#     new_price = forms.CharField(label=_('new price'),required=False)
#
#     class Meta:
#         model = deliveryitem
        # fields = ('material', 'measure', 'cnt', 'price')

