from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction,IncomeForm,ExpenseForm
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.urls import reverse
from django.db.models import Sum

from datetime import datetime,timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth

# Create your views here.

@login_required
def dashboard_view(request):

    ultimos_movimientos = Transaction.objects.filter(usuario=request.user).order_by('-fecha')[:5]

    return render(request, 'finanzas/dashboard.html',{'ultimos_movimientos': ultimos_movimientos,})




@login_required
def dashboard_data_api(request):

    rango = request.GET.get('rango', 'mes')
    hoy = timezone.localtime(timezone.now()).date()

    match rango.lower():
        case 'hoy':
            fecha_inicio = hoy
            fecha_fin = hoy
        case 'semana':
            fecha_inicio = hoy - timedelta(days=7)
            fecha_fin = hoy
        case 'mes':
            fecha_inicio = hoy - timedelta(days=30)
            fecha_fin = hoy
        case 'anio':
            fecha_inicio = hoy - timedelta(days=365)
            fecha_fin = hoy
        case 'personalizado':
            fecha_inicio_str = request.GET.get('fecha_inicio')
            fecha_fin_str = request.GET.get('fecha_fin')

            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Fechas inválidas'}, status=400)
            if fecha_inicio > fecha_fin:
                return JsonResponse({'error': 'La fecha de inicio no puede ser posterior a la fecha final'}, status=400)
        case _:
            fecha_inicio = hoy - timedelta(days=30)
            fecha_fin = hoy

    qs = Transaction.objects.filter(usuario=request.user, fecha__gte=fecha_inicio, fecha__lte=fecha_fin)

    ingresos_totales = float(qs.filter(tipo='ingreso').aggregate(t=Sum('monto'))['t'] or 0)
    gastos_totales = float(qs.filter(tipo='gasto').aggregate(t=Sum('monto'))['t'] or 0)
    balance = ingresos_totales - gastos_totales

    categoria_dict = dict(Transaction.CATEGORIA_CHOICES)
    gastos_categoria = qs.filter(tipo='gasto').values('categoria').annotate(t=Sum('monto')).order_by('-t')
    pie_gastos = {
        'labels': [categoria_dict.get(g['categoria'], g['categoria']) for g in gastos_categoria],
        'data': [float(g['t']) for g in gastos_categoria],
    }

    fuente_dict = dict(Transaction.FUENTE_CHOICES)
    ingresos_fuente = qs.filter(tipo='ingreso').values('fuente').annotate(t=Sum('monto')).order_by('-t')
    pie_ingresos = {
        'labels': [fuente_dict.get(i['fuente'], i['fuente']) for i in ingresos_fuente],
        'data': [float(i['t']) for i in ingresos_fuente],
    }

    dias_rango = (fecha_fin - fecha_inicio).days
    trunc_func = TruncDay if dias_rango <= 60 else TruncMonth
    formato_fecha = '%d/%m' if dias_rango <= 60 else '%b %Y'

    movimientos = (
        qs.annotate(periodo=trunc_func('fecha'))
        .values('periodo', 'tipo')
        .annotate(t=Sum('monto'))
        .order_by('periodo')
    )

    periodos = {}
    for m in movimientos:
        key = m['periodo'].strftime(formato_fecha)
        periodos.setdefault(key, {'ingreso': 0, 'gasto': 0})
        periodos[key][m['tipo']] = float(m['t'])

    linea_labels = list(periodos.keys())
    linea_ingresos = [periodos[k]['ingreso'] for k in linea_labels]
    linea_gastos = [periodos[k]['gasto'] for k in linea_labels]
    linea_balance = []
    acumulado = 0
    for k in linea_labels:
        acumulado += periodos[k]['ingreso'] - periodos[k]['gasto']
        linea_balance.append(round(acumulado, 2))

    return JsonResponse({
        'ingresos_totales': ingresos_totales,
        'gastos_totales': gastos_totales,
        'balance': balance,
        'pie_gastos': pie_gastos,
        'pie_ingresos': pie_ingresos,
        'linea_labels': linea_labels,
        'linea_ingresos': linea_ingresos,
        'linea_gastos': linea_gastos,
        'linea_balance': linea_balance,
    })



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
        messages.success(request, 'Ingreso eliminado correctamente.')

    return redirect('register_incomes')



@login_required
def register_expenses_view(request):

    gastos_list = Transaction.objects.filter(usuario = request.user, tipo = 'gasto').order_by('-fecha')

    paginator = Paginator(gastos_list, 10)

    page = request.GET.get('page')

    try:
        gastos = paginator.page(page)
    except PageNotAnInteger:
        gastos = paginator.page(1)
    except EmptyPage:
        gastos = paginator.page(paginator.num_pages)

    form_has_errors = False

    if request.method == 'POST':

        form = ExpenseForm(request.POST)

        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.usuario = request.user
            new_expense.tipo = 'gasto'
            new_expense.fuente = 'ninguna'
            new_expense.save()
            messages.success(request, '¡Gasto registrado exitosamente!')
            return redirect(f"{reverse('register_expenses')}?page={page or 1}")
        form_has_errors = True
        return render(request, 'finanzas/expenses.html', 
                      {'form': form, 'gastos': gastos, 'show_modal': True, 'form_has_errors': form_has_errors, 'is_editing': False})
    else:
        form = ExpenseForm()

    # Si entra por primera vez (GET), mostramos la página limpia
    return render(request, 'finanzas/expenses.html', 
                  {'form': form, 'gastos' : gastos, 'show_modal': False, 'form_has_errors': form_has_errors, 'is_editing': False})



@login_required
def edit_expense_register(request, id):

    gasto = get_object_or_404(Transaction, id=id, usuario=request.user, tipo='gasto')
    gastos_list = Transaction.objects.filter(usuario = request.user, tipo = 'gasto').order_by('-fecha')

    paginator = Paginator(gastos_list, 10)

    page = request.GET.get('page')

    try:
        gastos = paginator.page(page)
    except PageNotAnInteger:
        gastos = paginator.page(1)
    except EmptyPage:
        gastos = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gasto actualizado exitosamente!')
            return redirect(f"{reverse('register_expenses')}?page={page or 1}")
    else:
        form = ExpenseForm(instance=gasto)

    return render(request, 'finanzas/expenses.html', 
                  {'form':form, 'gasto': gasto, 'gastos': gastos, 'show_modal': True, 'form_has_errors': False, 'is_editing': True})



@login_required
def delete_expense_register(request, id):
    if request.method == 'POST':
        gasto = get_object_or_404(Transaction, id=id, usuario=request.user, tipo='gasto')
        gasto.delete()
        messages.success(request, 'Gasto eliminado correctamente.')

    return redirect('register_expenses')

