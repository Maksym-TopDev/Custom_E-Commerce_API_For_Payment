from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

# Create your views here.
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username} successfully. You can now log in.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})
