from django.db import models
from django.contrib.auth.models import User
from django import forms

# Create your models here.
class Transaction (models.Model):

    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    # Categorías específicas para los Gastos
    CATEGORIA_CHOICES = [
        ('ninguna', 'Ninguna / Ingreso'),
        ('comida', 'Comida'),
        ('agua', 'Agua'),
        ('electricidad', 'Electricidad'),
        ('gas', 'Gas'),
        ('recreacion', 'Recreación'),
        ('entretenimiento', 'Entretenimiento'),
        ('pago_deudas', 'Pago de deudas'),
        ('otros', 'Otros'),
    ]

    # Fuentes específicas para los Ingresos (Basado en tus <option>)
    FUENTE_CHOICES = [
        ('ninguna', 'Ninguna / Gasto'), # Para los gastos que no llevan fuente de ingreso
        ('salario', 'Salario'),
        ('servicios_profesionales', 'Servicios Profesionales'),
        ('freelance', 'Freelance'),
        ('dividendos', 'Dividendos'),
        ('intereses', 'Intereses'),
        ('ventas', 'Ventas'),
        ('obsequios', 'Obsequios'),
        ('otros', 'Otros'),
    ]

    # Campos en común
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    #campos específicos
    fuente = models.CharField(max_length=30, choices=FUENTE_CHOICES, default='ninguna')
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES, default='ninguna')

    fecha = models.DateField()

    def __str__(self):

        return f"{self.tipo.upper()} - {self.descripcion} - (${self.monto}) - {self.fecha}"
    


class IncomeForm(forms.ModelForm):

    FUENTE_CHOICES = [
        ('', 'Seleccione una opción'), # Opción por defecto
        ('salario', 'Salario'),
        ('servicios_profesionales', 'Servicios Profesionales'),
        ('freelance', 'Freelance'),
        ('dividendos', 'Dividendos'),
        ('intereses', 'Intereses'),
        ('ventas', 'Ventas'),
        ('obsequios', 'Obsequios'),
        ('otros', 'Otros'),
    ]

    fuente= forms.ChoiceField(
        choices=FUENTE_CHOICES,
        widget = forms.Select(attrs={
                'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500'
            })
    )

    class Meta:
        model = Transaction
        fields = ['descripcion', 'monto', 'fuente', 'fecha']
        widgets = {
            'descripcion' : forms.TextInput(attrs={
                'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500',
                'placeholder': "Ej: Pago de Freelance"
            }),
            'monto' : forms.NumberInput(attrs={
                'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500', 
                'step': '0.01',
                'placeholder': "0.00"
            }),
            'fecha': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500'
            }),
        }
