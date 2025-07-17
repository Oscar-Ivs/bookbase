# books/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Register view (must match what's referenced in urls.py)
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def my_collection(request):
    return render(request, 'my_collection.html')
def profile(request):
    return render(request, 'profile.html')
# This file contains views for user registration, home, about, and collection pages.
# The 'register' view handles user registration and login, while 'home', 'about',
# and 'my_collection' render their respective templates.

