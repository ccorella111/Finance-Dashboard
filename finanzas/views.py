from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
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