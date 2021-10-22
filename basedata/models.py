# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from common import const
from common import generic
from syscfg.models import Module,Site
from organ.models import Organization,Position
import datetime
from plugin.xls import ExcelManager
from django.utils.html import format_html


#
class pmdg(models.Model):#(generic.BO):
    """
    料件报价单
    """
    sx = (
        ('Y', "外加工"),
        ('N', "采购"),
    )
    STATUS = (
        (1, "最终报价"),
        (2, "理论重量首次报价")
    )
    TP = (
        ('0', "未提交"),
        ('1', "已提交"),
        ('2', "处理中"),
        ('3', "已完成"),
    )
    STATUSX = (
        ('0',"草稿"),
        ('1',"已发布")
    )
    managed = False
    # app_label = 'default'
    db_table = 'basedata_pmdg'

    index_weight = 8

    code = models.CharField("编号",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    keywords = models.CharField("关键词",max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    description = models.TextField("描述信息",blank=True,null=True)
    tp = models.CharField( "类别", max_length=const.DB_CHAR_CODE_2,default='10',choices=TP)
    business_domain = models.CharField( "业务域",max_length=const.DB_CHAR_CODE_4,choices=const.get_value_list('S045'),default='OT')
    user = models.ForeignKey(User,verbose_name="用户",blank=True,null=True,on_delete=models.CASCADE)
    status = models.CharField("单据状态",max_length=const.DB_CHAR_CODE_2,default='0',choices=TP)

    pmdgsite = models.CharField('公司别',max_length=20)
    pmdgdocno = models.CharField('询价单号',max_length=30)
    pmdgseq = models.CharField('项次',max_length=10)
    pmdg001 = models.CharField('属性',max_length=10)#,choices=sx
    pmdg002 = models.CharField('供应商编号',max_length=20)
    pmaal004 = models.CharField('供应商简称',max_length=60)
    pmdg003 = models.CharField('品号',max_length=20)
    imaal003 = models.CharField('品名',max_length=520)
    imaal004 = models.CharField('规格',max_length=520)
    pmdgua006 = models.IntegerField('报价分类',choices=STATUS, help_text=u'选择【最终报价】时填写【产品报价含税】，选择【理论重量首次报价】时填写【理论重量首次报价[按g]】')

    pmdg007 = models.IntegerField('询价数量')
    pmdg008 = models.CharField('询价单位',max_length=20)
    pmdg009 = models.BooleanField('是否分量计价',default=0)
    pmdg011 = models.DecimalField('税率',max_digits=14,decimal_places=4,blank=True,null=True)
    pmdgud014 = models.IntegerField('最小包装量')
    pmdg013 = models.IntegerField('最低采购量')
    pmdgua007 = models.DecimalField('产品报价含税',max_digits=14,decimal_places=4,blank=True,null=True)
    pmdguaqt = models.DecimalField('其他费用[如喷漆嵌件移印]',max_digits=14,decimal_places=4,blank=True,null=True)
    pmdgud013 = models.DecimalField('理论重量首次报价[按g]',max_digits=14,decimal_places=4,blank=True,null=True)
    pmdgud012 = models.DecimalField('模具费报价含税',max_digits=14,decimal_places=4,blank=True,null=True)
    pmdg017 = models.DateField('有效日期',auto_now_add=True)
    pmdg030 = models.TextField('报价公式及其他说明',blank=True,null=True)

    pmdf002 = models.CharField('工号',max_length=20)
    ooag011 = models.CharField('采购人员',max_length=60)

    pmdgud011 = models.DecimalField('产品采购员议价',max_digits=14,decimal_places=2,blank=True,null=True, help_text=u'与供应商交涉后，最终价格，采购员在终审时填写')
    pmdgud015 = models.DecimalField('模具费采购员议价',max_digits=14,decimal_places=2,blank=True,null=True, help_text=u'与供应商交涉后，最终价格，采购员在终审时填写')
    pmdgud018 = models.DecimalField('毛重(g)',max_digits=14,decimal_places=2,blank=True,null=True)
    pmdgud019 = models.DecimalField('净重(g)',max_digits=14,decimal_places=2,blank=True,null=True)
    pmdgud020 = models.DecimalField('理论重量(g)',max_digits=14,decimal_places=2,blank=True,null=True)
    pmdgud005 = models.CharField('材质及表面要求',blank=True,null=True,max_length=100)

    attach1 = models.FileField("附件1",blank=True,null=True,upload_to='doc', help_text=u'此处附件需要在提交审批前加入')
    attach2 = models.FileField("附件2",blank=True,null=True,upload_to='doc')
    attach3 = models.FileField("附件3",blank=True,null=True,upload_to='doc')

    pmdgud017 = models.IntegerField('交期(天)', default=0,null=True)
    # begin = models.DateField('开始时间',blank=True,null=True)
    # end = models.DateField('结束时间',blank=True,null=True)
    creator = models.CharField('创建人',blank=True,null=True,max_length=20)
    # modifier = models.CharField('修改时间',blank=True,null=True,max_length=20)
    creation = models.DateTimeField('创建时间',auto_now_add=True,blank=True,null=True)
    # modification = models.DateTimeField('修改人',auto_now=True,blank=True,null=True)

    def __str__(self):
        return u"%s | %s | %s" % (self.pmdg003,self.imaal003,self.imaal004)

    class Meta:
        verbose_name = '供应商报价'
        verbose_name_plural = verbose_name

    def short_name(self):
        try:
            return self.imaal003 + '|'+self.imaal004
        except Exception as e:
            return ''
    short_name.allow_tags = True
    short_name.short_description = '产品名称'

class pmdgfile(models.Model):
    pmdg = models.ForeignKey(pmdg, on_delete=models.CASCADE)
    pub_date = models.DateTimeField("发布日期",blank=True,null=True)
    size = models.CharField("大小",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    attach = models.FileField("附件",blank=True,null=True,upload_to='doc')
    title = models.CharField("标题",max_length=const.DB_CHAR_NAME_120)

    def __str__(self):
        return self.attach

    class Meta:
        managed = False
        verbose_name = "附件"
        verbose_name_plural = "附件"
        # db_tablespace = ''
        # permissions = (("can_deliver_pizzas", "Can deliver pizzas"),)
        # unique_together = (("first_name", "last_name"),)
        # get_latest_by = "order_date"
        # db_table = 'bookinfo'

# class pmdguser(models.Model):
#     id = models.AutoField(id, primary_key=True)
#     User = models.CharField('全称',max_length=140, null=True)
#
# #from app.models import Sale
#
# class SaleSummary(models.Model):
#     class Meta:
#         proxy = True
#         verbose_name = 'Sale Summary'
#         verbose_name_plural = 'Sales Summary'

class Pmdnt200(models.Model):

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
        db_table = 'Pmdnt200'
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


class Pmdnlog(models.Model):
    id = models.AutoField(id, primary_key=True)
    billno = models.CharField('采购单号', max_length=40)
    redate = models.DateField('供方回复交期')
    renote = models.TextField('供方说明', null=True)
    retime = models.DateTimeField('供方回复时间', auto_now=True)
    reman = models.CharField('回复人', max_length=20)
    ip = models.GenericIPAddressField('ip', max_length=20, null=True)
    country = models.CharField('国家', max_length=20, null=True)
    prov = models.CharField('省', max_length=20, null=True)
    city = models.CharField('城市', max_length=20, null=True)
    action = models.CharField('动作', max_length=40, null=True)
    environ = models.CharField('使用设备', max_length=200, null=True)
    class Meta:
        managed = False

        db_table = 'Pmdnlog'
        verbose_name = "采购单供方回复交期日志"
        verbose_name_plural = verbose_name
        ordering = ['-retime']
        #proxy = True  # 设置为True 否则会重新注册一张数据表

class apca_t(generic.BO):
    statusid=((True,'完成'),(False,'未完成'))

    id = models.AutoField(id, primary_key=True)
    paydate = models.DateField('计划付款日', null=True)
    sno = models.CharField('供方编号', max_length=40, null=True)
    sname = models.CharField('供应商简称', max_length=40, null=True)
    paybill = models.CharField('应付单号', max_length=40,null=True)
    paytj = models.CharField('付款条件', max_length=100,null=True)
    fphm = models.TextField('发票号码',null=True)
    fprq = models.DateField('发票日期', null=True)
    cash = models.DecimalField('应付/预付金额',max_digits=14,decimal_places=2,null=True)
    note = models.CharField('备注', max_length=100,null=True)
    status = models.CharField('冻结状态', max_length=40, null=True)
    zlts = models.DecimalField('账期天数',max_digits=14,decimal_places=0,null=True)
    gsb = models.CharField('公司别', max_length=10, null=True)
    cgybm = models.CharField('采购员编码', max_length=40, null=True)
    cgy = models.CharField('采购员', max_length=40, null=True)
    zc = models.CharField('周次', max_length=7, null=True)
    ok = models.BooleanField('付款完成状态',choices=statusid)

    def rjust_cash(self):
        return format_html(
            '<p align="right">{}</p>',
            self.cash,
        )
    rjust_cash.short_description = '应付/预付金额'
    class Meta:
        managed = False
        db_table = 'apca_t'
        #unique_together = (("采购单号", "采购单别", "序号"),)
        verbose_name = "付款计划"
        verbose_name_plural = verbose_name
        ordering = ['paydate']
        app_label = 'basedata'

    def short_fp(self):
        if len(str(self.fphm)) > 30:
            return '{}...'.format(str(self.fphm)[0:30])
        else:
            return str(self.fphm)

    short_fp.allow_tags = True
    short_fp.short_description = '发票号码'
# class res_partner(models.Model):
#     """
#     客户代码表
#     """
#     managed = False
#
#     #id = models.IntegerField('id',primary_key=True)
#     name = models.CharField('客户名称', max_length=100)
#     company_id = models.IntegerField('company_id')
#     company_type = models.CharField('客户类型', max_length=10)
#     street = models.CharField('地址', max_length=100)
#     country_id = models.IntegerField('country_id')
#     parent_id = models.IntegerField('parent_id')
#     supplier = models.BooleanField('供应商')
#     ref = models.CharField('ref', max_length=10)
#     email = models.EmailField('email')
#     is_company = models.BooleanField('is_company')
#     tz = models.CharField('tz', max_length=10)
#     customer = models.BooleanField('客户')
#     employee = models.BooleanField('employee')
#     active = models.BooleanField('active')
#     display_name = models.CharField('display_name', max_length=100)
#     phone = models.CharField('座机', max_length=30)
#     mobile = models.CharField('手机', max_length=30)
#     type = models.CharField('type', max_length=10)
#     commercial_partner_id = models.IntegerField('commercial_partner_id')
#     notify_email = models.CharField('notify_email', max_length=10)
#     opt_out = models.BooleanField('opt_out')
#     sourcing_mc = models.CharField('sourcing_mc', max_length=30)
#     pay_to = models.CharField('pay_to', max_length=10)
#     sourcing_main_products = models.CharField('sourcing_main_products', max_length=100)
#     name_cn = models.CharField('LUTEC', max_length=30)
#     write_date = models.DateTimeField('修改时间')
#
#     class Meta:
#         managed = False
#         app_label = 'Tao'
#         db_table = 'res_partner'
#         verbose_name = '客户代码表'
#         verbose_name_plural = verbose_name
#         ordering = ['-write_date']
class ApbacodeSummary(generic.apba_t):
    class Meta:
        proxy = True
        verbose_name = '对账单按品号汇总'
        verbose_name_plural = verbose_name

class res_company(models.Model):
    id = models.IntegerField(id,primary_key=True)
    name = models.CharField(max_length=const.DB_CHAR_NAME_40)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '公司'
        verbose_name_plural = verbose_name
        managed = False
        app_label = 'Tao'
        db_table = 'res_company'

class res_partner(models.Model):
    """
    客户名称
    """
    id = models.IntegerField(id,primary_key=True)
    ref = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='缩写')
    name = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='客户名称')
    company_type = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='公司类型')
    street = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='街道')
    email = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='邮箱')
    tz = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='时区')
    website = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='网址')
    fax = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='传真')
    street2 = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='街道2')
    display_name = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='显示名称')
    phone = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='电话')
    mobile = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='手机')
    type = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='类型')
    notify_email = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='通知邮箱')
    pay_to = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='付款对象')
    sourcing_main_products = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='主要产品')
    sourcing_code_of_business = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='商业代码')
    name_cn = models.CharField(max_length=const.DB_CHAR_NAME_40,verbose_name='中文名')
    supplier = models.BooleanField(verbose_name='供应商')
    is_company = models.BooleanField(verbose_name='企业')
    customer = models.BooleanField(verbose_name='客户')
    employee = models.BooleanField(verbose_name='雇员')
    active = models.BooleanField(verbose_name='有效')
    create_date = models.DateTimeField(verbose_name='建档时间')
    write_date = models.DateTimeField(verbose_name='修改时间')
    company = models.ForeignKey(res_company,on_delete=models.CASCADE,verbose_name='所属公司')
    class Meta:
        verbose_name = '客户名称'
        verbose_name_plural = verbose_name
        managed = False
        app_label = 'Tao'
        db_table = 'res_partner'
        ordering = ['-create_date']

    def __str__(self):
        return self.name

