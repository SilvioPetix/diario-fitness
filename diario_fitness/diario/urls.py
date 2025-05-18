from django.urls import path
from .views import LoginView,RegisterView,IndexView,LogoutView
from .views import GenericListView,GenericCreateView,GenericUpdateView,GenericDeleteView
from .views import GraficiGenericiView,ExportDataView,ExportGraficoPDFView
urlpatterns = [
    path('',IndexView.as_view(),name="index"),
    path('login/', LoginView.as_view(), name='login'),
    path('register/',RegisterView.as_view(),name = 'register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    #URL GENERICI
    path('<str:tipo>/lista/', GenericListView.as_view(), name='lista_generica'),
    path('<str:tipo>/crea/', GenericCreateView.as_view(), name='crea_generica'),
    path('<str:tipo>/<int:pk>/modifica/', GenericUpdateView.as_view(), name='modifica_generica'),
    path('<str:tipo>/<int:pk>/elimina/', GenericDeleteView.as_view(), name='elimina_generica'),
    path('grafici/<str:tipo>/', GraficiGenericiView.as_view(), name='grafici_generico'),

    #URL DOWNLOAD
    path('export/data/', ExportDataView.as_view(), name='export_data'),
    path('export-grafico-pdf/', ExportGraficoPDFView.as_view(), name='export_grafico_pdf'),
    
]