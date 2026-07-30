from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate

# Vistas de Autenticación (HU01)
def login_view(request):
    return render(request, 'agendamiento/auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
