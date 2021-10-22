# coding=utf-8
import datetime
import os
import xlrd
import decimal
from django.db import transaction
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from common import generic
from common import const
from LUERP import settings
from basedata.models import Material,ExtraParam,Project,ExpenseAccount,Measure
from organ.models import OrgUnit


class WorkOrder(generic.BO):
    """

    """
    index_weight = 1
    code = models.CharField( "工单编号",blank=True,null=True,max_length=const.DB_CHAR_CODE_10)
    refer = models.ForeignKey("self",verbose_name="参考工单",blank=True,null=True,on_delete=models.CASCADE)
    title = models.CharField("标题",max_length=const.DB_CHAR_NAME_120)
    description = models.TextField("描述信息",blank=True,null=True)
    business_domain = models.CharField("业务域",max_length=const.DB_CHAR_CODE_4,choices=const.get_value_list('S045'),default='OT')
    classification = models.CharField("分类",max_length=const.DB_CHAR_CODE_4,choices=const.get_value_list('S044'),default='D')
    service = models.ForeignKey(Material,verbose_name="服务名称",null=True,blank=True,limit_choices_to={"is_virtual":"1"},on_delete=models.CASCADE)
    project = models.ForeignKey(Project,verbose_name="项目",null=True,blank=True,on_delete=models.CASCADE)
    status = models.CharField("状态",blank=True,null=True,default='NEW',max_length=const.DB_CHAR_CODE_6,choices=const.get_value_list('S046'))
    answer = models.TextField("答复",blank=True,null=True)
    user = models.ForeignKey(User,verbose_name="用户",blank=True,null=True,on_delete=models.CASCADE)
    attach = models.FileField("附件",blank=True,null=True,help_text=u'工单附件，不导入明细。')
    detail = models.FileField("待导入明细",blank=True,null=True,help_text=u'您可导入需求明细，模板请参考文档FD0007')

    def __str__(self):
        return u"%s-%s" % (self.code,self.title)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(WorkOrder,self).save(force_insert,force_update,using,update_fields)
        if self.service:
            material = self.service
            if self.woextravalue_set.count() < 1 and material.extraparam_set and material.extraparam_set.count() > 0:
                for param in material.extraparam_set.all():
                    extra_param = WOExtraValue.objects.create(workorder=self,param_name=param)
                    self.woextravalue_set.add(extra_param)
        item_count = WOItem.objects.filter(workorder=self).count()
        if self.detail and item_count == 0:
            path = os.path.join(settings.MEDIA_ROOT,self.detail.name)
            workbook = xlrd.open_workbook(path)
            sheet = workbook.sheet_by_index(0)
            row_count = sheet.nrows
            with transaction.atomic():
                for row_index in range(row_count):
                    row = sheet.row_values(row_index)
                    if row_index == 0:
                        doc_type = row[1]
                        if doc_type.startswith('0'):
                            break
                        else:
                            continue
                    elif row_index < 3:
                        continue
                    material = None
                    measure = None
                    try:
                        measure = Measure.objects.get(code=row[4])
                    except Exception:
                        measure = Measure.objects.create(code=row[4],name=force_text(row[5]))
                    try:
                        material = Material.objects.get(code=row[0])
                    except Exception:
                        material = Material(code=row[0],name=force_text(row[1]),spec=force_text(row[2]))
                        material.save()
                    WOItem.objects.create(workorder=self,material=material,measure=measure,amount=row[6])

    class Meta:
        verbose_name = "工单服务"
        verbose_name_plural = "工单服务"

    class Media:
        js = ('js/workorder.js',)


class WOExtraValue(models.Model):
    """

    """
    workorder = models.ForeignKey(WorkOrder,verbose_name="工单",on_delete=models.CASCADE)
    param_name = models.ForeignKey(ExtraParam,verbose_name="扩展参数",on_delete=models.CASCADE)
    param_value = models.CharField("值",blank=True,null=True,max_length=const.DB_CHAR_NAME_40)

    class Meta:
        verbose_name = "扩展信息"
        verbose_name_plural = "扩展信息"


class WOItem(models.Model):
    """

    """
    workorder = models.ForeignKey(WorkOrder,verbose_name="工单",on_delete=models.CASCADE)
    material = models.ForeignKey(Material,verbose_name= "物料",null=True,blank=True,limit_choices_to={"is_virtual":"0"},on_delete=models.CASCADE)
    amount = models.DecimalField("数量",max_digits=10,decimal_places=4,blank=True,null=True)
    measure = models.ForeignKey(Measure,verbose_name="计量单位",blank=True,null=True,on_delete=models.CASCADE)
    price = models.DecimalField( "单价",max_digits=10,decimal_places=4,blank=True,null=True)

    class Meta:
        verbose_name = "工单明细"
        verbose_name_plural = "工单明细"


