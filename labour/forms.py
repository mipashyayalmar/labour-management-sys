from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import LabourEntry

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ईमेल'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label

class LabourEntryForm(forms.ModelForm):
    class Meta:
        model = LabourEntry
        fields = ['date', 'in_time', 'out_time', 'pargi_name', 'labour_name', 
                  'quantity', 'rupees_per_head', 'land_crop_name', 'owner_name', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'in_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'out_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'pargi_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., गट १, गट २'}),
            'labour_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., रमेश'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'मजुरांची संख्या', 'min': '1'}),
            'rupees_per_head': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'दर प्रति व्यक्ती', 'min': '0', 'step': '0.01'}),
            'land_crop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ऊस, गहू'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'मालकाचे नाव'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'अतिरिक्त माहिती'}),
        }