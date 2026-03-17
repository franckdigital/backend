from django.contrib import admin
from .models import (
    Ticket, TicketAttachment, TicketMessage,
    TicketStatusHistory, TicketDelegation, TicketEvaluation,
)


class AttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0


class MessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ('sender', 'created_at')


class StatusHistoryInline(admin.TabularInline):
    model = TicketStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'created_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'objet', 'pharmacie', 'categorie',
        'urgence', 'status', 'assigned_to', 'created_at',
    )
    list_filter = ('status', 'urgence', 'categorie', 'type_intervention')
    search_fields = ('reference', 'objet', 'description')
    readonly_fields = ('reference', 'created_at', 'updated_at')
    inlines = [AttachmentInline, MessageInline, StatusHistoryInline]


@admin.register(TicketDelegation)
class TicketDelegationAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'from_technicien', 'to_technicien', 'created_at')
    list_filter = ('created_at',)


@admin.register(TicketEvaluation)
class TicketEvaluationAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'note', 'created_by', 'created_at')
    list_filter = ('note',)
