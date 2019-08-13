from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import authenticate, login


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if(int(username) >= 1000000):
                    return redirect('student_dashboard')
                else:
                    return redirect('staff_dashboard')
            else:
                return render(request, 'landing/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'landing/login.html', {'error_message': 'Invalid login'})
    return render(request, 'landing/login.html')


def user_logout(request):
    auth.logout(request)
    return redirect('user_login')
