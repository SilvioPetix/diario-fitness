import base64
from PIL import Image
import json
from django.http import HttpResponse, JsonResponse
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
from django.shortcuts import get_object_or_404

from django.utils.decorators import method_decorator

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import csv

from .models import Allenamento, DiarioAlimentare, BenessereGiornaliero, Misurazione
from .forms import AllenamentoForm, DiarioAlimentareForm, BenessereGiornalieroForm, MisurazioneForm

from django.db.models import Avg


from django.views.decorators.csrf import csrf_exempt



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
#LIST
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

#CREATE
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

#UPDATE
class GenericUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'diario/generics_view/generic_form.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))

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

#DELETE
class GenericDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'diario/generics_view/generic_confirm_delete.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))

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
    

#ESPORTAZIONE DOWNLOAD


from .models import Allenamento, BenessereGiornaliero, Misurazione

class ExportDataView(LoginRequiredMixin, View):
    def get(self, request):
        tipo = request.GET.get('tipo')
        formato = request.GET.get('formato')

        if not tipo or not formato:
            return render(request, 'diario/export_data_form.html')

        if tipo not in ['allenamento', 'benessere', 'misurazione']:
            return HttpResponse("Tipo non valido", status=400)

        data_inizio = request.GET.get('data_inizio')
        data_fine = request.GET.get('data_fine')

        # Recupera i dati
        qs = self.get_queryset(tipo, request.user, data_inizio, data_fine)

        if formato == 'csv':
            return self.export_csv(tipo, qs)
        elif formato == 'pdf':
            return self.export_pdf(tipo, qs)
        else:
            return HttpResponse("Formato non supportato", status=400)

    def get_queryset(self, tipo, user, data_inizio, data_fine):
        if tipo == 'allenamento':
            qs = Allenamento.objects.filter(user=user)
        elif tipo == 'benessere':
            qs = BenessereGiornaliero.objects.filter(user=user)
        else:
            qs = Misurazione.objects.filter(user=user)

        if data_inizio:
            qs = qs.filter(data__gte=data_inizio)
        if data_fine:
            qs = qs.filter(data__lte=data_fine)

        return qs

    def export_csv(self, tipo, qs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{tipo}.csv"'
        writer = csv.writer(response)

        if tipo == 'allenamento':
            writer.writerow(['Data', 'Giorno', 'Esercizio', 'Serie', 'Ripetizioni', 'Peso', 'Note'])
            for obj in qs:
                writer.writerow([obj.data, obj.giorno, obj.esercizio, obj.serie, obj.ripetizioni, obj.peso, obj.note])
        
        elif tipo == 'benessere':
            writer.writerow(['Data', 'Acqua (litri)', 'Sigarette Fumate', 'Note'])
            for obj in qs:
                writer.writerow([obj.data, obj.acqua_litri, obj.sigarette_fumate, obj.note])

        else:  # misurazione
            writer.writerow(['Data', 'Sesso', 'Altezza', 'Peso', 'Vita', 'Collo', 'Fianchi', 'Note', 'BMI', 'BMI Descrizione', 'BFM'])
            for obj in qs:
                writer.writerow([
                    obj.data, obj.sesso, obj.altezza_cm, obj.peso_kg, obj.vita_cm,
                    obj.collo_cm, obj.fianchi_cm, obj.note,
                    obj.bmi_valore, obj.bmi_descr, obj.bfm
                ])

        return response

    def export_pdf(self, tipo, qs):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Report {tipo.capitalize()}")
        y -= 30

        if tipo == 'allenamento':
            headers = ['Data', 'Giorno', 'Esercizio', 'Serie', 'Ripetizioni', 'Peso', 'Note']
            rows = [[obj.data, obj.giorno, obj.esercizio, obj.serie, obj.ripetizioni, obj.peso, obj.note] for obj in qs]
        elif tipo == 'benessere':
            headers = ['Data', 'Acqua (litri)', 'Sigarette Fumate', 'Note']
            rows = [[obj.data, obj.acqua_litri, obj.sigarette_fumate, obj.note] for obj in qs]
        else:  # misurazione
            headers = ['Data', 'Sesso', 'Altezza', 'Peso', 'Vita', 'Collo', 'Fianchi', 'Note', 'BMI', 'BMI Descrizione', 'BFM']
            rows = [[
                obj.data, obj.sesso, obj.altezza_cm, obj.peso_kg, obj.vita_cm,
                obj.collo_cm, obj.fianchi_cm, obj.note,
                obj.bmi_valore, obj.bmi_descr, obj.bfm
            ] for obj in qs]

        def draw_table_header():
            x = 50
            p.setFont("Helvetica-Bold", 10)
            for header in headers:
                p.drawString(x, y, str(header))
                x += 70
            return y - 20

        def draw_table_rows(start_y):
            nonlocal y
            p.setFont("Helvetica", 9)
            for row in rows:
                x = 50
                for col in row:
                    p.drawString(x, y, str(col))
                    x += 70
                y -= 15
                if y < 40:
                    p.showPage()
                    y = height - 50
                    y = draw_table_header()

        y = draw_table_header()
        draw_table_rows(y)

        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="{tipo}.pdf"'
        })

#ESPORTAZIONI GRAFICI
from PIL import Image
from reportlab.lib.utils import ImageReader
import base64
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class ExportGraficoPDFView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            image_data = data.get("image")
            tipo = data.get("tipo", "grafico")

            if not image_data:
                return JsonResponse({"error": "Immagine mancante"}, status=400)

            # Rimuovi il prefisso data URL
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            image_buffer = BytesIO(image_bytes)

            # Apri con Pillow
            pil_img = Image.open(image_buffer)

            # Converti in RGB se necessario
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')

            # Crea ImageReader da PIL
            img_reader = ImageReader(pil_img)

            pdf_buffer = BytesIO()
            p = canvas.Canvas(pdf_buffer, pagesize=letter)
            width, height = letter

            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, height - 50, f"Grafico: {tipo.capitalize()}")

            # Disegna immagine usando ImageReader
            p.drawImage(img_reader, 50, height / 2 - 100, width=500, preserveAspectRatio=True, mask='auto')

            p.showPage()
            p.save()
            pdf_buffer.seek(0)

            return HttpResponse(pdf_buffer, content_type='application/pdf', headers={
                "Content-Disposition": f'attachment; filename="{tipo}_grafico.pdf"'
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
