from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Perfil, AsignacionSecretaria


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfil'


class UserAdminCustom(admin.ModelAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active', 'perfil__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')


# Desregistrar el admin por defecto de User y registrar el custom
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)


@admin.register(AsignacionSecretaria)
class AsignacionSecretariaAdmin(admin.ModelAdmin):
    list_display = ('secretaria', 'cliente', 'is_active', 'assigned_at')
    list_filter = ('is_active',)
    search_fields = ('secretaria__user__first_name', 'cliente__user__first_name', 'cliente__company_name')