class Loan(generic.BO):
    """

    """
    LOAD_STATUS = (
        ('N', "新建"),
        ('I',"IN PROGRESS"),
        ('A',"APPROVED"),
        ('P',"已支付")
    )
    index_weight = 3
    code = models.CharField("单据编号",max_length=const.DB_CHAR_CODE_10,blank=True,null=True)
    title = models.CharField("标题",max_length=const.DB_CHAR_NAME_120)
    description = models.TextField("描述信息",blank=True,null=True)
    project = models.ForeignKey(Project,verbose_name="项目",on_delete=models.CASCADE)
    user = models.ForeignKey(User,verbose_name="用户",blank=True,null=True,on_delete=models.CASCADE)
    status = models.CharField("状态",blank=True,null=True,default='N',max_length=const.DB_CHAR_CODE_2,choices=LOAD_STATUS)
    logout_time = models.DateTimeField("核销时间",blank=True,null=True)
    loan_amount = models.DecimalField("借款金额",max_digits=10,decimal_places=2,blank=True,null=True)
    logout_amount = models.DecimalField( "核销金额",max_digits=10,decimal_places=2,blank=True,null=True)
    pay_user = models.CharField("支付人",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    pay_time = models.DateTimeField("支付时间",blank=True,null=True)
    is_clear = models.BooleanField("全部核销",default=False)

    def __str__(self):
        import decimal
        left = self.loan_amount
        left -= self.logout_amount or decimal.Decimal(0.00)
        name = '%s%s'%(self.user.last_name,self.user.first_name)
        return '%s %s %s J:%.2f Y:%.2f' % (self.code,name,self.title,self.loan_amount,left)

    def applier(self):
        return u'%s%s'%(self.user.last_name,self.user.first_name)

    applier.short_description = "申请人"

    def action_pay(self,request):
        self.pay_time = datetime.datetime.now()
        self.pay_user = request.user.username
        self.status = 'P'
        self.save()

    class Meta:
        verbose_name = "借款申请"
        verbose_name_plural ="借款申请"
        permissions = (
            ('financial_pay',_("financial pay")),
        )


class Reimbursement(generic.BO):
    """

    """
    REIM_STATUS = (
        ('N',"新建"),
        ('I',"处理中"),
        ('A',"已批准"),
        ('P',"已支付")
    )
    index_weight = 2
    code = models.CharField( "单据编号",max_length=const.DB_CHAR_CODE_10,blank=True,null=True)
    title = models.CharField("标题",max_length=const.DB_CHAR_NAME_120)
    description = models.TextField("描述信息",blank=True,null=True)
    project = models.ForeignKey(Project,verbose_name="项目",on_delete=models.CASCADE)
    wo = models.ForeignKey(WorkOrder,verbose_name="工单",null=True,blank=True,on_delete=models.CASCADE)
    user = models.ForeignKey(User,verbose_name="用户",blank=True,null=True,on_delete=models.CASCADE)
    org = models.ForeignKey(OrgUnit,verbose_name="成本中心",blank=True,null=True,on_delete=models.CASCADE)
    bank_account = models.CharField("银行账户",max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    status = models.CharField( "状态",blank=True,null=True,default='N',max_length=const.DB_CHAR_CODE_2,choices=REIM_STATUS)
    amount = models.DecimalField("金额",max_digits=10,decimal_places=2,blank=True,null=True)
    loan = models.ForeignKey(Loan,verbose_name="借款单据",blank=True,null=True,on_delete=models.CASCADE)
    loan_amount = models.DecimalField( "借款金额",max_digits=10,decimal_places=2,blank=True,null=True)
    logout_amount = models.DecimalField("核销金额",max_digits=10,decimal_places=2,blank=True,null=True)
    pay_amount = models.DecimalField("支付金额",max_digits=10,decimal_places=2,blank=True,null=True)
    pay_time = models.DateTimeField("付款日期",blank=True,null=True)
    pay_user = models.CharField("付款用户",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)

    def applier(self):
        return u'%s%s'%(self.user.last_name,self.user.first_name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        import decimal
        if self.loan:
            left = self.loan.loan_amount
            left -= self.loan.logout_amount or decimal.Decimal(0.00)
            if self.logout_amount is None or self.logout_amount == '':
                if self.amount < left:
                    self.logout_amount = self.amount
                else:
                    self.logout_amount = left
        self.pay_amount = self.amount
        if self.logout_amount:
            self.pay_amount -= self.logout_amount
        super(Reimbursement,self).save(force_insert,force_update,using,update_fields)

    def action_pay(self,request):
        if self.loan:
            if self.logout_amount is None or self.logout_amount == '':
                self.logout_amount = self.amount
            if self.logout_amount < 0:
                raise Exception(u'核销金额小于0')

            if self.loan.logout_amount is None:
                self.loan.logout_amount = self.logout_amount
            else:
                self.loan.logout_amount += self.logout_amount

            if self.loan.loan_amount == self.loan.logout_amount:
                self.loan.is_clear=True

            self.loan.logout_time = datetime.datetime.now()
            self.loan.save()

        if self.amount > self.logout_amount:
            self.pay_amount = self.amount - self.logout_amount

        self.pay_time = datetime.datetime.now()
        self.pay_user = request.user.username
        self.status = 'P'
        self.save()

    applier.short_description = "申请人"

    class Meta:
        verbose_name = "费用报销"
        verbose_name_plural = "费用报销"
        permissions = (
            ('financial_pay',"财务支付"),
        )


class ReimbursementItem(models.Model):
    """

    """
    import datetime
    reimbursement = models.ForeignKey(Reimbursement,verbose_name="费用报销",on_delete=models.CASCADE)
    expense_account = models.ForeignKey(ExpenseAccount,verbose_name="费用科目",on_delete=models.CASCADE)
    begin = models.DateField( "发生日期",default=datetime.date.today)
    amount = models.DecimalField("金额",max_digits=10,decimal_places=2)
    memo = models.CharField("备注",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(ReimbursementItem,self).save(force_insert,force_update,using,update_fields)
        sql = 'UPDATE selfhelp_reimbursement SET amount = (SELECT SUM(amount) FROM selfhelp_reimbursementitem WHERE reimbursement_id = %s) WHERE id = %s'
        params = [self.reimbursement.id,self.reimbursement.id]
        generic.update(sql,params)

    class Meta:
        verbose_name = "费用明细"
        verbose_name_plural = "费用明细"


class Activity(generic.BO):
    """

    """
    CLASSIFICATION = (
        ('T', "培训"),
        ('M',"会议"),
        ('G',"集体活动"),
    )
    index_index_weight = 4
    begin_time = models.DateTimeField("开始时间")
    end_time = models.DateTimeField("结束时间")
    enroll_deadline = models.DateTimeField("报名截止日期",blank=True,null=True)
    code = models.CharField("编号",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    title = models.CharField("标题",max_length=const.DB_CHAR_NAME_120)
    parent = models.ForeignKey('self',verbose_name="父级",blank=True,null=True,on_delete=models.CASCADE)
    description = models.TextField("描述信息",blank=True,null=True)
    host = models.CharField( "主持人",max_length=const.DB_CHAR_NAME_80,blank=True,null=True)
    speaker = models.CharField("主讲人",max_length=const.DB_CHAR_NAME_80,blank=True,null=True)
    accept_enroll = models.BooleanField("接受报名",default=1)
    room = models.ForeignKey(Material,verbose_name= "房间/会议室",blank=True,null=True,limit_choices_to={'tp':20},on_delete=models.CASCADE)
    location = models.CharField("位置",max_length=const.DB_CHAR_NAME_80,blank=True,null=True)
    classification = models.CharField("分类",max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=CLASSIFICATION,default='M')
    mail_list = models.TextField("邮件组",blank=True,null=True)
    mail_notice = models.BooleanField("邮件通知",default=1)
    short_message_notice = models.BooleanField("短信通知？",default=1)
    weixin_notice = models.BooleanField("微信通知",default=1)
    status = models.BooleanField("已发布",default=0)
    publish_time = models.DateTimeField("发布时间",blank=True,null=True)
    attach = models.FileField("附件",blank=True,null=True,upload_to='activity')

    class Meta:
        verbose_name = "活动"
        verbose_name_plural = "活动"


class Feedback(models.Model):
    """

    """
    RANK = (
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D'),
    )
    activity = models.ForeignKey(Activity,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    feed_time = models.DateTimeField("反馈时间",auto_now_add=True)
    rank = models.CharField("排列",max_length=const.DB_CHAR_CODE_2,blank=True,null=True,choices=RANK,default='B')
    comment = models.CharField("建议",blank=True,null=True,max_length=const.DB_CHAR_NAME_80)


class Enroll(models.Model):
    """

    """
    activity = models.ForeignKey(Activity,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    enroll_time = models.DateTimeField("登记时间",auto_now_add=True)
