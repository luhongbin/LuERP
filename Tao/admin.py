from django.contrib import admin
from common import generic
from Tao.models import SaleOrder,SaleItem,PaymentCollection,OfferSheet,OfferItem
from basedata.models import BankAccount,sale_order,sale_order_line,res_partner
from common import generic
#from daterange_filter.filter import DateRangeFilter

import datetime

#@admin.register(res_partner)
class res_partnerAdmin(admin.ModelAdmin):
    model = res_partner
    CODE_NUMBER_WIDTH = 5
    CODE_PREFIX = 'SO'
    list_display = ['name','display_name','company','create_date','ref','street','mobile','phone','name_cn','supplier','is_company','customer','employee','active']
    list_display_links = ['name','display_name']
    #raw_id_fields = ['name','display_name','company_id']
#    list_filter = ('supplier', 'is_company',('create_date', DateRangeFilter), )
    list_filter = ('supplier', 'is_company',('create_date',), )

    # fields = (
    #     ('code','org',),('title','invoice_type',),('partner','user',),('order_date','deliver_date',),
    #     ('contact','phone',),('deliver_address','fax',),('description',),('amount','discount_amount','status')
    # )
    # readonly_fields = ['amount','status']
    date_hierarchy = 'create_date'

#@admin.register(sale_order)
class sale_orderAdmin(admin.ModelAdmin):
    model = sale_order
    CODE_NUMBER_WIDTH = 5
    CODE_PREFIX = 'SO'
    list_display = ['name','client_order_ref','date_order','partner','bd_required','state','note','date_approve','requested_date','effective_date','crd_date','shipping_date','bop_approval_date']
    list_display_links = ['name','client_order_ref']
    #raw_id_fields = ['name','display_name','company_id']
#    list_filter = ('unify_order', 'is_late', 'state',('date_order', DateRangeFilter), )
    list_filter = ('unify_order', 'is_late', 'state','date_order', )
    date_hierarchy = 'date_order'

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    fields = ('material','measure','sale_price','discount_price','cnt','tax')
    raw_id_fields = ['material']

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 3


class OfferItemInline(admin.TabularInline):
    model = OfferItem
    fields = ('material','brand','measure','cost_price','sale_price','discount_price','cnt','tax')
    raw_id_fields = ['material']
    readonly_fields = ['brand']

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 3


class SaleOrderAdmin(generic.BOAdmin):
    CODE_NUMBER_WIDTH = 5
    CODE_PREFIX = 'SO'
    inlines = [SaleItemInline]
    list_display = ['code','title','order_date','partner','amount','collection_amount']
    list_display_links = ['code','title']
    #raw_id_fields = ['partner','user','org']
    fields = (
        ('code','org',),('title','invoice_type',),('partner','user',),('order_date','deliver_date',),
        ('contact','phone',),('deliver_address','fax',),('description',),('amount','discount_amount','status')
    )
    readonly_fields = ['amount','status']
    date_hierarchy = 'begin'

    def save_model(self, request, obj, form, change):
        if obj:
            obj.user = request.user
        super(SaleOrderAdmin,self).save_model(request,obj,form,change)

    def get_changeform_initial_data(self, request):
        today = datetime.datetime.today()
        deadline = today+datetime.timedelta(days=30)
        return {'order_date':today,'deliver_date':deadline}


class OfferSheetAdmin(generic.BOAdmin):
    CODE_NUMBER_WIDTH = 5
    CODE_PREFIX = 'BJ'
    inlines = [OfferItemInline]
    list_display = ['code','title','offer_date','partner','amount']
    list_display_links = ['code','title']
    raw_id_fields = ['partner','user','org']
    fields = (
        ('code','org',),('partner','user',),('offer_date','deliver_date',),('title',),
        ('description',),('amount','discount_amount',),('attach'),
    )
    readonly_fields = ['amount']
    date_hierarchy = 'begin'

    def save_model(self, request, obj, form, change):
        if obj:
            obj.user = request.user
        super(OfferSheetAdmin,self).save_model(request,obj,form,change)

    def get_changeform_initial_data(self, request):
        today = datetime.datetime.today()
        deadline = today+datetime.timedelta(days=30)
        return {'offer_date':today,'deliver_date':deadline}


class PaymentCollectionAdmin(generic.BOAdmin):
    CODE_NUMBER_WIDTH = 4
    CODE_PREFIX = 'CP'
    list_display = ['code','so','partner','order_amount','collection_date','collection_amount']
    fields = (
        ('code',),('collection_date',),('so',),('partner',),('order_amount','collection_amount',),('bank',),
        ('memo',)
    )
    raw_id_fields = ['so','partner']
    readonly_fields = ['order_amount']
    list_display_links = ['code','so']
    date_hierarchy = 'begin'

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name=='bank':
            kwargs['queryset'] = BankAccount.objects.exclude(org__exact=None)
        return super(PaymentCollectionAdmin,self).formfield_for_foreignkey(db_field,request,**kwargs)

#admin.site.register(SaleOrder,SaleOrderAdmin)
# admin.site.register(PaymentCollection,PaymentCollectionAdmin)
# admin.site.register(OfferSheet,OfferSheetAdmin)
