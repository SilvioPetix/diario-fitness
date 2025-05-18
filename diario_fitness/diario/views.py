from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from .forms import LoginForm, RegisterForm
from django.contrib import messages  # opzionale per messaggi flash
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,UpdateView,DeleteView,TemplateView

from .models import Allenamento, DiarioAlimentare, BenessereGiornaliero, Misurazione
from .forms import AllenamentoForm, DiarioAlimentareForm, BenessereGiornalieroForm, MisurazioneForm

# diario/config.py (crea questo file)

from .models import Allenamento, DiarioAlimentare, BenessereGiornaliero, Misurazione
from .forms import AllenamentoForm, DiarioAlimentareForm, BenessereGiornalieroForm, MisurazioneForm
from django.db.models import Avg



MODELS_CONFIG = {
    'allenamento': {
        'model': Allenamento,
        'form': AllenamentoForm,
        'campi': ['data', 'giorno', "esercizio",'serie', 'ripetizioni', 'peso', 'note'],  
        'colonne': ['Data', 'Giorno','Esercizio', 'Serie', 'Ripetizioni', 'Peso', 'Note'],
        'filtri': [
            {'nome': 'data', 'label': 'Data', 'tipo': 'date'},
            {'nome': 'giorno', 'label': 'Giorno', 'tipo': 'text'},
        ],
        'success_url_name': 'lista_generica',
    },

    'alimentare': {
        'model': DiarioAlimentare,
        'form': DiarioAlimentareForm,
        'campi': ['data', 'tipologia_pasto', 'descrizione', 'calorie', 'note'],
        'colonne': ['Data', 'Tipologia Pasto', 'Descrizione', 'Calorie', 'Note'],
        'filtri': [
            {'nome': 'data', 'label': 'Data', 'tipo': 'date'},
        ],
        'success_url_name': 'lista_generica',
    },

    'benessere': {
        'model': BenessereGiornaliero,
        'form': BenessereGiornalieroForm,
        'campi': ['data', 'acqua_litri', 'sigarette_fumate', 'note'],
        'colonne': ['Data', 'Acqua Bevuta (litri)', 'Numero Sigarette Fumate', 'Note'],
        'filtri': [
            {'nome': 'data', 'label': 'Data', 'tipo': 'date'},
        ],
        'success_url_name': 'lista_generica',
    },

    'misurazione': {
        'model': Misurazione,
        'form': MisurazioneForm,
        'campi': ['data', 'sesso', 'altezza_cm', 'peso_kg', 'vita_cm', 'collo_cm', 'fianchi_cm', 'note', 'bmi_valore', 'bmi_descr', 'bfm'],
        'colonne': ['Data', 'Sesso', 'Altezza (cm)', 'Peso (Kg)', 'Vita (cm)', 'Collo (cm)', 'Fianchi (cm)', 'Note', 'BMI', 'BMI Descrizione', 'BFM'],
        'filtri': [
            {'nome': 'data', 'label': 'Data', 'tipo': 'date'},
            {'nome': 'giorno', 'label': 'Giorno', 'tipo': 'text'},
        ],
        'success_url_name': 'lista_generica',
    },
}




#LOGIN

class LoginView(View):
    template_name = 'diario/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Credenziali non valide.")  # opzionale
        return render(request, self.template_name, {'form': form})

#REGISTRAZIONI
class RegisterView(View):
    template_name = 'diario/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # salva utente senza fare login automatico
            messages.success(request, "Registrazione completata, ora effettua il login.")
            return redirect('login')  # rimanda al login
        else:
            messages.error(request, "Registrazione non valida.")  # opzionale
        return render(request, self.template_name, {'form': form})

#LOGOUT
class LogoutView(View):
    def get(self, request):
        logout(request)  # elimina la sessione e sloggati
        return redirect('login')  # reindirizza al login


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'diario/index.html'


#Views generiche:crea,modifica,elimina,visualizza

class GenericListView(LoginRequiredMixin, ListView):
    template_name = 'diario/generics_view/generic_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.tipo = kwargs.get('tipo')
        if self.tipo not in MODELS_CONFIG:
            return redirect('index')  # o 404
        self.config = MODELS_CONFIG[self.tipo]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.config['model'].objects.filter(user=self.request.user).order_by('-data')
        for filtro in self.config['filtri']:
            valore = self.request.GET.get(filtro['nome'])
            if valore:
                kwargs = {filtro['nome']: valore}
                qs = qs.filter(**kwargs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = self.tipo
        context['campi'] = self.config['campi']
        context['colonne'] = self.config['colonne']
        context['filtri'] = self.config['filtri']
        context['titolo'] = f"{self.tipo.capitalize()} - Lista"
        return context


class GenericCreateView(LoginRequiredMixin, CreateView):
    template_name = 'diario/generics_view/generic_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.tipo = kwargs.get('tipo')
        if self.tipo not in MODELS_CONFIG:
            return redirect('index')
        self.config = MODELS_CONFIG[self.tipo]
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.config['form']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('lista_generica', kwargs={'tipo': self.tipo})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titolo'] = f"Crea {self.tipo.capitalize()}"
        context['tipo'] = self.tipo
        context['url_ritorno'] = self.get_success_url()
        return context


class GenericUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'diario/generics_view/generic_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.tipo = kwargs.get('tipo')
        if self.tipo not in MODELS_CONFIG:
            return redirect('index')
        self.config = MODELS_CONFIG[self.tipo]
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.config['form']

    def get_queryset(self):
        return self.config['model'].objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('lista_generica', kwargs={'tipo': self.tipo})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titolo'] = f"Modifica {self.tipo.capitalize()}"
        context['tipo'] = self.tipo
        context['url_ritorno'] = self.get_success_url()
        return context


class GenericDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'diario/generics_view/generic_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.tipo = kwargs.get('tipo')
        if self.tipo not in MODELS_CONFIG:
            return redirect('index')
        self.config = MODELS_CONFIG[self.tipo]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.config['model'].objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('lista_generica', kwargs={'tipo': self.tipo})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = self.tipo
        context['titolo'] = f"Elimina {self.tipo.capitalize()}"
        context['url_ritorno'] = self.get_success_url()
        return context


#GRAFICI


class GraficiGenericiView(LoginRequiredMixin, TemplateView):
    template_name = 'diario/generics_view/grafici_generici.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo = self.kwargs.get('tipo')

        if tipo == 'benessere':
            qs = BenessereGiornaliero.objects.filter(user=self.request.user).order_by('data')
            context['dateLabels'] = [b.data.strftime('%Y-%m-%d') for b in qs]
            context['dati'] = {
                'sigarette': [b.sigarette_fumate for b in qs],
                'acqua': [float(b.acqua_litri) for b in qs],
            }

        elif tipo == 'indici':
            qs = Misurazione.objects.filter(user=self.request.user).order_by('data')
            context['dateLabels'] = [m.data.strftime('%Y-%m-%d') for m in qs]
            context['dati'] = {
                'bmi': [float(m.bmi_valore) if m.bmi_valore else None for m in qs],
                'bfm': [float(m.bfm) if m.bfm else None for m in qs],
            }

        elif tipo == 'misurazioni':
            qs = Misurazione.objects.filter(user=self.request.user).order_by('data')
            context['dateLabels'] = [m.data.strftime('%Y-%m-%d') for m in qs]
            context['dati'] = {
                'collo': [m.collo_cm for m in qs],
                'vita': [m.vita_cm for m in qs],
                'fianchi': [m.fianchi_cm for m in qs],
            }

        else:
            context['dateLabels'] = []
            context['dati'] = {}

        return context


