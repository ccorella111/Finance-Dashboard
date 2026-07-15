from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction,IncomeForm
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.urls import reverse

# Create your views here.

@login_required
def dashboard_view(request):
    
    return render(request,'finanzas/dashboard.html')


def login_view(request):

    if request.method == 'POST':
        userCred = request.POST.get('username')
        key = request.POST.get('password')

        user = authenticate(request, username=userCred, password=key)

        if user is not None:
            login(request, user)

            return redirect('dashboard')
        else:
            messages.error(request, 'Datos ingresados incorrectos')
            return render(request, 'auth/login.html')
        
    return render(request, 'auth/login.html')



def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        key = request.POST.get('registerPassword')
        confirmKey = request.POST.get('confirmPassword')

        if key != confirmKey:
            messages.error(request,'Las contraseñas no coinciden. Intentalo de nuevo')
            return render(request,'auth/register.html')
        
        if User.objects.filter(username = email).exists():
            messages.error(request,'El correo electrónico ya está registrado')
            return render(request,'auth/register.html')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=key,
            first_name=name
        )

        login(request, user)

        return redirect('dashboard')

    return render(request, 'auth/register.html')

@login_required
def register_incomes_view(request):

    ingresos_list = Transaction.objects.filter(usuario = request.user, tipo = 'ingreso').order_by('-fecha')

    paginator = Paginator(ingresos_list, 10)

    page = request.GET.get('page')

    try:
        ingresos = paginator.page(page)
    except PageNotAnInteger:
        ingresos = paginator.page(1)
    except EmptyPage:
        ingresos = paginator.page(paginator.num_pages)

    form_has_errors = False

    if request.method == 'POST':

        form = IncomeForm(request.POST)

        if form.is_valid():
            nuevo_ingreso = form.save(commit=False)
            nuevo_ingreso.usuario = request.user
            nuevo_ingreso.tipo = 'ingreso'
            nuevo_ingreso.categoria = 'ninguna'
            nuevo_ingreso.save()
            messages.success(request, '¡Ingreso registrado exitosamente!')
            return redirect(f"{reverse('register_incomes')}?page={page or 1}")
        form_has_errors = True
        return render(request, 'finanzas/incomes.html', 
                      {'form': form, 'ingresos': ingresos, 'show_modal': True, 'form_has_errors': form_has_errors, 'is_editing': False})
    else:
        form = IncomeForm()

    # Si entra por primera vez (GET), mostramos la página limpia
    return render(request, 'finanzas/incomes.html', 
                  {'form': form, 'ingresos' : ingresos, 'show_modal': False, 'form_has_errors': form_has_errors, 'is_editing': False})



@login_required
def edit_income_register(request, id):

    ingreso = get_object_or_404(Transaction, id=id, usuario=request.user, tipo='ingreso')
    ingresos_list = Transaction.objects.filter(usuario = request.user, tipo = 'ingreso').order_by('-fecha')

    paginator = Paginator(ingresos_list, 10)

    page = request.GET.get('page')

    try:
        ingresos = paginator.page(page)
    except PageNotAnInteger:
        ingresos = paginator.page(1)
    except EmptyPage:
        ingresos = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=ingreso)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Ingreso actualizado exitosamente!')
            return redirect(f"{reverse('register_incomes')}?page={page or 1}")
    else:
        form = IncomeForm(instance=ingreso)

    return render(request, 'finanzas/incomes.html', 
                  {'form':form, 'ingreso': ingreso, 'ingresos': ingresos, 'show_modal': True, 'form_has_errors': False, 'is_editing': True})



@login_required
def delete_income_register(request, id):
    if request.method == 'POST':
        ingreso = get_object_or_404(Transaction, id=id, usuario=request.user, tipo='ingreso')
        ingreso.delete()

    return redirect('register_incomes')


@login_required
def register_expenses_view(request):
    
    return render(request, 'finanzas/expenses.html') 

