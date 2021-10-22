__author__ = 'lutec'
__date__ = ' '

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from common import generic
from django.db.models import Q
from purchase.models import factoryaddr,deliverynote,deliveryitem,filterpmdn200
#from daterange_filter.filter import DateRangeFilter
from django import forms
from basedata.admin import Pmdnt200Admin
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

@admin.register(filterpmdn200)

class filterpmdn200Admin(admin.ModelAdmin):
    list_select_related = False
    def get_queryset(self, request):
        t100 = super().get_queryset(request)
        if request.user.is_superuser:
            return t100.exclude(bclass='3399').order_by('zc')
            # return t100#super(yxhst20190325Admin, self).get_queryset(request)
        return t100.filter(buyercode=request.user.username ).exclude(bclass='3399').order_by('zc')

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    model_icon = 'fa  fa-home'
    list_display = ("billno",'sbill',"code","short_name","short_spec","unit","note","quan","noquan","short_predate","sdate","snote") #界面上展示的列，对应Model的字段
    save_as_continue = True
    save_on_top = True
    search_fields = ("billno",'sbill',"code","name","spec","unit","note","quan","noquan","predate","sdate","snote")
    list_display_links = ('billno',)
    date_hierarchy = 'sdate'  # 详细时间分层筛选　  采购单号序号
    list_per_page = 100
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


# class deliveryitemInlineForm(forms.ModelForm):
#
#     def __init__(self, *args, ** kwargs):
#         super(deliveryitemInlineForm, self).__init__(*args,** kwargs)
#         self.fields['group'].queryset = filterpmdn200.objects.filter(company=self.)

class deliveryitemInline(admin.TabularInline):
    model = deliveryitem
    fields = ('bill', 'noquan', 'code', 'name', 'spec', 'unit',  'sendquan','quan', 'okquan',  'buydate', 'sdate', 'arrive_date','jokquan','jcnoquan')
    raw_id_fields = ['bill']
    readonly_fields = ( 'code', 'name', 'spec', 'unit',  'sendquan','quan', 'noquan',  'buydate', 'sdate', 'arrive_date','jokquan','jcnoquan')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1

    # def get_readonly_fields(self, request, obj=None):
    #     if obj and obj.status == 1:
    #         return ['bill', 'code', 'name', 'spec']
    #     else:
    #         return []

    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     if db_field.name == 'material':
    #         kwargs['queryset'] = Material.objects.filter(is_virtual=0)
    #     return super(deliveryitemInline,self).formfield_for_foreignkey(db_field,request,**kwargs)

@admin.register(deliverynote)

class deliverynoteAdmin(generic.BOAdmin):
    # save_on_top=True
    list_display = ['id','usercode','username','order_date','arrive_date','unitcode','unitaddr','status','description']
    inlines = [deliveryitemInline]
    #change_form_template = 'admin/purchase/deliverynote/deliverynote_form.html'
    fields = ( ('company','unitaddr',),('status','usercode','username',),('order_date','arrive_date',),('description') ,'unitcode',   )
    date_hierarchy = 'order_date'
    extra_buttons = [{'href': 'pbill', 'title': '打印送货单'}, {'href': 'pbillid', 'title': '打印产品标识卡'}]
    #raw_id_fields = ['company']
    empty_value_display = '-'
    readonly_fields = ('usercode','username','order_date','arrive_date','status',)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            print('object_id:', object_id)
            extra_context = extra_context or {}
            object_id=object_id.replace('/change/pbill','')
            obj = deliverynote.objects.get(id=object_id)
            if obj.status == '99':
                extra_context.update(dict(readonly=True))
        return super(deliverynoteAdmin, self).changeform_view(request, object_id, form_url, extra_context)

#    def get_ordering(self, request): def get_search_results(self, request, queryset, search_term):save_related(request, form, formsets, change)
    #get_autocomplete_fields() get_readonly_fields(request, obj=None)¶get_list_display(request)get_inline_instances(request, obj=None),delete_model(self, request, obj): #delete_queryset

    def save_model(self, request, obj, form, change): #save_formset
        obj.unitaddr = request.address
        obj.unitcode = request.name
        super().save_model(request, obj, form, change)

    def get_changeform_initial_data(self, request):
        usercode = request.user.username
        username = request.user.first_name
        unitcode = 'Y1-耀泰'
        unitaddr = '浙江余姚远东工业城CN8'

        import datetime
        begin =  datetime.datetime.now()
        end = begin + datetime.timedelta(30)
        return {'order_date': begin, 'arrive_date': end, 'usercode': usercode, 'username': username, 'unitcode': unitcode, 'unitaddr': unitaddr, 'company': '1'}

    # def get_readonly_fields(self, request, obj=None):
    #     print(obj)
    #
    #     return []
        # if obj and obj.status == 9:
        #     return ['code','title','po','warehouse','batch','status']
        # else:
        #     return ['status','amount']

    # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     if object_id:
    #         obj = deliverynote.objects.get(id=object_id)
    #         if obj and obj.execute_time:
    #             extra_context.update(dict(readonly=True))
    #     return super(deliverynoteAdmin,self).changeform_view(request,object_id,form_url,extra_context)



