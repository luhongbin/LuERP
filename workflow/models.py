# coding=utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from common import const
from syscfg.models import Role
from organ.models import Position, OrgUnit


class Modal(models.Model):
    """

    """
    import datetime
    index_weight = 1
    code = models.CharField("编号", max_length=const.DB_CHAR_CODE_6, blank=True, null=True)
    name = models.CharField("工作流名称", max_length=const.DB_CHAR_NAME_40, blank=True, null=True)
    description = models.TextField("描述信息", blank=True, null=True)
    content_type = models.ForeignKey(ContentType, verbose_name="内容类型", limit_choices_to={"app_label__in": ['basedata', 'organ']}, on_delete=models.CASCADE)
    app_name = models.CharField("应用名称", max_length=const.DB_CHAR_NAME_60, blank=True, null=True)
    model_name = models.CharField("模型名称", max_length=const.DB_CHAR_NAME_60, blank=True, null=True)
    begin = models.DateField("开始时间", blank=True, null=True, default=datetime.date.today)
    end = models.DateField("结束时间", blank=True, null=True, default=datetime.date(9999, 12, 31))

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "工作流模型"
        verbose_name_plural = "工作流模型"


class Node(models.Model):
    """
    submitter()
    upper()
    user()
    role()
    position()
    sql()
    """
    HANDLER_TYPE = (
        (1, "指定用户"),
        (2, "指定岗位"),
        (3, "指定角色"),
        (4, "提交人"),
    )
    index_weight = 2
    modal = models.ForeignKey(Modal,verbose_name="工作流模型", on_delete=models.CASCADE)
    code = models.CharField("节点编号", max_length=const.DB_CHAR_CODE_4, blank=True, null=True)
    name = models.CharField("节点名称", max_length=const.DB_CHAR_NAME_80)
    tooltip = models.CharField("提示语", blank=True, null=True, max_length=const.DB_CHAR_NAME_120)

    start = models.BooleanField("起始节点？", default=False)
    stop = models.BooleanField("结束节点？", default=False)
    can_terminate = models.BooleanField("允许终止？", default=False)
    can_deny = models.BooleanField( "允许拒绝？", default=True)
    can_edit = models.BooleanField("可编辑？", default=False)
    can_restart = models.BooleanField("可重启工作流？", default=False)

    email_notice = models.BooleanField("邮件通知？", default=True)
    short_message_notice = models.BooleanField("短信通知？", default=False)
    approve_node = models.BooleanField("批准节点", default=False)
    handler = models.TextField("处理人", blank=True, null=True, help_text=u'自定义SQL语句，优先高于指定用户、岗位、角色')
    handler_type = models.IntegerField("处理人类型", choices=HANDLER_TYPE, default=1)
    positions = models.ManyToManyField(Position, verbose_name="指定岗位", blank=True)
    roles = models.ManyToManyField(Role, verbose_name="指定角色", blank=True)
    users = models.ManyToManyField(User, verbose_name="指定用户", blank=True)
    departments = models.ManyToManyField(OrgUnit, verbose_name="部门范围", blank=True)
    next = models.ManyToManyField('self', blank=True, verbose_name="下一节点", symmetrical=False)
    next_user_handler = models.CharField("next用户处理类", blank=True, null=True, max_length=const.DB_CHAR_NAME_40)
    next_node_handler = models.CharField("next节点处理类", blank=True, null=True, max_length=const.DB_CHAR_NAME_40)
    status_field = models.CharField("状态字段", blank=True, null=True, max_length=const.DB_CHAR_NAME_40)
    status_value = models.CharField("状态值", blank=True, null=True, max_length=const.DB_CHAR_NAME_40)
    action = models.CharField("执行动作", blank=True, null=True, max_length=const.DB_CHAR_NAME_40)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.code:
            fmt = 'N%02d'
            self.code = fmt % (self.modal.node_set.count()+1)
        super(Node,self).save(force_insert,force_update,using,update_fields)

    def __str__(self):
        return "%s-%s" % (self.code, self.name)

    class Meta:
        verbose_name = "工作流节点"
        verbose_name_plural = "工作流节点"


class Instance(models.Model):
    """

    """
    STATUS = (
        (1, "新建"),
        (2, "处理中"),
        (3, "拒绝"),
        (4, "已终止审批"),
        (9, "已批准"),
        (99, "完成")
    )
    index_weight = 3
    code = models.CharField("编号", blank=True, null=True, max_length=const.DB_CHAR_CODE_10)
    modal = models.ForeignKey(Modal, verbose_name="工作流模型", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField("对象清单 id")
    starter = models.ForeignKey(User, verbose_name="提交人", related_name="starter", on_delete=models.CASCADE)
    start_time = models.DateTimeField("提交时间", auto_now_add=True)
    approved_time = models.DateTimeField("批准时间", blank=True, null=True)
    status = models.IntegerField("状态", default=1, choices=STATUS)
    current_nodes = models.ManyToManyField(Node, verbose_name="当前节点", blank=True)

    def __str__(self):
        return '%s' % self.code

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Instance, self).save(force_insert, force_update, using, update_fields)
        if not self.code:
            self.code = 'S%05d' % self.id
            self.save()

    class Meta:
        verbose_name = "工作流实例"
        verbose_name_plural = "工作流实例"


