from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile

class Loginform(AuthenticationForm):
    """
        Custom login form that accepts username Or email
    """
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or email',
            'autofocus': True
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    error_messages = {
        'invalid_login': 'Invalid username/email or password. Please try again.',
        'inactive': 'This account is inactive.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = "Username or Email"

class CustomeUserCreation(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        # Django automatically calls clean_<fieldname>() methods when validating a form.
        email = self.cleaned_data.get("email") # Using .get() - SAFE (returns None if key doesn't exist)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email
    
class PasswordChange(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use .update to ensure we don't overwrite other important attributes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            print(f"DEBUG: Field {field} now has classes: {field.widget.attrs['class']}")

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell something about yourself..'
            }),
            'profile_pic': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }