from django.contrib import admin

from .models import Giving, OnlineGiving


@admin.register(Giving)
class GivingAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'amount', 'giving_category', 'date', 'payment_method', 'reference_number']
    list_filter = ['giving_category', 'payment_method', 'date']
    search_fields = ['member__first_name', 'member__last_name', 'reference_number', 'notes', 'member__member_number']


@admin.register(OnlineGiving)
class OnlineGivingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'amount', 'giving_category', 'frequency', 'status', 'reference_number', 'created_at']
    list_filter = ['status', 'giving_category', 'frequency']
    search_fields = ['name', 'email', 'reference_number']
    readonly_fields = ['reference_number', 'created_at']