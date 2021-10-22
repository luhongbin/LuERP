# coding=utf-8
from django.db import models
from django.db import connection
from django.utils.translation import ugettext_lazy as _
from common import const
from common import generic


class Organization(generic.BO):
    """
    组织单位
    """
    index_weight = 1
    code = models.CharField("机构编号",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    name = models.CharField("机构名称",max_length=const.DB_CHAR_NAME_120)
    short = models.CharField("简称",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    pinyin = models.CharField("拼音/英语",max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    status = models.BooleanField("在用？",default=True)

    tax_num = models.CharField( "纳税识别号",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    tax_address = models.CharField("开票地址/电话",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    tax_account = models.CharField( "发票开户行",max_length=const.DB_CHAR_NAME_80,blank=True,null=True)

    represent = models.CharField("法人代表",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    address = models.CharField("地址",max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    zipcode = models.CharField( "邮编",max_length=const.DB_CHAR_CODE_8,blank=True,null=True)
    fax = models.CharField("传真",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    contacts = models.CharField( "联系人",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    phone = models.CharField("联系电话",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    website = models.CharField( "网址",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    email = models.CharField("邮箱",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    lic_code = models.CharField("营业执照代码",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    cer_code = models.CharField("组织机构代码",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    license = models.FileField( "营业执照",blank=True,null=True,upload_to='organ')
    certificate = models.FileField("组织机构证书",blank=True,null=True,upload_to='organ')
    weight = models.IntegerField("排序权重",default=9)

    class Meta:
        verbose_name = "组织机构"
        verbose_name_plural = "组织机构"


class OrgUnit(generic.BO):
    """
    组织单元
    """
    UNIT_LEVEL = (
        (1,"分公司/事业部"),
        (2,"一级部门"),
        (3, "二级部门/处室/科室"),
        (4,"组/班"),
        (5,"委员会")
    )
    index_weight = 2
    parent = models.ForeignKey('self',verbose_name="父级",on_delete=models.CASCADE, null=True,blank=True)
    organization = models.ForeignKey(Organization,verbose_name = "组织机构",on_delete=models.CASCADE, null=True,blank=True)
    code = models.CharField("编号",max_length=const.DB_CHAR_CODE_8,blank=True,null=True)
    name = models.CharField("名称",max_length=const.DB_CHAR_NAME_120)
    short = models.CharField("简称",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    pinyin = models.CharField("拼音/英语",max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    unit_type = models.IntegerField("类别",choices=UNIT_LEVEL,default=2)
    status = models.BooleanField("在用？",default=True)
    virtual = models.BooleanField("虚拟？",default=False)
    fax = models.CharField("传真",max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    phone = models.CharField( "联系电话",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    contacts = models.CharField("联系人",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    email = models.CharField("邮箱",max_length=const.DB_CHAR_NAME_40,blank=True,null=True)
    weight = models.IntegerField("排序权重",default=99)

    class Meta:
        verbose_name = "组织单元"
        verbose_name_plural = "组织单元"


class Position(generic.BO):
    """
    岗位
    """
    SERIES = (
        ('A',"管理类"),
        ('S',"营销类"),
        ('T',"技术类"),
        ('P', "生产/操作类"),
    )

    GRADE = (
        ('01', "基础"),
        ('02', "中等"),
        ('03',  "高级"),
        ('04', "教授"),
        ('05', "专家"),
    )
    index_weight = 3
    unit = models.ForeignKey(OrgUnit,verbose_name=_('org unit'),on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization,verbose_name=_('organization'),on_delete=models.CASCADE, null=True,blank=True)
    parent = models.ForeignKey('self',verbose_name=_("parent"),on_delete=models.CASCADE, null=True,blank=True)
    code = models.CharField(_("position code"),max_length=const.DB_CHAR_CODE_8,blank=True,null=True)
    name = models.CharField(_("position name"),max_length=const.DB_CHAR_NAME_120)
    short = models.CharField(_("short name"),max_length=const.DB_CHAR_NAME_20,blank=True,null=True)
    pinyin = models.CharField(_("pinyin"),max_length=const.DB_CHAR_NAME_120,blank=True,null=True)
    series = models.CharField(_("position series"),max_length=1,default='A',choices=const.get_value_list('S014'))
    grade =  models.CharField(_("position grade"),max_length=const.DB_CHAR_CODE_2,default='01',choices=const.get_value_list('S015'))
    virtual = models.BooleanField(_("is virtual"),default=False)
    status = models.BooleanField(_("in use"),default=True)
    description = models.TextField(_("position description"),blank=True,null=True)
    qualification = models.TextField(_("qualification"),blank=True,null=True)
    document = models.FileField(_("reference"),blank=True,null=True)
    weight = models.IntegerField(_("weight"),default=99)

    def __str__(self):
        return u'%s %s' % (self.code,self.name)

    class Meta:
        verbose_name ="岗位"
        verbose_name_plural = "岗位"
