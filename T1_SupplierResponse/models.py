from django.db import models
from django.contrib import admin
from django.db import connection
import cx_Oracle
from django.utils.html import format_html

class ooag_t(models.Model):
    ooag011 = models.CharField('姓名', max_length=10)
    ooagent = models.CharField('企业编号', max_length=10)
    ooag001 = models.CharField('员工编号',primary_key=True, max_length=10,unique=True)
    ooag003 = models.CharField('归属部门', max_length=10)
    ooag004 = models.CharField('歸屬營運據點', max_length=10)
    ooag005 = models.CharField('職稱', max_length=10)
    ooag006 = models.CharField('銀行行號/郵局局號', max_length=50)
    ooag007 = models.CharField('帳號', max_length=50)
    ooag015 = models.CharField('员工核决层级', max_length=10)
    ooag016 = models.BooleanField('启用代理人')
    ooag017 = models.CharField('代理人员工编号', max_length=10)
    ooagstus = models.CharField('状态码', max_length=10)
    ooagmoddt = models.DateField('最近修改如')

    class Meta:
        managed = False
        app_label = 'T1_SupplierResponse'
        db_table = 'ooag_t'
        verbose_name = "员工编号"
        verbose_name_plural = verbose_name
        ordering = ['ooag001']

    def __str__(self):
         return self.ooag011

class pmaal_t(models.Model):

    pmaal004 = models.CharField('供应商简称', max_length=20,editable=False)
    pmaal003 = models.CharField('供应商全称', max_length=20,editable=False)
    pmaal002 = models.CharField('语言', max_length=10,editable=False)
    pmaal001 = models.CharField('供应商编码', max_length=10,primary_key=True,editable=False,unique=True)
    pmaalent = models.CharField('企业编号', max_length=10,editable=False)

    class Meta:
        managed = False
        app_label = 'T1_SupplierResponse'
        db_table = 'pmaal_t'
        verbose_name = "供应商"
        verbose_name_plural = verbose_name
        ordering = ['pmaal001']

    def __str__(self):
        return self.pmaal004

class imaal_t(models.Model):
    imaal001 = models.CharField('品号', max_length=20,primary_key=True,unique=True)
    imaal003 = models.CharField('名称', max_length=100)
    imaal004 = models.CharField('规格', max_length=100)
    imaalent = models.CharField('企业代码', max_length=20)

    def __str__(self):
        return "%s,%s,%s" % (self.imaal001,self.imaal003,self.imaal004)

    class Meta:
        managed = False
        app_label = 'T1_SupplierResponse'
        db_table = 'imaal_t'
        verbose_name = "品号名称"
        verbose_name_plural = verbose_name
        ordering = ['imaal001']

class oofc_t(models.Model):
    oofc008 = models.CharField('通訊類型', max_length=20,primary_key=True,unique=True)
    oofc003 = models.CharField('聯絡對象', max_length=100)
    oofc012 = models.CharField('邮箱', max_length=100)
    oofc011 = models.CharField('簡要說明', max_length=20)
    oofcstus = models.CharField('狀態碼', max_length=100)
    oofccrtdt = models.CharField('创建日', max_length=100)
    def __str__(self):
        return self.oofc012

    class Meta:
        managed = False
        app_label = 'T1_SupplierResponse'
        db_table = 'oofc_t'
        verbose_name = "通訊方式"
        verbose_name_plural = verbose_name
        #ordering = ['-oofccrtdt']