class History(models.Model):
    """
    workflow history
    """
    PROCESS_TYPE = (
        (0, "提交"),
        (1, "同意"),
        (3, "拒绝"),
        (4, "终止"),
    )
    index_weight = 5
    inst = models.ForeignKey(Instance, verbose_name="工作流实例", on_delete=models.CASCADE)
    node = models.ForeignKey(Node, verbose_name="工作流节点", blank=True,null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="提交人", on_delete=models.CASCADE)
    pro_time = models.DateTimeField("处理时间", auto_now_add=True)
    pro_type = models.IntegerField("处理类型", choices=PROCESS_TYPE, default=0)
    memo = models.CharField("备注", max_length=const.DB_CHAR_NAME_40, blank=True, null=True)

    def get_node_desc(self):
        if self.node:
            return self.node.name
        else:
            return u'启动'

    def get_action_desc(self):
        action_mapping = {0: u'提交', 1: u'同意', 3: u'拒绝', 4: u'终止', }
        # print action_mapping
        if self.pro_type:
            return action_mapping[self.pro_type]
        else:
            return u'提交'

    def get_memo_desc(self):
        if self.memo:
            return self.memo
        else:
            return ''

    class Meta:
        verbose_name = "审批记录"
        verbose_name_plural = "审批记录"
        ordering = ['inst', 'pro_time']


class TodoList(models.Model):
    """

    """
    index_weight = 4
    code = models.CharField("编号", max_length=const.DB_CHAR_CODE_10, blank=True , null=True)
    inst = models.ForeignKey(Instance, verbose_name="工作流实例", on_delete=models.CASCADE)
    node = models.ForeignKey(Node, verbose_name="当前节点", blank=True, null=True, on_delete=models.CASCADE)
    app_name = models.CharField("应用名称", max_length=const.DB_CHAR_NAME_60, blank=True, null=True)
    model_name = models.CharField("模型名称", max_length=const.DB_CHAR_NAME_60, blank=True, null=True)
    user = models.ForeignKey(User, verbose_name="处理人", on_delete=models.CASCADE)
    arrived_time = models.DateTimeField("到达时间", auto_now_add=True)
    is_read = models.BooleanField("已阅？", default=False)
    read_time = models.DateTimeField("阅读时间", blank=True, null=True)
    status = models.BooleanField("已办？", default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(TodoList, self).save(force_update, force_update, using, update_fields)
        if not self.code:
            self.code = 'TD%05d' % self.id
            self.save()

    def node_dsc(self):
        if self.node:
            return u'%s' % self.node.name
        else:
            return u'启动'

    def code_link(self):
        return format_html("<a href='/admin/{}/{}/{}'>{}</a>",
                           self.app_name, self.model_name, self.inst.object_id, self.code)
    code_link.allow_tags = True
    code_link.short_description = "编号"

    def href(self):
        ct = ContentType.objects.get(app_label=self.app_name, model=self.model_name)
        obj = ct.get_object_for_this_type(id=self.inst.object_id)
        title = u"%s" % (obj)
        return format_html("<a href='/admin/{}/{}/{}'>{}</a>",
                           self.app_name,self.model_name,self.inst.object_id,title)
    def modal_dsc(self):
        return u'%s' % (self.inst.modal.name)
    modal_dsc.short_description = u'业务流程'

    def start_time(self):
        return self.inst.start_time.strftime('%Y-%m-%d %H:%M')

    href.allow_tags = True
    href.short_description = "描述信息"
    node_dsc.short_description = "当前节点"

    def submitter(self):
        if self.inst.starter.last_name or self.inst.starter.first_name:
            return u"%s%s" % (self.inst.starter.last_name, self.inst.starter.first_name)
        return u"%s" % (self.inst.starter.username)
    submitter.short_description ="提交人"

    class Meta:
        verbose_name = "待办任务"
        verbose_name_plural = "待办任务"
        ordering = ['user', '-arrived_time']


def get_modal(app_label,model_name):
    """

    :param app_label:
    :param model_name:
    :return:
    """
    try:
        return Modal.objects.get(app_name=app_label,model_name=model_name)
    except Exception:
        return None


def get_instance(obj):
    """

    :param obj:
    :return:
    """
    if obj and obj._meta:
        modal = get_modal(obj._meta.app_label,obj._meta.model_name)
        if modal:
            try:
                return Instance.objects.get(modal=modal,object_id=obj.id)
            except Exception:
                return None
    else:
        return None
