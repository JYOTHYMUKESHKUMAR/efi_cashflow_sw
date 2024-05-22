"""
URL configuration for data_management_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render ,redirect
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

from . import account_views
from . import cashin_views
from . import cashout_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/',views.BASE,name='base'),
    path('',views.LOGIN,name='login'),
    path('doLogin',views.doLogin,name='doLogin'),
    path('account/Home',account_views.HOME,name='home'),
    path('doLogout',views.doLogout,name='logout'),
    path('Profile',views.PROFILE,name='profile'),
    path('Profile/update',views.PROFILE_UPDATE,name='profile_update'),
    path('account/CashIn/Add', account_views.ADD_CASHIN, name='add_cashin'),
    path('account/CashIn/View', account_views.VIEW_CASHIN, name='view_cashin'), 
    path('account/CashIn/Edit/<str:id>',account_views.EDIT_CASHIN,name='edit_cashin'),
    path('account/CashIn/Update',account_views.UPDATE_CASHIN,name='update_cashin'),
    path('account/CashIn/Import', account_views.import_cashin, name='import_cashin'),
    path('account/CashIn/Export', account_views.export_cashin, name='export_cashin'),
    path('account/CashIn/Delete/<int:cashin_id>', account_views.DELETE_CASHIN, name='delete_cashin'),
    path('add_income_source/', account_views.add_income_source, name='add_income_source'),
    path('add_project/', account_views.add_project, name='add_project'),


    path('account/CashOut/Add', account_views.ADD_CASHOUT, name='add_cashout'),
    path('add-expense-source/', account_views.add_expense_source, name='add_expense_source'),
    path('add-project/', account_views.add_project, name='add_project'),
    path('account/CashOut/View', account_views.VIEW_CASHOUT, name='view_cashout'), 
    path('account/CashOut/Edit/<str:id>',account_views.EDIT_CASHOUT,name='edit_cashout'),
    path('account/CashOut/Update',account_views.UPDATE_CASHOUT,name='update_cashout'),
    path('account/CashOut/Import', account_views.import_cashout, name='import_cashout'),
    path('account/CashOut/Export', account_views.export_cashout, name='export_cashout'),
    path('account/CashOut/Delete/<int:cashout_id>/', account_views.DELETE_CASHOUT, name='delete_cashout'),
    path('account/Summary/View',  account_views.summary_view, name='view_summary'),
    path('update-summary/cashin/', account_views.update_summary_cashin, name='update_summary_cashin'),
    path('update-summary/cashout/', account_views.update_summary_cashout, name='update_summary_cashout'),
    path('account/Summary/edit-summary/<str:date>/', account_views.edit_summary, name='edit_summary'),
    path('account/Summary/export/', account_views.export_summary, name='export_summary'),
   
    path('account/Project_Summary/view_project_summary/', account_views.view_project_summary, name='view_project_summary'),
    path('account/Project_Summary/export/', account_views.export_project_summary, name='export_project_summary'),

    path('account/Customers_Database/', account_views.view_incomesource, name='view_incomesource'),
   
    path('account/Suppliers_Database/', account_views.view_expensesource, name='view_expensesource'),
    path('account/Project Database/', account_views.VIEW_PROJECT, name='view_project'),
    
 


    

    
 
    
] +static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
