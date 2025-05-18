from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Allenamento,DiarioAlimentare,BenessereGiornaliero,Misurazione

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'autocomplete': 'username',       # standard per username
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
        })
    )
    password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'autocomplete': 'new-password',  # standard per password attuale
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aggiorna attributi widget originali per sicurezza
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'username',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
            'placeholder': 'Username',
        })
        self.fields['password'].widget.attrs.update({
            'autocomplete': 'new-password',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
            'placeholder': 'Password',
        })


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'autocomplete': 'username',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'autocomplete': 'new-password',   # nuovo password per registrazione
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
        })
    )
    password2 = forms.CharField(
        label='Conferma Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Conferma Password',
            'autocomplete': 'new-password',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
        })
    )

    class Meta:
        model = User
        fields = ['username']

    def clean_password2(self):
        pw1 = self.cleaned_data.get('password1')
        pw2 = self.cleaned_data.get('password2')

        if pw1 and pw2 and pw1 != pw2:
            raise ValidationError("Le password non coincidono")
        try:
            validate_password(pw1)
        except ValidationError as e:
            raise ValidationError(e)
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class AllenamentoForm(forms.ModelForm):
    class Meta:
        model = Allenamento
        exclude = ['user']  # lo gestiamo nella view

        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'giorno': forms.Select(attrs={'class': 'form-select'}),
            'serie': forms.NumberInput(attrs={'class': 'form-control'}),
            'ripetizioni': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DiarioAlimentareForm(forms.ModelForm):
    class Meta:
        model =DiarioAlimentare
        exclude = ['user']
    
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipologia_pasto':forms.Select(attrs={'class': 'form-select'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'calorie': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BenessereGiornalieroForm(forms.ModelForm):
    class Meta:
        model =BenessereGiornaliero
        exclude = ['user']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'acqua_litri': forms.NumberInput(attrs={'class': 'form-control'}),
            'sigarette_fumate':forms.NumberInput(attrs={'class':'form-control'}),
        }

class MisurazioneForm(forms.ModelForm):
    class Meta:
        model = Misurazione
        exclude = ['user', 'bmi_valore', 'bmi_descr','bfm']  # Escludiamo i campi calcolati

        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sesso': forms.Select(attrs={'class': 'form-select'}),
            'altezza_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vita_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'collo_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'fianchi_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        labels = {
            'altezza_cm': 'Altezza (cm)',
            'peso_kg': 'Peso (kg)',
            'vita_cm': 'Circonferenza vita (cm)',
            'collo_cm': 'Circonferenza collo (cm)',
            'fianchi_cm': 'Fianchi (cm)',
            'note': 'Note personali',
        }
