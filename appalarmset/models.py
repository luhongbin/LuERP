# coding:utf-8
from django.db import models

class getsmm(models.Model):
    #id = models.IntegerField('结果',primary_key=True) name, price, aver, interidcreatdate
    interid = models.IntegerField('interid',primary_key=True)
    name = models.CharField('商品名称', max_length=20)
    price = models.CharField('价格', max_length=20)
    aver = models.DecimalField('价格',max_digits=14,decimal_places=4)
    today = models.CharField('日期', max_length=20)
    creatdate = models.DateTimeField('创建时间')
    class Meta:
        managed = False
        app_label = 'appalarmset'
        db_table = 'getsmm'
        verbose_name = "上海有色金属交易价格"
        verbose_name_plural = verbose_name
        ordering = ['-creatdate','name']
        #proxy = True  # 设置为True 否则会重新注册一张数据表
    def __str__(self):
        return self.name
# Create your models here.
class appalarmset(models.Model):
    id = models.IntegerField('ID',primary_key=True)
    snid = models.CharField('结果', max_length=40)
    sn = models.CharField('设备号', max_length=20)
    action = models.CharField('动作', max_length=20)
    mobtype = models.CharField('机型', max_length=40)
    Country = models.CharField('国家', max_length=40)
    creatdate = models.DateTimeField('创建时间', auto_now_add=True)
    uuid = models.CharField('uuid', max_length=150)
    devname = models.CharField('设备名称', max_length=150)
    mobname = models.CharField('手机名称', max_length=40)
    mobver = models.CharField('手机版本', max_length=40)
    mobid = models.CharField('手机标识', max_length=40)
    mobidver = models.CharField('手机标识版本', max_length=40)
    firmver = models.CharField('固件版本', max_length=40)
    longitude = models.CharField('经度', max_length=40)
    latitude = models.CharField('维度', max_length=40)
    password = models.CharField('密码', max_length=40)
    mobidname = models.CharField('手机标识名', max_length=40)
    speed = models.FloatField('速度', default=0)
    altitude = models.CharField('海拔高度', max_length=40)
    class Meta:
        managed = False
        app_label = 'appalarmset'
        db_table = 'appalarmset'
        verbose_name = "智能灯日志"
        verbose_name_plural = verbose_name
        ordering = ['-creatdate']
        #proxy = True  # 设置为True 否则会重新注册一张数据表
        # permissions = (
        #     ('view_appalarmset', 'view_appalarmset'),
        # )
    def __str__(self):
        return self.sn

    # ID = models.IntegerField('结果',  primary_key=True)
    # Command = models.CharField('机型', max_length=1000)
    # HostName = models.CharField('国家', max_length=40)
    # LoginName = models.CharField('国家', max_length=100)
    # PostTime = models.CharField('创建时间', max_length=24)
    # class Meta:
    #     db_table = 'AuditLog'
    #     verbose_name = "智能灯日志"
    #     verbose_name_plural = verbose_name
    #     ordering = ['-PostTime']
    #     #proxy = True  # 设置为True 否则会重新注册一张数据表
    #
    # def __str__(self):
    #     return self.sn
# Create your models here.
