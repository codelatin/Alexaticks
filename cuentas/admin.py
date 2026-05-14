from django.contrib import admin
from django.contrib.auth.models import User
from .models import Perfil, AsignacionVendedor # <-- CAMBIO 1: Importar el modelo correcto


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfil'
    # Puedes añadir esto para que se vea el departamento al crear el usuario desde el admin
    fields = ('role', 'departamento', 'phone', 'company_name', 'country', 'preferred_language') 


class UserAdminCustom(admin.ModelAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'get_departamento')
    list_filter = ('is_active', 'perfil__role', 'perfil__departamento') # <-- CAMBIO 2: Filtro por departamento
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # <-- CAMBIO 3: Método para mostrar el departamento en la lista del admin
    def get_departamento(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil.departamento:
            return obj.perfil.get_departamento_display()
        return "-"
    get_departamento.short_description = 'Departamento'
    get_departamento.admin_order_field = 'perfil__departamento'


# Desregistrar el admin por defecto de User y registrar el custom
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)


# <-- CAMBIO 4: Registrar el nuevo modelo AsignacionVendedor
@admin.register(AsignacionVendedor)
class AsignacionVendedorAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'cliente', 'is_active', 'assigned_at') # <-- CAMBIO 5: 'vendedor' en vez de 'secretaria'
    list_filter = ('is_active',)
    search_fields = (
        'vendedor__user__first_name', 
        'cliente__user__first_name', 
        'cliente__company_name'
    )