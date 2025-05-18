from django.contrib import admin
from .models import Allenamento, DiarioAlimentare, Misurazione,BenessereGiornaliero

@admin.register(Allenamento)
class AllenamentiAdmin(admin.ModelAdmin):
    list_display = ['user', 'data', 'giorno', 'esercizio', 'serie', 'ripetizioni', 'peso', 'note']
    list_filter = ['giorno', 'data']
    search_fields = ['user__username', 'esercizio']
    date_hierarchy = 'data'
    ordering = ['-data']

    def esercizio(self, obj):
        return f"{obj.serie} x {obj.ripetizioni} @ {obj.peso} kg"


@admin.register(DiarioAlimentare)
class DiarioAlimentareAdmin(admin.ModelAdmin):
    list_display = ['user', 'data', 'tipologia_pasto', 'descrizione']
    list_filter = ['data']
    search_fields = ['user__username', 'tipologia_pasto', 'descrizione']
    date_hierarchy = 'data'
    ordering = ['-data']


@admin.register(Misurazione)
class MisurazioneAdmin(admin.ModelAdmin):
    list_display = ['user', 'data', 'altezza_cm', 'peso_kg', 'bmi_display', 'bfm_display']
    list_filter = ['data']
    search_fields = ['user__username']
    date_hierarchy = 'data'
    ordering = ['-data']

    def bmi_display(self, obj):
        return obj.bmi()
    bmi_display.short_description = 'BMI'

    def bfm_display(self, obj):
        return obj.bfm()
    bfm_display.short_description = 'BFM %'

@admin.register(BenessereGiornaliero)
class BenessereGiornalieroAdmin(admin.ModelAdmin):
    list_display = ['acqua_litri','sigarette_fumate']
