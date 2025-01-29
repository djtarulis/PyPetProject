from django import forms
from .models import Pet, Item, CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price']


class DebugLoginView(LoginView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        print("Login POST data:", request.POST)  # Debug: Check the submitted data
        return super().post(request, *args, **kwargs)