class sale_order(models.Model):
    """
    订单主表
    """
    managed = False

    #id = models.IntegerField('id',primary_key=True)
    client_order_ref = models.CharField('client_order_ref', max_length=100)
    partner = models.ForeignKey('res_partner', to_field='id', on_delete=models.CASCADE,verbose_name='客户名称')
    create_uid = models.IntegerField('create_uid')
    procurement_group_id = models.IntegerField('procurement_group_id')
    amount_untaxed = models.DecimalField('amount_untaxed',max_digits=14,decimal_places=4)
    company_id = models.IntegerField('company_id')
    amount_string = models.TextField('说明')
    note = models.TextField('备注')
    state = models.CharField('状态', max_length=30)
    amount_tax = models.DecimalField('amount_tax',max_digits=14,decimal_places=4)
    validity_date = models.DateField('validity_date')
    payment_term_id = models.IntegerField('payment_term_id')
    create_date = models.DateTimeField('单据日期')
    partner_invoice_id = models.IntegerField('partner_invoice_id')
    user_id = models.IntegerField('user_id',)
    amount_total = models.DecimalField('amount_total',max_digits=14,decimal_places=4)
    invoice_status = models.CharField('invoice_status', max_length=30)
    name = models.CharField('名称', max_length=20)
    partner_shipping_id = models.IntegerField('partner_shipping_id')
    picking_policy = models.CharField('picking_policy', max_length=10)
    incoterm = models.IntegerField('incoterm')
    warehouse_id = models.IntegerField('warehouse_id')
    quote_viewed = models.BooleanField('quote_viewed')
    effective_date = models.DateTimeField('effective_date')
    requested_date = models.DateTimeField('requested_date')
    commitment_date = models.DateTimeField('commitment_date')
    auto_generated = models.BooleanField('auto_generated')
    port_discharge = models.CharField('port_discharge', max_length=10)
    date_approve = models.BooleanField('date_approve')
    crd_original_date = models.DateField('crd_original_date')
    construction_check = models.BooleanField('construction_check')
    container_used = models.CharField('container_used', max_length=10)
    invoice_quantity = models.CharField('invoice_quantity', max_length=10)
    crd_date = models.DateField('crd_date')
    inactive_comp = models.BooleanField('inactive_comp')
    shipment = models.CharField('运输方式', max_length=30)
    delay_2_confirm_date = models.IntegerField('delay_2_confirm_date')
    psi_original_date = models.DateField('psi_original_date')
    shipping_date = models.DateField('shipping_date')
    bd_required = models.BooleanField('bd_required')
    is_late = models.BooleanField('is_late')
    load_original_date = models.DateField('load_original_date')
    delivery_place = models.CharField('delivery_place', max_length=100)
    bd_approval_date = models.DateField('bd_approval_date')
    latest_shipment = models.DateField('latest_shipment')
    load_date = models.DateField('load_date')
    shipping_company = models.CharField('shipping_company', max_length=100)
    priority = models.IntegerField('priority')
    pre_inspection = models.CharField('pre_inspection', max_length=10)
    psi_date = models.DateField('psi_date')
    mkt_approval_date = models.DateTimeField('mkt_approval_date')
    currency_rate2usd = models.DecimalField('currency_rate2usd',max_digits=14,decimal_places=4)
    client_batch_number = models.CharField('client_batch_number', max_length=30)
    date_order = models.DateTimeField('date_order')
    bop_approval_date = models.DateTimeField('bop_approval_date')
    bop_approval_deadline = models.DateField('bop_approval_deadline')
    amount_string = models.CharField('amount_string', max_length=30)
    pack_approval_date = models.DateTimeField('pack_approval_date')
    unify_order = models.BooleanField('unify_order')
    user_pack_id = models.IntegerField('user_pack_id')
    user_cs_id = models.IntegerField('user_cs_id')
    port_loading = models.CharField('port_loading', max_length=30)
    write_date = models.DateTimeField('修改时间')

    class Meta:
        managed = False
        app_label = 'Tao'
        db_table = 'sale_order'
        verbose_name = '订单主表'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']