class pmdl_t(models.Model):
    STATUS = ( ('A', '已核准'), ('C', '结案'), ('D', '抽单'),
        ('F', '已发出'), ('M', '成本结案'), ( 'N', '未审核'),
        ( 'R', '拒绝'), ( 'W', '送签中'), ('X', '作废'),
        ( 'N', '未审核'), ( 'Y', '已审核'), ('E', '终止'),
    )
    CLASSSTATUS = ( ('1', '采购'), ('2', '加工'),)

    pmdldocdt = models.DateField('采购日期')
    pmdldocno = models.CharField('采购单号',primary_key=True, max_length=20,unique=True)
    pmdl025 = models.CharField('送货地址', max_length=100)
    pmdl015 = models.CharField('币种', max_length=10)
    pmdl005 = models.CharField('分类', max_length=10,choices=CLASSSTATUS)
    pmdl044 = models.TextField('备注')
    pmdlstus = models.CharField('状态', max_length=10,choices=STATUS)
    pmdlsite = models.CharField('公司别', max_length=10)
    pmdl004 = models.ForeignKey(to='pmaal_t',verbose_name='供应商', to_field='pmaal001',db_column='pmdl004',on_delete=models.CASCADE,default=1)
    #pmdl004 = models.CharField('供应商', max_length=10)
    pmdl002 = models.ForeignKey(to='ooag_t',verbose_name='采购员', to_field='ooag001',db_column='pmdl002',related_name='+',on_delete=models.PROTECT,default=1)
    #pmdl002 = models.CharField('采购员', max_length=10)
    # objects = PersonManager()
    class Meta:
        managed = False
        app_label = 'T1_SupplierResponse'
        db_table = 'pmdl_t'
        verbose_name = "采购单主表"
        verbose_name_plural = verbose_name
        ordering = ['-pmdldocdt']
    def __str__(self):
        return "%s,%s,%s" % (self.pmdldocno, self.pmdldocdt, self.pmdl044)


class pmdn_t(models.Model):
    ROWSTATUS = ( ('1', '一般'), ('2', '正常结案'),('4', '取消'),)
    JDSTATUS = ( ('1', '一般'), ('2', '正常结案'),('4', '取消'),)

    pmdn002 = models.ForeignKey(pmdl_t,verbose_name='采购单号',to_field="pmdldocno",db_column='pmdndocno',on_delete=models.CASCADE)
    #pmdndocno = models.CharField('单号',primary_key=True, max_length=20,unique=True)
    pmdnseq = models.CharField('序号', max_length=10,primary_key=True,unique=True)
    #pmdn001 = models.ForeignKey(imaal_t,verbose_name='料号', to_field="imaal001",on_delete=models.CASCADE)
    pmdn001 = models.ForeignKey(imaal_t,verbose_name='名称规格', to_field="imaal001",db_column='pmdn001',on_delete=models.CASCADE)
   # pmdn005 = models.ForeignKey(imaal_t,verbose_name='名称规格', to_field="imaal001",db_column='pmdn001',on_delete=models.CASCADE)
    pmdn005 = models.CharField('类别', max_length=10)
    pmdn006 = models.CharField('单位', max_length=10)
    pmdn007 = models.DecimalField('数量',max_digits=14,decimal_places=4)
    pmdn015 = models.DecimalField('单价',max_digits=14,decimal_places=4)
    pmdn012 = models.DateField('出货日期')
    pmdn013 = models.DateField('到厂日期')
    pmdn014 = models.DateField('到庫日期')
    pmdnua004 = models.DateField('供方回复交期')
    pmdnua005 = models.TextField('供方说明')
    pmdnua006 = models.DateTimeField('供方回复时间')
    pmdnua007 = models.CharField('回复人', max_length=20)
    pmdnua026 = models.CharField('PO', max_length=20)
    pmdn025 = models.CharField('收获地址', max_length=120)
    pmdn045 = models.CharField('行状态', max_length=20)
    pmdn020 = models.CharField('紧急度', max_length=20)

    class Meta:
        managed = False
        unique_together = (("pmdn002", "pmdnseq"),)
        app_label = 'T1_SupplierResponse'
        db_table = 'pmdn_t'
        verbose_name = "采购单子表"
        verbose_name_plural = verbose_name
        ordering = ['-pmdn012']
        #proxy = True  # 设置为True 否则会重新注册一张数据表
        #list_select_related = True


class pmdo_t(models.Model):
    pmdo019 = models.DecimalField('已入庫量',max_digits=14,decimal_places=4)
    pmdo021 = models.DecimalField('交货状态',max_digits=14,decimal_places=4)
    pmdo015 = models.DecimalField('已收貨量',max_digits=14,decimal_places=4)
    pmdo016 = models.DecimalField('驗退量',max_digits=14,decimal_places=4)
    class Meta:
        managed = False
        app_label = 'T1_SupplierResponse'
        db_table = 'pmdo_t'
        verbose_name = "采购交期明细档"
        verbose_name_plural = verbose_name
        ordering = ['pmdo019']



