from typing import Optional
from django import forms
from django.forms import ValidationError
from .models import ExchangeProposal, Ad, User
from ad.utils import get_categories

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'placeholder': 'Логин',
            'max_length': '40'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            "placeholder": "Введите пароль",
            'max_length': '50'
        })
    )

class CodeForm(forms.Form):
    code = forms.CharField(
        label='Код с почты',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите код с почты',
            'max_length': '6'
        })
    )

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Ник',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите ник...',
            'max_length': 30,
            'class': 'form-control'
        })
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите свой email...',
            'max_length': 50,
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            raise ValidationError('Минимальная длина ника — 4 символа')
        if len(username) > 30:
            raise ValidationError('Максимальная длина ника — 30 символов')
        return username

        
class SetPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']
        
    password = forms.CharField(
            label='Пароль',
            widget=forms.PasswordInput
        )
    password2 = forms.CharField(
            label='Повторите пароль',
            widget=forms.PasswordInput
        )

    def clean_password2(self) -> str:
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise ValidationError('Пароли не совпадают')
        return cd['password2']
    

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category', 'condition']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Введите название',
                'max_length': '40'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Введите описание товара',
                'max_length': '200',
                'rows': '4'
            }),
            'category': forms.Select(),
            'condition': forms.Select()
        }
        labels = {
            'title': 'Название товара',
            'description': 'Описание товара',
            'category': 'Категория товара',
            'condition': 'Состояние товара'
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={
            'placeholder': 'Название, описание, артикул...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=get_categories(),
        required=False,
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Любая категория'
    )
    condition = forms.ChoiceField(
        choices=[('', 'Любое состояние')] + Ad.CONDITION_CHOICES,
        required=False,
        label='Состояние',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']
        widgets = {
            'ad_sender': forms.Select(),
            'comment': forms.Textarea(attrs={
                'max_length': '150',
                'rows': '4',
                'placeholder': 'Введите комментарий',
                'class': 'form-control'
            })
        }
        labels = {
            'ad_sender': 'Ваш товар для обмена',
            'comment': 'Комментарий для получателя'
        }

    def clean_ad_sender(self) -> Ad:
        sender = self.cleaned_data.get('ad_sender')
        if not sender:
            raise ValidationError('Выберите одно из своих объявлений')
        return sender

    def clean_comment(self) -> str:
        comment = self.cleaned_data.get('comment', '')
        if len(comment.strip()) < 5:
            raise ValidationError('Минимальный размер комментария — 5 символов')
        return comment

    def __init__(self, *args, **kwargs) -> None:
        user: Optional[User] = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)
