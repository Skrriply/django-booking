from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

User = get_user_model()


class LoginForm(forms.Form):
    """Форма для входу в обліковий запис."""

    username = forms.CharField(widget=forms.TextInput(), label="Ім'я користувача")
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')


class RegisterForm(UserCreationForm):
    """Форма для реєстрації."""

    class Meta:
        """Метаклас форми, який визначає метадані форми."""

        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]


class ProfileUpdateForm(forms.ModelForm):
    """Форма для оновлення профілю користувача."""

    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomPasswordChangeForm(PasswordChangeForm):
    """Форма для зміни пароля."""

    old_password = forms.CharField(widget=forms.PasswordInput(), label='Старий пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput(), label='Новий пароль')
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(), label='Підтвердження нового пароля'
    )