class sale_order_line(models.Model):
    """·
    订单明细
    """
    managed = False

    #id = models.ForeignKey('sale_order', to_field='id', default=1,on_delete=models.CASCADE)
    qty_to_invoice = models.DecimalField('qty_to_invoice',max_digits=14,decimal_places=4)
    sequence = models.IntegerField('sequence')
    product_uom_qty = models.DecimalField('product_uom_qty',max_digits=14,decimal_places=4)
    qty_invoiced = models.DecimalField('qty_invoiced',max_digits=14,decimal_places=4)
    currency_id = models.IntegerField('currency_id')
    price_tax = models.DecimalField('price_tax',max_digits=14,decimal_places=4)
    product_uom = models.IntegerField('product_uom')
    customer_lead = models.DecimalField('customer_lead',max_digits=14,decimal_places=4)
    company_id = models.IntegerField('company_id')
    name = models.TextField('name')
    state = models.CharField('state', max_length=10)
    order_id = models.IntegerField('order_id')
    price_subtotal = models.DecimalField('price_subtotal',max_digits=14,decimal_places=4)
    discount = models.DecimalField('discount',max_digits=14,decimal_places=4)
    price_reduce = models.DecimalField('price_reduce',max_digits=14,decimal_places=4)
    amount_total = models.DecimalField('amount_total',max_digits=14,decimal_places=4)
    qty_delivered = models.DecimalField('qty_delivered',max_digits=14,decimal_places=4)
    price_total = models.DecimalField('price_total',max_digits=14,decimal_places=4)
    invoice_status = models.CharField('invoice_status', max_length=10)
    product_id = models.IntegerField('product_id')
    salesman_id = models.IntegerField('salesman_id')
    pi_cust_code = models.CharField('pi_cust_code', max_length=30)
    display_barcode = models.CharField('display_barcode', max_length=30)
    status_check = models.BooleanField('status_check')
    inn = models.IntegerField('inn')
    price_unit_default = models.DecimalField('price_unit_default',max_digits=14,decimal_places=4)
    outer = models.IntegerField('outer')
    currency_rate2usd = models.DecimalField('currency_rate2usd',max_digits=14,decimal_places=4)
    gs_qty = models.IntegerField('gs_qty')
    inn_barcode = models.CharField('inn_barcode', max_length=10)
    item_number = models.IntegerField('item_number')
    outer_barcode = models.CharField('outer_barcode', max_length=10)
    brand = models.IntegerField('brand')
    size_option = models.CharField('size_option', max_length=10)
    type_of_pallet = models.IntegerField('type_of_pallet')
    type_of_outer = models.IntegerField('type_of_outer')
    size_total = models.CharField('size_total', max_length=10)
    unit_pack = models.IntegerField('unit_pack')
    th_weight = models.DecimalField('th_weight',max_digits=14,decimal_places=4)
    type_of_display = models.IntegerField('type_of_display')
    type_of_inn = models.IntegerField('type_of_inn')
    display = models.IntegerField('display')
    create_date = models.DateTimeField('建档时间')
    write_date = models.DateTimeField('修改时间')

    class Meta:
        managed = False
        app_label = 'Tao'
        db_table = 'sale_order_line'
        verbose_name = '订单明细'
        verbose_name_plural = verbose_name
        ordering = ['-write_date']

