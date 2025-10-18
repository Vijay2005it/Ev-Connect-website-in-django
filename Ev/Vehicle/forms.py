from django import forms
from .models import CustomUser,AddBunker

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'zip', 'password']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password Mismatched")
        
        if CustomUser.objects.filter(username = username).exists():
            raise forms.ValidationError('User Already Exist')
        
        if CustomUser.objects.filter(email = email).exists():
            raise forms.ValidationError("Email Already Exists")


class LoginForm(forms.Form):
    username = forms.CharField(label= "User Name" , max_length=150)
    password = forms.CharField(label= "Password", widget= forms.PasswordInput)


class BunkerForm(forms.ModelForm):
    class Meta:
        model = AddBunker
        fields = ['bunker_name', 'location', 'slots', 'rate', 'description', 'image']
