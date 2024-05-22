from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
import csv
import json
from decimal import Decimal
import pandas as pd
from django.db.models import Sum
from django.db.models.signals import post_save
from django.db.models import Sum, F, Value as V
from django.db.models.functions import Coalesce
from django.db.models import FloatField
from django.dispatch import receiver
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from cashflow.forms import BalanceUpdateForm,DateRangeForm,InventoryForm



from cashflow.models import IncomeSource, ExpenseSource, Project, CashIn,CustomUser,Cashout,Summary,ProjectSummary, Project

# @login_required(login_url='/')
# def HOME(request):
#     return render(request, 'account/home.html')

@login_required(login_url='/')
def HOME(request):
    # Aggregate cash in, cash out, and balance
    total_cash_in = Summary.objects.aggregate(Sum('cash_in'))['cash_in__sum'] or 0
    total_cash_out = Summary.objects.aggregate(Sum('cash_out'))['cash_out__sum'] or 0
    balance = total_cash_in - total_cash_out
    bank_balance = Summary.objects.first().balance if Summary.objects.exists() else 0

   
    context = {
        'total_cash_in': total_cash_in,
        'total_cash_out': total_cash_out,
        'balance': balance,
        'bank_balance': bank_balance,
    
    }

    return render(request, 'account/home.html', context)
    
@login_required(login_url='/')
def ADD_CASHIN(request):
    income_source = IncomeSource.objects.all()
    project = Project.objects.all()
    
    if request.method == "POST":
        income_source_id = request.POST.get('income_source_id')
        date = request.POST.get('date')
        cash_in = request.POST.get('cash_in')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        project_id = request.POST.get('project_id')
        cost_center = request.POST.get('cost_center')
        service_date = request.POST.get('service_date')

        # Retrieve IncomeSource and Project objects
        income_source = IncomeSource.objects.get(id=income_source_id)
        project = Project.objects.get(id=project_id)
        
        # Get the currently logged-in user
        admin = request.user
        
        # Create and save CashIn instance
        cashin = CashIn(
            income_source=income_source,
            date=date,
            cash_in=cash_in,
            status=status,
            remark=remark,
            project=project,
            cost_center=cost_center,
            service_date=service_date
        )
        cashin.save()
        
        messages.success(request, 'Cashin Successfully Saved')
        return redirect('view_cashin')

    context = {
        'income_source': income_source,
        'project': project
    }
    
    return render(request, 'account/add-cashin.html', context)

@login_required(login_url='/')
def VIEW_CASHIN(request):
    cashins = CashIn.objects.all().order_by('date')
    context = { "cashins": cashins  }
    return render(request, 'account/view-cashin.html', context)
        
@login_required(login_url='/')
def EDIT_CASHIN(request, id):
    # if request.user.user_type != '1,2,3':
    #     messages.error(request, "No Permission to go there")
    #     return redirect("logout")
    # else:
        cashin = CashIn.objects.filter(id=id)
        # Assuming you have IncomeSource and Project models similarly to Student, Course, and Session_Year
        income_sources = IncomeSource.objects.all()
        projects = Project.objects.all()

        context = {
            'cashin': cashin,
            'income_sources': income_sources,
            'projects': projects,
        }
        return render(request, 'account/edit-cashin.html', context)


@login_required(login_url='/')
def UPDATE_CASHIN(request):
    if request.method == "POST":
        cashin_id = request.POST.get('cashin_id')
        date = request.POST.get('date')
        cash_in = request.POST.get('cash_in')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        project_id = request.POST.get('project')
        cost_center = request.POST.get('cost_center')
        service_date = request.POST.get('service_date')

        cashin = CashIn.objects.get(id=cashin_id)
        cashin.date = date
        cashin.cash_in = cash_in
        cashin.status = status
        cashin.remark = remark
        cashin.project_id = project_id
        cashin.cost_center = cost_center
        cashin.service_date = service_date
        cashin.save()

        messages.success(request, 'Cashin Record Successfully Updated!')
        return redirect('view_cashin')

    return render(request, 'account/edit-cashin.html')


