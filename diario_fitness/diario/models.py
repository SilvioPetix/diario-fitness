from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
import math


#Modelli


#Modello Allenamento
class Allenamento(models.Model):
    GIORNI = [
        ('giorno1', 'Giorno 1'),
        ('giorno2', 'Giorno 2'),
        ('giorno3', 'Giorno 3'),
        ('giorno4', 'Giorno 4'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    giorno = models.CharField(max_length=10, choices=GIORNI)
    esercizio = models.CharField(max_length=20,null=True,blank=True)
    serie = models.PositiveIntegerField()
    ripetizioni = models.PositiveIntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso in kg")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.giorno} - {self.data}"
    
    class Meta:
        verbose_name_plural = "Allenamenti"

class DiarioAlimentare(models.Model):
    TIPOLOGIE_PASTO = [
        ('colazione', 'Colazione'),
        ('spuntino_mattina', 'Spuntino Mattina'),
        ('pranzo', 'Pranzo'),
        ('spuntino_pomeriggio', 'Spuntino Pomeriggio'),
        ('cena', 'Cena'),
        ('spuntino_sera', 'Spuntino Sera'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    tipologia_pasto = models.CharField(max_length=20, choices=TIPOLOGIE_PASTO)
    descrizione = models.TextField(help_text="Cosa hai mangiato?")
    calorie = models.PositiveIntegerField(null=True, blank=True, help_text="Calorie (facoltativo)")
    note = models.TextField(blank=True, help_text="Note aggiuntive (facoltative)")

    def __str__(self):
        return f"{self.user.username} - {self.tipologia_pasto} - {self.data}"
    
    class Meta:
        verbose_name_plural = "Diario Alimentare"

class BenessereGiornaliero(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField(unique=True)
    acqua_litri = models.DecimalField(max_digits=4, decimal_places=2, help_text="Litri di acqua bevuti")
    sigarette_fumate = models.PositiveIntegerField(help_text="Numero di sigarette fumate", default=0)
    note = models.TextField(blank=True, help_text="Note personali")

    def __str__(self):
        return f"{self.user.username} - Benessere {self.data}"
    
    class Meta:
        verbose_name_plural = "Benessere Giornaliero"
    




class Misurazione(models.Model):
    SESSO = [
        ('M', 'Maschio'),
        ('F', 'Femmina'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    sesso = models.CharField(max_length=1, choices=SESSO)

    altezza_cm = models.PositiveIntegerField(help_text="In cm")
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)

    vita_cm = models.PositiveIntegerField(help_text="Circonferenza vita (cm)")
    collo_cm = models.PositiveIntegerField(help_text="Circonferenza collo (cm)")
    fianchi_cm = models.PositiveIntegerField(null=True, blank=True, help_text="Solo per donne (cm)")

    note = models.TextField(blank=True)

    # Nuovi campi per BMI salvati
    bmi_valore = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi_descr = models.CharField(max_length=20, null=True, blank=True)

    bfm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    @property
    def calcola_bmi(self):
        altezza_m = Decimal(self.altezza_cm) / Decimal('100')  # converto altezza in Decimal
        peso = self.peso_kg  # già Decimal

        if altezza_m > 0:
            bmi = peso / (altezza_m ** 2)
            return float(bmi)  # se vuoi tornare float (opzionale)
        else:
            return 0.0

    def calcola_descrizione_bmi(self, bmi):
        if bmi is None:
            return None
        if bmi < 18.5:
            return "Sottopeso"
        elif 18.5 <= bmi < 25:
            return "Normopeso"
        elif 25 <= bmi < 30:
            return "Sovrappeso"
        elif 30 <= bmi < 35:
            return "Obeso"
        else:
            return "Obesità estrema"

    def calcola_bfm(self):
        try:
            if self.sesso == 'M':
                return round(
                    495 / (1.0324 - 0.19077 * math.log10(self.vita_cm - self.collo_cm) + 0.15456 * math.log10(self.altezza_cm)) - 450,
                    2
                )
            elif self.sesso == 'F' and self.fianchi_cm:
                return round(
                    495 / (1.29579 - 0.35004 * math.log10(self.vita_cm + self.fianchi_cm - self.collo_cm) + 0.22100 * math.log10(self.altezza_cm)) - 450,
                    2
                )
        except (ValueError, ZeroDivisionError):
            return None

    def save(self, *args, **kwargs):
        bmi = self.calcola_bmi  # senza ()
        self.bmi_valore = round(bmi, 2) if bmi is not None else None
        self.bmi_descr = self.calcola_descrizione_bmi(bmi)
        # salva il valore calcolato di bfm nel campo
        self.bfm = self.calcola_bfm()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.data}"

    class Meta:
        verbose_name_plural = "Misurazioni"
