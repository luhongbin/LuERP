# Generated by Django 3.0.3 on 2020-03-05 19:52

import apiview.model
from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='主键ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')),
                ('modify_time', models.DateTimeField(auto_now=True, db_index=True, verbose_name='修改时间')),
                ('delete_status', models.BooleanField(choices=[(False, '正常'), (True, '已经删除')], db_index=True, default=False, verbose_name='删除状态')),
                ('remark', models.TextField(blank=True, default='', null=True, verbose_name='备注说明')),
                ('openid', models.CharField(default='', max_length=64, unique=True, verbose_name='openId')),
                ('unionid', models.CharField(db_index=True, default='', max_length=64, verbose_name='unionId')),
                ('session_key', models.CharField(max_length=256, verbose_name='session_key')),
                ('nickname', models.CharField(default='', max_length=64, verbose_name='昵称')),
                ('gender', models.IntegerField(choices=[(0, '未知'), (1, '男'), (2, '女')], default=0, verbose_name='性别')),
                ('language', models.CharField(default='', max_length=64, verbose_name='语言')),
                ('country', models.CharField(default='', max_length=64, verbose_name='国家')),
                ('province', models.CharField(default='', max_length=64, verbose_name='省份')),
                ('city', models.CharField(default='', max_length=64, verbose_name='城市')),
                ('avatarurl', models.ImageField(default='', max_length=512, upload_to='', verbose_name='头像')),
                ('mobile', models.CharField(max_length=32, verbose_name='小程序授权手机号')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
            bases=(models.Model, apiview.model.ModelFieldChangeMixin, apiview.model.AbstractUserMixin),
            managers=[
                ('default_manager', django.db.models.manager.Manager()),
            ],
        ),
    ]