@login_required(login_url='/')
def import_cashin(request):
    if request.method == 'POST':
        # Get the uploaded file
        csv_file = request.FILES['csv_file']

        try:
            # Read the CSV or Excel file
            if csv_file.name.endswith('.csv'):
                df = pd.read_csv(csv_file)
            elif csv_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(csv_file)
            else:
                raise ValueError("Unsupported file format")

            # Iterate over each row in the DataFrame
            for index, row in df.iterrows():
                # Extract data from the row
                date = row['Date']
                income_source_name = row['Income Source']
                cash_in = row['Cash In']
                status = row['Status']
                project_name = row['Project']
                cost_center = row['Cost Center']
                service_date = row['Service Date']

                # Check if the Income Source exists, otherwise create it
                income_source, _ = IncomeSource.objects.get_or_create(name=income_source_name)

                # Check if the Project exists, otherwise create it
                project, _ = Project.objects.get_or_create(name=project_name)

                # Create the CashIn object
                cashin = CashIn(
                    income_source=income_source,
                    date=date,
                    cash_in=cash_in,
                    status=status,
                    project=project,
                    cost_center=cost_center,
                    service_date=service_date
                )
                cashin.save()

            messages.success(request, 'Cashin Data Successfully Imported!')
            return redirect('view_cashin')
        
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'account/import-cashin.html')

@login_required(login_url='/')
def export_cashin(request):
    cashins = CashIn.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cashin_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Income Source', 'Cash In', 'Status', 'Project', 'Cost Center', 'Service Date'])

    for cashin in cashins:
        writer.writerow([
            cashin.id,
            cashin.date,
            cashin.income_source.name,
            cashin.cash_in,
            cashin.status,
            cashin.project.name,
            cashin.cost_center,
            cashin.service_date
        ])

    return response
@login_required(login_url='/')
def DELETE_CASHIN(request, cashin_id):
    if request.user.user_type in ['1', '2', '3']:
        cashin = CashIn.objects.get(id=cashin_id)
        cashin.delete()
        messages.success(request, 'Cashin record deleted successfully!')
    else:
        messages.error(request, "No permission to delete cashin records.")
    return redirect('view_cashin')

