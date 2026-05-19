from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.db.models import Q
from django.http import JsonResponse
from userpreferences.models import UserPreference
from django.utils import timezone


def search_expenses(request):


    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText', '').strip().lower()

        
        if len(search_str) < 2:
            return JsonResponse([], safe=False)

        expenses = Expense.objects.filter(
            Q(description__icontains=search_str) |
            Q(category__icontains=search_str) |
            Q(amount__icontains=search_str),
            owner=request.user
        )

        data = expenses.values('id', 'amount', 'category', 'description', 'date')
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    user_pref = UserPreference.objects.get_or_create(user=request.user)[0]
    currency = user_pref.currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency' : currency
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expenses(request):
    categories = Category.objects.all()

    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'expenses/add_expenses.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        date = request.POST.get('expense_date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expenses.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expenses.html', context)

        if not date:
            date = timezone.now().date()

        category = Category.objects.get(name=category_id)

        Expense.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            category=category,
            description=description
        )

        return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')


        if not date:
            date = timezone.now().date()

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')