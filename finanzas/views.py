from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate

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
            return render(request, 'auth/login.html',{'error' : 'Datos incorrectos'})
        
    return render(request, 'auth/login.html')



def register_view(request):

    return render(request, 'auth/register.html')
