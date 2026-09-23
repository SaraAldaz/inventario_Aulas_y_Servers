from django.contrib import admin

from .models import Piso, Aula


@admin.register(Piso)
class PisoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    ordering = ('numero',)


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'piso', 'capacidad', 'activo')
    list_filter = ('piso', 'activo')
    search_fields = ('codigo', 'nombre')
    ordering = ('piso__numero', 'codigo')