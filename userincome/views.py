from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.


def search_income(request):


    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText', '').strip().lower()

        
        if len(search_str) < 2:
            return JsonResponse([], safe=False)

        income = UserIncome.objects.filter(
            Q(description__icontains=search_str) |
            Q(source__icontains=search_str) |
            Q(amount__icontains=search_str),
            owner=request.user
        )

        data = income.values('id', 'amount', 'source', 'description', 'date')
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    user_pref = UserPreference.objects.get_or_create(user=request.user)[0]
    currency = user_pref.currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency' : currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()

    context = {
        'sources': sources,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        source = request.POST.get('source')
        date = request.POST.get('expense_date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)

        if not date:
            date = timezone.now().date()


        UserIncome.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            source=source,
            description=description
        )
        messages.success(request, 'Record saved successfully')

        return redirect('income')
    
@login_required(login_url='/authentication/login')
def income_edit(request, id):
        income = UserIncome.objects.get(pk=id)
        sources = Source.objects.all()
        context = {
            'income': income,
            'values': income,
            'sources': sources
        }
        if request.method == 'GET':
            return render(request, 'income/edit_income.html', context)
        if request.method == 'POST':
            amount = request.POST.get('amount')

            if not amount:
                messages.error(request, 'Amount is required')
                return render(request, 'income/edit_income.html', context)
            description = request.POST.get('description')
            date = request.POST.get('income_date')
            source = request.POST.get('source')


            if not date:
                date = timezone.now().date()

            if not description:
                messages.error(request, 'description is required')
                return render(request, 'income/edit_income.html', context)

            income.owner = request.user
            income.amount = amount
            income. date = date
            income.source = source
            income.description = description

            income.save()
            messages.success(request, 'Record updated  successfully')

            return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income removed')
    return redirect('income')