class ValueList(generic.BO):
    """
    值列表
    """
    index_weight = 9
    code = models.CharField(_("list code"),max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    name = models.CharField(_("list name"),max_length=const.DB_CHAR_NAME_40)
    module = models.ForeignKey(Module,verbose_name=_("module"),on_delete=models.CASCADE, blank=True,null=True)
    status = models.BooleanField(_("in use"),default=True)
    init = models.BooleanField(_("is init"),default=False)
    locked = models.BooleanField(_("is locked"),default=False)
    locked_by = models.ForeignKey(User,verbose_name=_("locked by"),on_delete=models.CASCADE, blank=True,null=True)
    lock_time = models.DateTimeField(_("locked time"),null=True,blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(ValueList,self).save(force_insert,force_update,using,update_fields)
        # sql = 'update basedata_valuelistitem set group_code = %s where groud_id=%s'
        # params = [self.code,self.id]
        # generic.update(sql,params)

    class Meta:
        managed = False
        verbose_name = "值列表"
        verbose_name_plural = "值列表"


class ValueListItem(models.Model):
    """
    值列表项
    """
    group = models.ForeignKey(ValueList,verbose_name=_("list group"),on_delete=models.CASCADE)
    group_code = models.CharField(max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    code = models.CharField(_("item code"),max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    name = models.CharField(_("item name"),max_length=const.DB_CHAR_NAME_40)
    status = models.BooleanField(_("in use"),default=True)
    weight = models.IntegerField(_("weight"),null=True,default=9)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.code:
            cnt = self.group.valuelistitem_set.count()+1
            self.code = "%02d" % cnt
        self.group_code = self.group.code
        super(ValueListItem,self).save(force_insert,force_update,using,update_fields)

    def __unicode__(self):
        return "%s-%s" % (self.code,self.name)

    class Meta:
        managed = False
        verbose_name = "值列表项"
        verbose_name_plural = verbose_name
        ordering = ['weight','code']
        index_together = ['group','group_code']


def get_value_list(group):
    """

    :param group:
    :return:
    """
    if group:
        return tuple([(item.code, item.name) for item in ValueListItem.objects.filter(group_code__exact=group,status=1)])
    else:
        return None

class Document(generic.BO):
    """
    文档管理
    """
    TP = (
        ('00',"系统手册"),
        ('10', "业务文档"),
    )
    STATUS = (
        ('0',"草稿"),
        ('1',"已发布")
    )
    index_weight = 8
    code = models.CharField("编号",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    title = models.CharField("标题",max_length=const.DB_CHAR_NAME_120)
    keywords = models.CharField("关键词",max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    description = models.TextField("描述信息",blank=True,null=True)
    tp = models.CharField( "类别",max_length=const.DB_CHAR_CODE_2,default='10',choices=TP)
    business_domain = models.CharField( "业务域",max_length=const.DB_CHAR_CODE_4,choices=const.get_value_list('S045'),default='OT')
    user = models.ForeignKey(User,verbose_name="用户",blank=True,null=True,on_delete=models.CASCADE)
    status = models.CharField("状态",max_length=const.DB_CHAR_CODE_2,default='0',choices=STATUS)
    pub_date = models.DateTimeField("发布日期",blank=True,null=True)
    size = models.CharField("大小",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    attach = models.FileField("附件",blank=True,null=True,upload_to='doc')

    class Meta:
        managed = False
        verbose_name = "文档"
        verbose_name_plural = "文档"

class Address(generic.BO):
    """
    地址
    """
    ADDRESS_TYPE = get_value_list('S011')
    address_type = models.CharField(_("address type"),max_length=const.DB_CHAR_CODE_2,default='01')#,choices=ADDRESS_TYPE
    address = models.CharField(_("address"),max_length=const.DB_CHAR_NAME_120)
    zipcode = models.CharField(_("zipcode"),max_length=const.DB_CHAR_CODE_8,blank=True,null=True)
    phone = models.CharField(_("phone"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    contacts = models.CharField(_("contacts"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)

    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE, blank=True,null=True)
    object_id = models.PositiveIntegerField(blank=True,null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        managed = False
        verbose_name = "地址"
        verbose_name_plural = "地址"


class Partner(generic.BO):
    """
    合作伙伴
    """
    index_weight = 3
    PARTNER_TYPE = (
        ('C', _('Customer')),
        ('S', _('Supplier')),
    )

    LEVEL = (
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D'),
    )
    org = models.ForeignKey(Organization,verbose_name=_("organization"),on_delete=models.CASCADE, blank=True,null=True)
    code = models.CharField(_("partner code"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    name = models.CharField(_("partner name"),max_length=const.DB_CHAR_NAME_120)
    short = models.CharField(_("short name"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    pinyin = models.CharField(_("pinyin"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    partner_type = models.CharField(_("type"),max_length=const.DB_CHAR_CODE_2,choices=PARTNER_TYPE,default='C')
    level = models.CharField(_("level"),max_length=const.DB_CHAR_CODE_2,choices=LEVEL,default='C')

    tax_num = models.CharField(_("tax num"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    tax_address = models.CharField(_("tax address"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    tax_account = models.CharField(_("tax account"),max_length=const.DB_CHAR_NAME_80,blank=True,null=True)

    contacts = models.CharField(_("contacts"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    phone = models.CharField(_("phone"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    memo = models.TextField(_("memo"),blank=True,null=True)

    class Meta:
        managed = False
        verbose_name = "合作伙伴"
        verbose_name_plural = "合作伙伴"
        permissions = (
            ('view_all_customer',_("view all customer")),
            ('view_all_supplier',_("view all supplier")),
        )


class BankAccount(generic.BO):
    """
    银行账户 organization
    """
    account = models.CharField(_("account num"),max_length=const.DB_CHAR_NAME_40)
    title = models.CharField(_("bank name"),max_length=const.DB_CHAR_NAME_40)
    memo = models.CharField(_("memo"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    partner = models.ForeignKey(Partner,verbose_name=_("partner"),on_delete=models.CASCADE, blank=True,null=True)
    org = models.ForeignKey(Organization,verbose_name=_("organization"),on_delete=models.CASCADE, blank=True,null=True)

    def __str__(self):
        name = ''
        if self.org:
            name = self.org.name
        elif self.partner:
            name = self.partner.name
        return u"%s %s %s" % (name,self.account,self.title)

    class Meta:
        managed = False
        verbose_name = "银行账户"
        verbose_name_plural = "银行账户"


class Project(generic.BO):
    """
    工程项目
    """
    STATUS = get_value_list('S012')
    TYPES = get_value_list('S013')
    index_weight = 1

    code = models.CharField(_("project code"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    name = models.CharField(_("project name"),max_length=const.DB_CHAR_NAME_120)
    short = models.CharField(_("short name"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    pinyin = models.CharField(_("pinyin"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)

    partner = models.ForeignKey(Partner,blank=True,null=True,verbose_name=_("partner"),on_delete=models.CASCADE, limit_choices_to={"partner_type":"C"})
    status = models.CharField(_("status"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,default='00')#,choices=STATUS
    prj_type = models.CharField(_("project type"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,default='00')#choices=TYPES,

    description = models.TextField(_("description"),blank=True,null=True)

    budget = models.DecimalField(_("budget"),max_digits=10,decimal_places=2,blank=True,null=True)
    income = models.DecimalField(_("income"),max_digits=10,decimal_places=2,blank=True,null=True)
    expand = models.DecimalField(_("expand"),max_digits=10,decimal_places=2,blank=True,null=True)

    blueprint = models.FileField(_("blueprint"),upload_to='project',blank=True,null=True)
    offer = models.FileField(_("offer sheet"),upload_to='offer sheet',blank=True,null=True)
    business = models.FileField(_("business document"),upload_to='project',blank=True,null=True)

    users = models.ManyToManyField(User,verbose_name=_("related users"),blank=True)
    org = models.ForeignKey(Organization,verbose_name=_("organization"),on_delete=models.CASCADE, blank=True,null=True)

    class Meta:
        managed = False
        verbose_name = "项目"
        verbose_name_plural = "项目"


class Warehouse(models.Model):
    """
    仓库
    """
    index_weight = 6
    code = models.CharField(_("code"),max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_40)
    status = models.BooleanField(_("in use"),default=True)
    location = models.CharField(_("location"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    users = models.ManyToManyField(User,verbose_name=_("related users"),blank=True)
    org = models.ForeignKey(Organization,verbose_name=_("organization"),on_delete=models.CASCADE, blank=True,null=True)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        managed = False
        verbose_name = "仓库"
        verbose_name_plural = "仓库"


class Measure(models.Model):
    """
    计量单位
    """
    index_weight = 5
    code = models.CharField(_("code"),max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_20)
    status = models.BooleanField(_("in use"),default=True)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        managed = False
        verbose_name ="计量单位"
        verbose_name_plural = "计量单位"


class Trade(models.Model):
    """
    国民经济行业分类
    """
    index_weight = 102
    code = models.CharField(_("code"),max_length=const.DB_CHAR_CODE_6)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_120)
    memo = models.CharField(_("memo"),max_length=const.DB_CHAR_NAME_120,null=True,blank=True)
    parent = models.ForeignKey('self',verbose_name=_("parent"),on_delete=models.CASCADE, null=True,blank=True)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        managed = False
        verbose_name = "国民经济行业分类"
        verbose_name_plural = "国民经济行业分类"
        ordering = ['code']


class Brand(models.Model):
    """
    品牌
    """
    index_weight = 101
    trade = models.ForeignKey(Trade,verbose_name=_("trade"),on_delete=models.CASCADE, null=True,blank=True)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_120)
    pinyin = models.CharField(_("pinyin"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    weight = models.IntegerField(_("weight"),blank=True,null=True,default=99)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        managed = False
        verbose_name = "品牌"
        verbose_name_plural = "品牌"


class Category(models.Model):
    """
    分类
    """
    index_weight = 100
    trade = models.ForeignKey(Trade,verbose_name=_("trade"),on_delete=models.CASCADE, null=True,blank=True)
    parent = models.ForeignKey('self',verbose_name=_("parent"),on_delete=models.CASCADE, null=True,blank=True)
    code = models.CharField(_("code"),max_length=const.DB_CHAR_CODE_6,null=True,blank=True)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_120)
    path = models.CharField(_("path"),max_length=const.DB_CHAR_NAME_200,null=True,blank=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        managed = False
        verbose_name = "分类"
        verbose_name_plural =  "分类"


class TechnicalParameterName(models.Model):
    """
    技术参数-名称，将技术参数绑定于物料分类上，在此分类下的物料自动继承全部技术参数
    """
    index_weight = 7
    category = models.ForeignKey(Category,verbose_name=_("material category"),on_delete=models.CASCADE)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_40)
    status = models.BooleanField(_("in use"),default=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        managed = False
        verbose_name = "技术参数-名称"
        verbose_name_plural = "技术参数-名称"


class TechnicalParameterValue(models.Model):
    """
    技术参数-值，将技术参数绑定于物料分类上，在此分类下的物料自动继承全部技术参数
    """
    tech_name = models.ForeignKey(TechnicalParameterName,verbose_name=_("technical name"),on_delete=models.CASCADE)
    value = models.CharField(_("value"),max_length=const.DB_CHAR_NAME_80)
    description = models.CharField(_("description"),max_length=const.DB_CHAR_NAME_80,null=True,blank=True)

    def __str__(self):
        return '%s' % self.value

    class Meta:
        managed = False
        verbose_name = "技术参数-值"
        verbose_name_plural = "技术参数-值"


class Material(generic.BO):
    """
    物料
    """
    index_weight = 4
    code = models.CharField(_("material code"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    barcode = models.CharField(_("bar code"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    name = models.CharField(_("material name"),max_length=const.DB_CHAR_NAME_120)
    spec = models.CharField(_("specifications"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    pinyin = models.CharField(_("pinyin"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    brand = models.ForeignKey(Brand,blank=True,null=True,verbose_name=_("brand"),on_delete=models.CASCADE)
    category = models.ForeignKey(Category,blank=True,null=True,verbose_name=_("category"),on_delete=models.CASCADE)
    tp = models.CharField(_('mt type'),blank=True,null=True,max_length=const.DB_CHAR_CODE_2,choices=const.get_value_list('S054'),default='10')
    status = models.BooleanField(_("in use"),default=True)
    is_equip = models.BooleanField(_("is equipment"),default=False)
    can_sale = models.BooleanField(_("can sale"),default=True)
    is_virtual = models.BooleanField(_("is virtual"),default=False)

    warehouse = models.ForeignKey(Warehouse,blank=True,null=True,verbose_name=_("warehouse"),on_delete=models.CASCADE)
    measure = models.ManyToManyField(Measure,verbose_name=_("measure"))

    params = models.ManyToManyField(TechnicalParameterValue,verbose_name=_("technical parameter"),through='MaterialParam')

    stock_price = models.DecimalField(_("stock price"),max_digits=14,decimal_places=4,blank=True,null=True)
    purchase_price = models.DecimalField(_("purchase price"),max_digits=14,decimal_places=4,blank=True,null=True)
    sale_price = models.DecimalField(_("sale price"),max_digits=14,decimal_places=4,blank=True,null=True)
    org = models.ForeignKey(Organization,verbose_name=_("organization"),blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):

        return "%s %s" % (self.code,self.name)

    class Meta:
        managed = False
        verbose_name = "物料"
        verbose_name_plural = "物料"
        ordering = ['tp','code']


class MaterialParam(models.Model):
    """

    """
    material = models.ForeignKey(Material,on_delete=models.CASCADE)
    param_value = models.ForeignKey(TechnicalParameterValue,on_delete=models.CASCADE)
    param_name = models.ForeignKey(TechnicalParameterName,blank=Trade,null=True,on_delete=models.CASCADE)
    creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return '%s' % self.param_value

    class Meta:
        managed = False
        verbose_name = "物料参数"
        verbose_name_plural = "物料参数"


class ExtraParam(models.Model):
    """

    """
    DATA_TYPE = (
        ('CHAR',_('CHAR')),
        ('NUM',_('NUMBER')),
        ('DATE',_('DATE')),
    )
    material = models.ForeignKey(Material,verbose_name=_("material"),on_delete=models.CASCADE)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_40)
    data_type = models.CharField(_("data type"),default='CHAR',choices=DATA_TYPE,max_length=const.DB_CHAR_CODE_6)
    data_source = models.CharField(_("data source"),blank=True,null=True,max_length=const.DB_CHAR_NAME_40)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        managed = False
        verbose_name = "扩展参数"
        verbose_name_plural = "扩展参数"


class ExpenseAccount(generic.BO):
    """
    费用科目
    """
    CATEGORY = (
        ('HR',_('HR-DOMAIN')),
        ('OF',_('OFFICE-DOMAIN')),
        ('PU',_('PUBLIS-DOMAIN')),
        ('MU',_('MUNADOMAIN')),
        ('BU',_('BUSINESS')),
        ('OT',_('OTHER')),
    )
    index_weight = 10
    code = models.CharField(_("code"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_120)
    category = models.CharField(_("category"),max_length=const.DB_CHAR_CODE_4,choices=CATEGORY,default='PU')
    description = models.TextField(_("description"),blank=True,null=True)
    parent = models.ForeignKey('self',verbose_name=_("parent"),null=True,blank=True,on_delete=models.CASCADE)
    status = models.BooleanField(_("in use"),default=True)
    org = models.ForeignKey(Organization,verbose_name=_("organization"),blank=True,null=True,on_delete=models.CASCADE)

    class Meta:
        managed = False
        verbose_name = "费用科目"
        verbose_name_plural ="费用科目"
        ordering = ['category','code']


class Employee(generic.BO):
    """
    职员信息
    """
    index_weight = 2
    code = models.CharField(_("employee number"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    phone = models.CharField(_("phone"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    organization = models.ForeignKey(Organization,verbose_name = _('organization'),null=True,blank=True,on_delete=models.CASCADE)
    name = models.CharField(_("employee name"),max_length=const.DB_CHAR_NAME_120)
    pinyin = models.CharField(_("pinyin"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    birthday = models.DateField(_("birthday"),blank=True,null=True)

    gender = models.CharField(_("gender"),max_length=const.DB_CHAR_CODE_2,choices=const.get_value_list('gender'),default='1')
    idcard = models.CharField(_("id card"),max_length=const.DB_CHAR_NAME_20)

    country = models.CharField(_("nationality"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,default='CN',choices=const.get_value_list('S022'))
    hometown = models.CharField(_("hometown"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    address = models.CharField(_("home address"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    banknum = models.CharField(_("bank account"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    bankname = models.CharField(_("bank name"),max_length=const.DB_CHAR_NAME_80,blank=True,null=True)
    emergency = models.CharField(_("emergency contacts"),max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    email = models.CharField(_("email"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    office = models.CharField(_("office phone"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)

    position = models.ForeignKey(Position,verbose_name = _('position'),on_delete=models.CASCADE)
    rank = models.CharField(_("employee rank"),max_length=const.DB_CHAR_CODE_2,default='00',choices=const.get_value_list('S017'))

    workday = models.DateField(_("workday"),blank=True,null=True)
    startday = models.DateField(_("start date"),blank=True,null=True)

    religion = models.CharField(_("religion"),max_length=const.DB_CHAR_CODE_2,default='00',choices=const.get_value_list('S020'),blank=True,null=True,)
    marital = models.CharField(_("marital status"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S023'),default='10')

    party = models.CharField(_("political party"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S026'),default='13')
    nation = models.CharField(_("nation"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S021'),default='01')

    ygxs = models.CharField(_("employ ygxs"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S019'),default='2')
    status = models.CharField(_("employ status"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S016'),default='10')
    category = models.CharField(_("employ category"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S018'),default='21')

    literacy = models.CharField(_("literacy"),max_length=const.DB_CHAR_CODE_2,default='10',choices=const.get_value_list('S024'),blank=True,null=True)
    major = models.CharField(_("major type"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S038'),default='99')
    degree = models.CharField(_("major degree"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S037'),default='4')

    spjob = models.CharField(_("special job"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S042'),default='00')
    health = models.CharField(_("health"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S043'),default='1')

    tag1 = models.CharField(_("tag1 fzjr"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S039'),default='99')
    tag2 = models.CharField(_("tag2 dwld"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S040'),default='9')
    tag3 = models.CharField(_("tag3 dsjs"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S041'),default='00')
    tag4 = models.CharField(_("tag4 byzk"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S027'),default='0')

    user = models.ForeignKey(User,verbose_name=_("user"),blank=True,null=True,on_delete=models.CASCADE)

    def age(self):
        import datetime
        if self.birthday:
            cnt = datetime.date.today().year-self.birthday.year
            return cnt

    def work_age(self):
        import datetime
        if self.birthday and self.workday:
            cnt = datetime.date.today().year-self.workday.year
            return cnt

    def __str__(self):
        return u'%s %s'%(self.code,self.name)

    age.short_description = u'年龄'
    work_age.short_description = u'工龄'

    class Meta:
        managed = False
        verbose_name = "职员信息"
        verbose_name_plural = "职员信息"
        permissions = (
            ('view_all_employee',_("view all employee")),
        )


class Family(generic.BO):
    """
    家庭成员
    """
    relation = models.CharField(_("family title"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S025'))
    status = models.CharField(_("social status"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S029'),default='17')
    name = models.CharField(_("name"),max_length=const.DB_CHAR_NAME_60)
    birthday = models.DateField(_("birthday"),blank=True,null=True)
    organization = models.CharField(_("organization"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    phone = models.CharField(_("phone"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    emergency = models.BooleanField(_("emergency"),default=False)
    employee = models.ForeignKey(Employee,verbose_name=_("employee"),on_delete=models.CASCADE)

    class Meta:
        managed = False
        verbose_name = "家庭成员"
        verbose_name_plural = "家庭成员"


class Education(generic.BO):
    """
    教育履历
    """
    edu_type = models.CharField(_("edu type"),max_length=const.DB_CHAR_CODE_2,choices=const.get_value_list('S035'),default='1')
    school = models.CharField(_("school"),max_length=const.DB_CHAR_NAME_120)
    major = models.CharField(_("major"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    degree = models.CharField(_("major degree"),max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=const.get_value_list('S037'),default='4')
    employee = models.ForeignKey(Employee,verbose_name=_("employee"),on_delete=models.CASCADE)

    class Meta:
        managed = False
        verbose_name = "教育履历"
        verbose_name_plural = "教育履历"


class WorkExperience(generic.BO):
    """
    工作履历
    """
    organization = models.CharField(_("organization"),max_length=const.DB_CHAR_NAME_120)
    position = models.CharField(_("position"),max_length=const.DB_CHAR_NAME_120)
    employee = models.ForeignKey(Employee,verbose_name=_("employee"),on_delete=models.CASCADE)

    class Meta:
        managed = False
        verbose_name = "工作履历"
        verbose_name_plural = "工作履历"


class DataImport(generic.BO):

    """
    Data import
    """
    actions = {}

    STATUS = (
        ('0',"新建"),
        ('1',"已执行"),
    )
    imp_date = models.DateField("日期",blank=True,null=True,default=datetime.datetime.today)
    title = models.CharField("标题",max_length=const.DB_CHAR_NAME_40)
    description = models.TextField("描述信息",blank=True,null=True)
    content_type = models.ForeignKey(ContentType,verbose_name="内容类型",limit_choices_to={"app_label__in":['basedata','organ','auth']},on_delete=models.CASCADE)
    attach = models.FileField("附件",blank=True,null=True,upload_to='data')
    is_clear = models.BooleanField( "清除旧数据？",default=0)
    handler = models.CharField("处理类",max_length=const.DB_CHAR_NAME_80,blank=True,null=True)
    status = models.CharField("状态",max_length=const.DB_CHAR_CODE_2,default='0',choices=STATUS)

    def action_import(self,request):
        from django.db import transaction
        if self.attach:
            if self.handler:
                klass = ExcelManager().handlers.get(self.handler)
                with transaction.atomic():
                    klass.handle(self,self.attach)
                    self.status = 1
                    self.save()
            else:
                import xlrd
                import os
                from LUERP import settings
                path = os.path.join(settings.MEDIA_ROOT,self.attach.name)
                workbook = xlrd.open_workbook(path)
                sheet = workbook.sheet_by_index(0)
                row_count = sheet.nrows
                col_count = sheet.ncols
                cols = []
                with transaction.atomic():
                    for row_index in range(row_count):
                        line = sheet.row_values(row_index)
                        if row_index == 0:
                            cols = line
                            continue
                        elif row_index == 1:
                            continue
                        else:
                            klass = self.content_type.model_class()
                            values = line
                            params = {}
                            for name in cols:
                                index = cols.index(name)
                                v = values[index]
                                if type(v) == str:
                                    v = force_text(v.decode('gbk'))
                                params[name]=v
                                # print 'name is %s value is %s'%(name,v)
                            try:
                                params.pop('')
                            except Exception :
                                pass
                            # print params
                            klass.objects.create(**params)
                    self.status = '1'
                    self.save()

    class Meta:
        managed = False
        verbose_name ="导入"
        verbose_name_plural ="导入"


