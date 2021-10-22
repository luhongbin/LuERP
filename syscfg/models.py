# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from common import const
from common import generic
from django.contrib.contenttypes.models import ContentType


class Site(models.Model):
    """
    站点，一个站点下可有多个公司，处于同一个站点下的用户逻辑上位于同一个组织
    """
    index_weight = 1
    begin = models.DateField("开始日期", blank=True,null=True)
    end = models.DateField("结束日期", blank=True,null=True)
    name = models.CharField("站点名称", max_length=const.DB_CHAR_NAME_40)
    description = models.TextField( "描述信息",blank=True,null=True)
    user = models.ManyToManyField(User,verbose_name="管理员")

    def __str__(self):
        return u'%s'%self.name

    class Meta:
        verbose_name = "站点"
        verbose_name_plural = "站点"



class Module(generic.BO):
    """
    模块管理
    """
    index_weight = 2
    code = models.CharField("模块编号",max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    name = models.CharField("模块名称",max_length=const.DB_CHAR_NAME_40)
    url = models.URLField("URL",blank=True,null=True,max_length=const.DB_CHAR_NAME_80)
    weight = models.IntegerField("排序权重",blank=True,null=True,default=99)
    icon = models.CharField("样式类",blank=True,null=True,max_length=const.DB_CHAR_NAME_40)
    parent = models.ForeignKey('self', blank=True, null=True, verbose_name="父级",on_delete=models.CASCADE)
    status = models.BooleanField("在用？",default=True)

    class Meta:
        verbose_name = "模块"
        verbose_name_plural = "模块"

    def __str__(self):
        return self.name

class Menu(generic.BO):
    """
    菜单管理
    """
    index_weight = 3
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name="模块")
    code = models.CharField("菜单编号",max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    name = models.CharField("菜单名称",max_length=const.DB_CHAR_NAME_40)
    url = models.URLField("URL",blank=True,null=True,max_length=const.DB_CHAR_NAME_80)
    weight = models.IntegerField("排序权重",blank=True,null=True,default=99)
    icon = models.CharField("样式类",blank=True,null=True,max_length=const.DB_CHAR_NAME_40)
    status = models.BooleanField("在用？",default=True)

    class Meta:
        verbose_name = "菜单"
        verbose_name_plural = "菜单"

    def __str__(self):
        return self.name

class Role(generic.BO):
    """
    角色管理，分配用户所拥有的菜单
    """
    index_weight = 4
    code = models.CharField("角色编号",max_length=const.DB_CHAR_CODE_6,blank=True,null=True)
    name = models.CharField("角色名称",max_length=const.DB_CHAR_NAME_40)
    description = models.CharField( "描述信息",max_length=const.DB_CHAR_NAME_80,blank=True,null=True)
    status = models.BooleanField("在用？",default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True,null=True, verbose_name="父级")
    users = models.ManyToManyField(User,verbose_name="分配用户",blank=True)
    menus = models.ManyToManyField(Menu,verbose_name="分配菜单",blank=True)

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
    def __str__(self):
        return self.name