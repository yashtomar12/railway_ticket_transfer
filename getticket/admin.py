from django.contrib import admin
from .models import TicketTransferRequest, RailwayStaff

@admin.register(TicketTransferRequest)
class TicketTransferRequestAdmin(admin.ModelAdmin):
    list_display = ('id','user','passenger_name','train_number','journey_date',
                    'seat_number','transferred_to','status','created_at')
    list_filter = ('status','journey_date','train_number')
    search_fields = ('passenger_name','transferred_to','train_number')
    actions = ['approve_requests','reject_requests']

    def approve_requests(self, request, qs): qs.update(status='APPROVED')
    approve_requests.short_description = 'Approve selected'
    def reject_requests(self, request, qs): qs.update(status='REJECTED')
    reject_requests.short_description = 'Reject selected'


@admin.register(RailwayStaff)
class RailwayStaffAdmin(admin.ModelAdmin):
    list_display = ("user", "hrms_id", "department", "role")
    search_fields = ("hrms_id", "user__username", "department")
    list_filter = ("role", "department")
