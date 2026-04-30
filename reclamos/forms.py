from django import forms
from django.core.exceptions import ValidationError
from .models import Reclamo, Evidencia, Respuesta


# Widget personalizado que SÍ permite múltiples archivos
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class ReclamoForm(forms.ModelForm):
    archivos = forms.FileField(
        label='Evidencia (fotos o videos)',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-input',
            'accept': 'image/*,video/*'
        })
    )

    class Meta:
        model = Reclamo
        fields = [
            'numero_cargamento', 'fecha_reclamo', 'variedad_rosa',
            'cantidad_afectada', 'tipo_problema', 'descripcion'
        ]
        widgets = {
            'numero_cargamento': forms.TextInput(attrs={'class': 'form-input'}),
            'fecha_reclamo': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'variedad_rosa': forms.TextInput(attrs={'class': 'form-input'}),
            'cantidad_afectada': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'tipo_problema': forms.Select(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
        }

    def clean_archivos(self):
        archivos = self.files.getlist('archivos')
        for archivo in archivos:
            if archivo.size > 10 * 1024 * 1024:
                raise ValidationError(f'El archivo "{archivo.name}" excede el límite de 10 MB.')
        return archivos


class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 4,
                'placeholder': 'Escriba su respuesta...'
            })
        }