@csrf_exempt
@login_required(login_url='/')
def add_income_source(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            income_source = IncomeSource.objects.create(name=name)
            return JsonResponse({'success': True, 'id': income_source.id, 'name': income_source.name})
        return JsonResponse({'success': False})

@csrf_exempt
def add_project(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        new_project = Project.objects.create(name=name)
        return JsonResponse({'id': new_project.id, 'name': new_project.name})

@login_required(login_url='/')
def ADD_CASHOUT(request):
    expense_source = ExpenseSource.objects.all()
    project = Project.objects.all()

    if request.method == "POST":
        expense_source_id = request.POST.get('expense_source_id')
        date = request.POST.get('date')
        cash_out = request.POST.get('cash_out')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        project_id = request.POST.get('project_id')
        cost_center = request.POST.get('cost_center')
        service_date = request.POST.get('service_date')

        expense_source = ExpenseSource.objects.get(id=expense_source_id)
        project = Project.objects.get(id=project_id)

        cashout = Cashout(
            expense_source=expense_source,
            date=date,
            cash_out=cash_out,
            status=status,
            remark=remark,
            project=project,
            cost_center=cost_center,
            service_date=service_date
        )
        cashout.save()

        if status == "Scheduled":
            installment_details = []
            for i in range(1, 6):
                installment_date = request.POST.get(f'installment_{i}_date')
                installment_amount = request.POST.get(f'installment_{i}_amount')
                if installment_date and installment_amount:
                    installment_details.append({'date': installment_date, 'amount': installment_amount})

            if installment_details:
                cashout.update_installments(installment_details)
            else:
                cashout.delete()
                messages.error(request, 'Installment details cannot be empty for scheduled cashout.')
                return redirect('add_cashout')

        messages.success(request, 'Cashout Successfully Saved')
        return redirect('view_cashout')

    context = {
        'expense_source': expense_source,
        'project': project
    }

    return render(request, 'account/add-cashout.html', context)
@login_required(login_url='/')
def add_expense_source(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            expense_source = ExpenseSource.objects.create(name=name)
            return JsonResponse({'success': True, 'id': expense_source.id, 'name': expense_source.name})
        return JsonResponse({'success': False})

@login_required(login_url='/')
def add_project(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            project = Project.objects.create(name=name)
            return JsonResponse({'success': True, 'id': project.id, 'name': project.name})
        return JsonResponse({'success': False})
    

@login_required(login_url='/')
def VIEW_CASHOUT(request):
    cashouts = Cashout.objects.all().order_by('date')
    context = {"cashouts": cashouts}
    return render(request, 'account/view-cashout.html', context)

@login_required(login_url='/')
def EDIT_CASHOUT(request, id):
    cashout = Cashout.objects.filter(id=id).first()
    if not cashout:
        messages.error(request, "Cashout record not found")
        return redirect("view_cashout")

    # Assuming you have ExpenseSource and Project models similarly to IncomeSource and Project
    expense_sources = ExpenseSource.objects.all()
    projects = Project.objects.all()

    context = {
        'cashout': cashout,
        'expense_sources': expense_sources,
        'projects': projects,
    }
    return render(request, 'account/edit-cashout.html', context)

@login_required(login_url='/')
def UPDATE_CASHOUT(request):
    if request.method == "POST":
        cashout_id = request.POST.get('cashout_id')
        date = request.POST.get('date')
        cash_out = request.POST.get('cash_out')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        project_id = request.POST.get('project')
        cost_center = request.POST.get('cost_center')
        service_date = request.POST.get('service_date')

        cashout = Cashout.objects.get(id=cashout_id)
        cashout.date = date
        cashout.cash_out = cash_out
        cashout.status = status
        cashout.remark = remark
        cashout.project_id = project_id
        cashout.cost_center = cost_center
        cashout.service_date = service_date
        cashout.save()

        messages.success(request, 'Cashout Record Successfully Updated!')
        return redirect('view_cashout')

    return render(request, 'account/edit-cashout.html')
@login_required(login_url='/')
def DELETE_CASHOUT(request, cashout_id):
    if request.user.user_type in ['1', '2', '3']:
        cashout = Cashout.objects.get(id=cashout_id)
        cashout.delete()
        messages.success(request, 'Cashout record deleted successfully!')
    else:
        messages.error(request, "No permission to delete cashout records.")
    return redirect('view_cashout')
@login_required(login_url='/')
def export_cashout(request):
    cashouts = Cashout.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cashout_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Expense Source', 'Cash Out', 'Status', 'Remark', 'Project', 'Cost Center', 'Service Date', 'Total Installment Amount', 'Balance to Pay'])

    for cashout in cashouts:
        writer.writerow([
            cashout.id,
            cashout.date,
            cashout.expense_source.name,
            cashout.cash_out,
            cashout.status,
            cashout.remark,
            cashout.project.name if cashout.project else "",  # Check if project exists
            cashout.cost_center,
            cashout.service_date,
            cashout.total_installment_amount,
            cashout.balance_to_pay
        ])

    return response

@login_required(login_url='/')
def import_cashout(request):
    if request.method == 'POST':
        # Get the uploaded file
        csv_file = request.FILES['csv_file']

        try:
            # Read the CSV or Excel file
            if csv_file.name.endswith('.csv'):
                df = pd.read_csv(csv_file)
            elif csv_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(csv_file)
            else:
                raise ValueError("Unsupported file format")

            # Iterate over each row in the DataFrame
            for index, row in df.iterrows():
                # Extract data from the row
                date = row['Date']
                expense_source_name = row['Expense Source']
                cash_out = row['Cash Out']
                status = row['Status']
                remark = row['Remark']
                project_name = row['Project']
                cost_center = row['Cost Center']
                service_date = row['Service Date']

                # Check if the Expense Source exists, otherwise create it
                expense_source, _ = ExpenseSource.objects.get_or_create(name=expense_source_name)

                # Check if the Project exists, otherwise create it
                project, _ = Project.objects.get_or_create(name=project_name)

                # Create the Cashout object
                cashout = Cashout(
                    expense_source=expense_source,
                    date=date,
                    cash_out=cash_out,
                    status=status,
                    remark=remark,
                    project=project,
                    cost_center=cost_center,
                    service_date=service_date
                )
                cashout.save()

            messages.success(request, 'Cashout Data Successfully Imported!')
            return redirect('view_cashout')
        
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'account/import-cashout.html')






@login_required(login_url='/')
def summary_view(request):
    form = BalanceUpdateForm(request.POST or None)
    date_range_form = DateRangeForm(request.GET or None)

    summaries = Summary.objects.order_by('date')

    # Filter summaries based on date range
    if date_range_form.is_valid():
        start_date = date_range_form.cleaned_data.get('start_date')
        end_date = date_range_form.cleaned_data.get('end_date')
        if start_date and end_date:
            summaries = summaries.filter(date__range=(start_date, end_date))
        elif start_date:
            summaries = summaries.filter(date__gte=start_date)
        elif end_date:
            summaries = summaries.filter(date__lte=end_date)

    if request.method == 'POST' and form.is_valid():
        date = form.cleaned_data['date']
        available_balance = form.cleaned_data['available_balance']

        previous_summary = Summary.objects.filter(date__lt=date).order_by('-date').first()
        if previous_summary:
            balance = previous_summary.balance + available_balance
        else:
            balance = available_balance

        # Update balance for the given date
        Summary.objects.filter(date=date).update(balance=balance)

        # Recalculate balances for subsequent dates
        for obj in Summary.objects.filter(date__gt=date).order_by('date'):
            previous_summary = Summary.objects.filter(date__lt=obj.date).order_by('-date').first()
            if previous_summary:
                obj.balance = previous_summary.balance + obj.cash_in - obj.cash_out
                obj.save()

        messages.success(request, 'Balance updated successfully!')  # Add success message
        return redirect('view_summary')

    context = {
        'summaries': summaries,
        'form': form,
        'date_range_form': date_range_form,
    }
    return render(request, 'account/view-summary.html', context)

@login_required(login_url='/')
def update_summary_cashin(request):
    # Get all CashIn objects
    cashin_queryset = CashIn.objects.all()

    # Group CashIn objects by date
    grouped_cashin_by_date = defaultdict(list)
    for cashin_obj in cashin_queryset:
        grouped_cashin_by_date[cashin_obj.date].append(cashin_obj)

    # Update or create Summary records for each unique date
    for date, cashin_objects_with_same_date in grouped_cashin_by_date.items():
        # Collect cash_in values for the objects with the same date
        cashin_values = [obj.cash_in for obj in cashin_objects_with_same_date]

        # Calculate the sum for cash_in
        total_cashin = sum(cashin_values)

        # Update or create Summary record for the specified date
        summary, _ = Summary.objects.update_or_create(
            date=date,
            defaults={
                'cash_in': total_cashin,
            }
        )

    messages.success(request, 'Summary Successfully Updated for Cash In!')
    return redirect('view_summary')

@login_required(login_url='/')
def update_summary_cashout(request):
    # Get all CashOut objects
    cashout_queryset = Cashout.objects.all()

    # Group CashOut objects by date
    grouped_cashout_by_date = defaultdict(list)
    for cashout_obj in cashout_queryset:
        grouped_cashout_by_date[cashout_obj.date].append(cashout_obj)

    # Update or create Summary records for each unique date
    for date, cashout_objects_with_same_date in grouped_cashout_by_date.items():
        # Collect cash_out values for the objects with the same date
        cashout_values = [obj.cash_out for obj in cashout_objects_with_same_date]

        # Calculate the sum for cash_out
        total_cashout = sum(cashout_values)

        # Check if a Summary record exists for this date
        summary = Summary.objects.filter(date=date).first()

        # Update or create Summary record for the specified date
        if summary:
            summary.cash_out = total_cashout
            summary.save()
        else:
            # Create a new Summary record if it doesn't exist
            Summary.objects.create(date=date, cash_out=total_cashout)

    messages.success(request, 'Summary Successfully Updated for Cash Out!')
    return redirect('view_summary')

@login_required(login_url='/')
def edit_summary(request, date):
    cashin_records = CashIn.objects.filter(date=date)
    cashout_records = Cashout.objects.filter(date=date)

    context = {
        'date': date,
        'cashin_records': cashin_records,
        'cashout_records': cashout_records,
    }
    return render(request, 'account/edit_summary.html', context)

def export_summary(request):
    # Retrieve all summaries
    summaries = Summary.objects.all().order_by('date')

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="summary_export.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write CSV header
    writer.writerow(['Date', 'Cash In', 'Cash Out', 'Balance'])

    # Write data rows
    for summary in summaries:
        writer.writerow([summary.date, summary.cash_in, summary.cash_out, summary.balance])

    return response


@login_required(login_url='/')
def view_incomesource(request):
    income_sources = IncomeSource.objects.all()
    context = {'income_sources': income_sources}
    return render(request, 'account/view-income-source.html', context)

@csrf_exempt
@login_required(login_url='/')
def add_income_source(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            if IncomeSource.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'Income source already exists.'})
            income_source = IncomeSource.objects.create(name=name)
            return JsonResponse({'success': True, 'id': income_source.id, 'name': income_source.name})
        return JsonResponse({'success': False, 'message': 'Invalid data.'})
    
@login_required(login_url='/')
def view_expensesource(request):
    expense_sources = ExpenseSource.objects.all()
    context = {'expense_sources': expense_sources}
    return render(request, 'account/view-expense-source.html', context)
@csrf_exempt
@login_required(login_url='/')
def add_expense_source(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            if ExpenseSource.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'Expense source already exists.'})
            expense_source = ExpenseSource.objects.create(name=name)
            return JsonResponse({'success': True, 'id': expense_source.id, 'name': expense_source.name})
        return JsonResponse({'success': False, 'message': 'Invalid data.'})
    
@login_required(login_url='/')
def VIEW_PROJECT(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'account/view-project-db.html', context)
@csrf_exempt
@login_required(login_url='/')
def add_project(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            if Project.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'Project already exists.'})
            new_project = Project.objects.create(name=name)
            return JsonResponse({'success': True, 'id': new_project.id, 'name': new_project.name})
        return JsonResponse({'success': False, 'message': 'Invalid data.'})
    

