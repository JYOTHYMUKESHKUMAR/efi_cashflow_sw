

# Register your models here.
from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from decimal import Decimal,ROUND_HALF_UP,InvalidOperation
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib import admin
from .models import IncomeSource, ExpenseSource, Project, CashIn,Cashout,Summary ,ProjectSummary

class CashInAdmin(admin.ModelAdmin):
    list_display = [ 'income_source', 'date', 'cash_in', 'status', 'project', 'cost_center', 'service_date']
   
    list_filter = ['status', 'cost_center', 'service_date']




class CashoutAdmin(admin.ModelAdmin):
    list_display = ['id', 'expense_source', 'date', 'cash_out', 'status', 'remark', 'project', 'cost_center', 'service_date','total_installment_amount','balance_to_pay','installment_details']
    readonly_fields = ['total_installment_amount',  'balance_to_pay','installment_details']
    fields = ['expense_source', 'date', 'cash_out', 'status', 'remark', 'project', 'cost_center', 'service_date', 'total_installment_amount','balance_to_pay', 'installment_details']


class SummaryAdmin(admin.ModelAdmin):
    
    list_display = ('date', 'cash_in', 'cash_out', 'balance') #'actual_cash_in', 'actual_cash_out', 'actual_balance', 
    search_fields = ['date']
    ordering = ['-date']


@receiver(post_save, sender=CashIn)
@receiver(post_save, sender=Cashout)
def update_project_summary(sender, instance, created, **kwargs):
    if created:
        # Calculate cash flow based on the instance
        cash_flow = instance.cash_in if isinstance(instance, CashIn) else -instance.cash_out

        # Create a new ProjectSummary record for the specific date and project
        ProjectSummary.objects.create(
            date=instance.date,
            project=instance.project,
            cash_in=cash_flow if cash_flow > 0 else 0,
            cash_out=-cash_flow if cash_flow < 0 else 0,
            service_date=instance.service_date,
            balance=cash_flow
        )
    else:
        # Retrieve all UpdateCashIn and UpdateCashOut instances for the specific date and project
        cash_in_transactions = CashIn.objects.filter(date=instance.date, project=instance.project)
        cash_out_transactions = Cashout.objects.filter(date=instance.date, project=instance.project)

        # Calculate the total cash in and cash out for the specific date and project
        cash_in_total = cash_in_transactions.aggregate(total_cash_in=Sum('cash_in'))['total_cash_in'] or 0
        cash_out_total = cash_out_transactions.aggregate(total_cash_out=Sum('cash_out'))['total_cash_out'] or 0

        # Calculate the balance
        balance = cash_in_total - cash_out_total

        # Update or create the ProjectSummary record for the specific date and project
        project_summary, _ = ProjectSummary.objects.update_or_create(
            date=instance.date,
            project=instance.project,
            defaults={
                'cash_in': cash_in_total,
                'cash_out': cash_out_total,
                
                'balance': balance,
            }
        )

class ProjectSummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'project', 'service_date', 'cash_in', 'cash_out', 'balance')
    list_filter = ('date', 'project', 'service_date')
    search_fields = ('project',)
    
    

    
    
    def has_add_permission(self, request):
        # Disable the ability to add new Summary records
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to change existing Summary records
        return False

    # def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete existing Summary records
        return False
    change_list_template = 'admin/cashflow/project_summary_change_list.html'




    



    def changelist_view(self, request, extra_context=None):
        # Get the queryset based on applied filters
        cl = self.get_changelist_instance(request)
        queryset = cl.get_queryset(request)

        # Calculate total cash in, total cash out, and balance based on the filtered queryset
        total_cash_in = Decimal(queryset.aggregate(total_cash_in=Sum('cash_in'))['total_cash_in'] or 0)
        total_cash_out = Decimal(queryset.aggregate(total_cash_out=Sum('cash_out'))['total_cash_out'] or 0)
        balance = total_cash_in - total_cash_out

        # Initialize actual balance
        actual_balance = balance

        start_inventory = Decimal(0)  # Initialize start_inventory with Decimal(0)
        end_inventory = Decimal(0)    # Initialize end_inventory with Decimal(0)

        if request.method == 'POST':
            # Get start inventory and end inventory from the form
            start_inventory_str = request.POST.get('start_inventory', '').strip()
            end_inventory_str = request.POST.get('end_inventory', '').strip()

            if not start_inventory_str:
                messages.error(request, "Please enter the start inventory amount.")
            elif not end_inventory_str:
                messages.error(request, "Please enter the end inventory amount.")
            else:
                try:
                    start_inventory = Decimal(start_inventory_str)
                    end_inventory = Decimal(end_inventory_str)
                except InvalidOperation:
                    messages.error(request, "Invalid inventory amount. Please enter a valid number.")

            # Calculate actual balance
            actual_balance = balance - start_inventory + end_inventory

        # Prepare the extra context with the calculated values and form inputs
        extra_context = extra_context or {}
        extra_context['total_cash_in'] = total_cash_in
        extra_context['total_cash_out'] = total_cash_out
        extra_context['balance'] = balance
        extra_context['actual_balance'] = actual_balance
        extra_context['start_inventory'] = start_inventory
        extra_context['end_inventory'] = end_inventory

        # Render the changelist view with the extra context
        return super().changelist_view(request, extra_context=extra_context)




admin.site.register(Cashout, CashoutAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(ProjectSummary, ProjectSummaryAdmin)






# class UserModel(UserAdmin):
#     list_display = ['username','user_type']
    
admin.site.register(CustomUser) 
admin.site.register(IncomeSource)
admin.site.register(ExpenseSource)
admin.site.register(Project)
admin.site.register(CashIn,CashInAdmin)
# from django.contrib import admin
# from .models import *
# from django.contrib.auth.admin import UserAdmin
# from .models import  CashIn, CashOut, Summary, ProjectSummary, UserActionLog
# class UserModel(UserAdmin):
#     list_display = ['username','user_type']

# admin.site.register(CustomUser,UserModel)
# admin.site.register(CashIn)
# admin.site.register(CashOut)
# admin.site.register(Summary)
# admin.site.register(ProjectSummary)
# admin.site.register(UserActionLog)

