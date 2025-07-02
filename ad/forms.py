from django import forms
from .models import ExchangeProposal, Ad
from ad.utils import get_categories
from django.forms import ValidationError

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = [
            'title',
            'description',
            'category',
            'condition'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Bведите название',
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
            'description': 'Oписание товара',
            'category': 'Категория товара',
            'condition': 'Состояние товара'
        }

class ProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = [
            'ad_sender',
            'comment'
        ]
        widgets = {
            'ad_sender': forms.Select(),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Введите коментарий к предложению',
                'max_length': '200',
                'rows': '4'
            })
        }
        labels = {
            'ad_sender': 'Ваше предложение',
            'comment': 'Коментарий к предложению'
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
        fields = [
            'ad_sender',
            'comment'
        ]
        widgets ={
        'ad_sender': forms.Select(),
        'comment': forms.Textarea(attrs={
            'max_length': '150',
            'rows': '4',
            'placeholder': 'Введите коментарий',
            'class': 'form-control' # для bootstrap
        })
        }
        labels = {
            'ad_sender': 'Ваш товар для обмена',
            'comment': 'Коментарий для получателя'
        }

    def clean_ad_sender(self):
        sender = self.cleaned_data.get('ad_sender')
        if not sender:
            raise ValidationError('Выберите 1 из своих обьявлений')
        return sender
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment) < 5:
            raise ValidationError('Минимальный размер комментария 5 символов')
        return comment
        
    # Берем пользователя при прорисовки формы и достаем его обьявления
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)