# class yxhst20190325(models.Model):
#     全称 = models.CharField(max_length=40,null=True)
#     采购单号 = models.CharField('采购单号',max_length=20,null=True)
#     采购单别 = models.CharField('采购单别',max_length=20,null=True)
#     序号 = models.CharField('序号',max_length=20)
#     采购日期 = models.DateTimeField('采购日期',null=True)
#     简称 = models.CharField(max_length=20)
#     品号 = models.CharField(max_length=20,null=True)
#     品名 = models.CharField(max_length=120,null=True)
#     规格 = models.CharField(max_length=120,null=True)
#     计量单位 = models.CharField(max_length=6,null=True)
#     采购量 = models.DecimalField(max_digits=14,decimal_places=4,null=True)
#     已交数量 = models.DecimalField(max_digits=14,decimal_places=4,null=True)
#     未交量 = models.DecimalField(max_digits=14,decimal_places=4,null=True)
#     币别 = models.CharField(max_length=10,null=True)
#     采购单价 = models.DecimalField(max_digits=14,decimal_places=4,null=True)
#     税率 = models.DecimalField(max_digits=14,decimal_places=4,null=True)
#     未交未税金额 = models.DecimalField(max_digits=14,decimal_places=2,null=True)
#     税额 = models.DecimalField(max_digits=14,decimal_places=4,null=True)
#     未交含税金额 = models.DecimalField(max_digits=14,decimal_places=4,null=True)
#     分类 = models.CharField(max_length=20,null=True)
#     预交日 = models.DateField(null=True)
#     来源单号 = models.CharField(max_length=20,null=True)
#     PO = models.CharField(max_length=20,null=True)
#     采购人员 = models.CharField(max_length=20,null=True)
#     审核者 = models.CharField(max_length=20,null=True)
#     tao料号 = models.CharField(max_length=40,null=True)
#     公司 = models.CharField(max_length=40,null=True)
#     供方编号 = models.CharField(max_length=20)
#     采购单号序号 = models.CharField(max_length=60,null=True,primary_key=True)
#     备注 = models.TextField(null=True)
#     供方回复交期 = models.DateField()
#     供方说明 =  models.TextField()
#     回复时间交期 = models.DateTimeField()
#     回复人 =  models.CharField(max_length=20)
#     def sex_color(self):
#         if self.sex == '男':
#             color = '#00F'
#         elif self.sex == '女':
#             color = '#F00'
#         else:
#             color = ''
#         return format_html(
#             '<span style="color: {}">{}</span>',
#             color,
#             self.sex,
#         )
#
#
#     class Meta:
#         managed = False
#         app_label = 'T1_SupplierResponse'
#         db_table = 'yxhst20190325'
#         unique_together = (("采购单号", "采购单别", "序号"),)
#         verbose_name = "采购交期供应商确认"
#         verbose_name_plural = verbose_name
#         ordering = ['-预交日','采购单别']
# Create your models here.
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    desc = cursor.description
    if desc == None:
        return []
    columns = [col[0] for col in desc]
    # for row in cursor.fetchall():
    #     rows.append(row)
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
        ]

def dictfetone(cursor):
    desc = cursor.description
    if desc == None:
        return None
    columns = [col[0] for col in desc]
    row = cursor.fetchone()
    if row == None:
        return None
    return dict(zip(columns, row))

def fetchall(sql, params=[]):
    connection = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
    cursor = connection.cursor()
    cursor.execute(sql, params)
    ret = dictfetchall(cursor)
    return ret

def fetchone(sql, params=[]):
    connection = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
    cursor = connection.cursor()
    cursor.execute(sql, params)
    ret = dictfetone(cursor)
    cursor.close()
    return ret

def executeDb(sql, params=[]):
    connection = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
    cursor = connection.cursor()
    ret = cursor.execute(sql, params)
    cursor.close()
    return ret
