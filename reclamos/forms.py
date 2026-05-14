from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _ 
from .models import Reclamo, Respuesta, TipoProblema


# ==========================================
# WIDGET 
# ==========================================
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


# FileInput.value_from_datadict usa getlist()
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    # hay sobreescribir el método clean(), para leer la lista de archivos
    def clean(self, data, initial=None):
        if not data:
            if self.required:
                raise forms.ValidationError(self.error_messages['required'], code='required')
            return []
        if isinstance(data, (list, tuple)):
            return [super(MultipleFileField, self).clean(f, initial) for f in data]
        return [super(MultipleFileField, self).clean(data, initial)]


# ==========================================
# FORMULARIO DE RECLAMOS
# ==========================================
class ReclamoForm(ModelForm):
    # Campo extra para subir múltiples archivos
    archivos = MultipleFileField(
        label=_('Evidencias (Mínimo 1, máximo 10)'),
        widget=MultipleFileInput(attrs={
            'accept': 'image/png, image/jpeg, application/pdf'
        }),
        required=True
    )

    class Meta:
        model = Reclamo
        fields = [
            'tipo_problema', 
            'variedad_rosa', 
            'numero_guia_master', 
            'fecha_despacho', 
            'descripcion'
        ]
        widgets = {
            'tipo_problema': forms.Select(attrs={'class': 'form-input'}),
            'variedad_rosa': forms.TextInput(attrs={'class': 'form-input'}),
            'numero_guia_master': forms.TextInput(attrs={'class': 'form-input'}),
            'fecha_despacho': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo los tipos de problemas activos
        self.fields['tipo_problema'].queryset = TipoProblema.objects.filter(activo=True)
        
        # Personalizar etiquetas (Listo para traducciones futuras)
        self.fields['tipo_problema'].label = _('Tipo de Problema')
        self.fields['variedad_rosa'].label = _('Variedad de rosa')
        self.fields['numero_guia_master'].label = _('Número de Guía Master')
        self.fields['fecha_despacho'].label = _('Fecha de despacho')
        self.fields['descripcion'].label = _('Descripción detallada')


# ==========================================
# FORMULARIO DE RESPUESTAS
# ==========================================
class RespuestaForm(ModelForm):
    class Meta:
        model = Respuesta
        fields = ['mensaje', 'es_interno']
        widgets = {
            'mensaje': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'es_interno': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'mensaje': _('Mensaje'),
            'es_interno': _('Nota interna (No visible para el cliente)'),
        }