@login_required(login_url='/')
def view_project_summary(request):
    # Retrieve all project summaries and order by date
    project_summaries = ProjectSummary.objects.all().order_by('date')

    # Get the selected project from the GET parameters
    selected_project = request.GET.get('project')

    # Filter project summaries based on the selected project
    if selected_project:
        project_summaries = project_summaries.filter(project__name=selected_project)

    # Get the start and end date from the GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply date range filtering if both dates are provided
    if start_date and end_date:
        project_summaries = project_summaries.filter(date__range=[start_date, end_date])
    elif start_date:
        project_summaries = project_summaries.filter(date__gte=start_date)
    elif end_date:
        project_summaries = project_summaries.filter(date__lte=end_date)

    # Calculate total cash in and cash out
    total_cash_in = sum(summary.cash_in for summary in project_summaries)
    total_cash_out = sum(summary.cash_out for summary in project_summaries)

    # Calculate the initial balance
    balance = total_cash_in - total_cash_out

    # Initialize inventory values
    start_inventory = Decimal('0')
    end_inventory = Decimal('0')
    actual_balance = balance

    # Process inventory form data if the request method is POST
    if request.method == 'POST':
        inventory_form = InventoryForm(request.POST)
        if inventory_form.is_valid():
            start_inventory = Decimal(inventory_form.cleaned_data['start_inventory'])
            end_inventory = Decimal(inventory_form.cleaned_data['end_inventory'])
            actual_balance = balance - start_inventory + end_inventory
    else:
        inventory_form = InventoryForm()

    # Get unique project names for the dropdown
    project_names = ProjectSummary.objects.values_list('project__name', flat=True).distinct()

    # Prepare the context to be rendered in the template
    context = {
        'total_cash_in': total_cash_in,
        'total_cash_out': total_cash_out,
        'balance': balance,
        'start_inventory': start_inventory,
        'end_inventory': end_inventory,
        'actual_balance': actual_balance,
        'project_summaries': project_summaries,
        'inventory_form': inventory_form,
        'project_names': project_names,
        'selected_project': selected_project,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'account/view_project_summary.html', context)

def export_project_summary(request):
    # Retrieve project summaries based on filters (if any)
    project_summaries = ProjectSummary.objects.all()

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="project_summary.csv"'

    # Define CSV writer
    writer = csv.writer(response)
    
    # Write CSV header
    writer.writerow(['Date', 'Project', 'Cash In', 'Cash Out', 'Balance', 'Service Date'])

    # Write data rows
    for summary in project_summaries:
        writer.writerow([
            summary.date,
            summary.project.name if summary.project else "",  # Assuming you have a 'name' attribute in your Project model
            summary.cash_in,
            summary.cash_out,
            summary.balance,
            summary.service_date if summary.service_date else ""  # Assuming you have a 'service_date' attribute
        ])

    return response

