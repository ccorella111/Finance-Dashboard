from django.shortcuts import render

# Create your views here.

def dashboard_view(request):
    
    return render(request,'finanzas/dashboard.html')

def login_view(request):

    return render(request, 'auth/login.html')

def register_view(request):

    return render(request, 'auth/register.html')
