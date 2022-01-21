from django.contrib import admin

from memoorje.accounting.models import Expense, ExpenseType, Transaction

admin.site.register(ExpenseType)
admin.site.register(Transaction)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("created_on", "creator_name", "type", "description", "amount")
    ordering = ("-created_on",)
