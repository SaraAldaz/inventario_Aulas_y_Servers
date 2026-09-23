from django.contrib import admin

from .models import (
    Computador,
    ComponenteComputador,
    EquipoTecnologico,
    Mobiliario,
    MovimientoActivo,
    Mantenimiento,
)

from .forms import (
    MovimientoActivoForm,
    MantenimientoForm,
)


# ============================================================
# COMPUTADORES
# ============================================================

class ComponenteComputadorInline(admin.TabularInline):
    model = ComponenteComputador
    extra = 0
    max_num = 4


@admin.register(Computador)
class ComputadorAdmin(admin.ModelAdmin):

    list_display = (
        "codigo_inventario",
        "aula",
        "marca",
        "modelo",
        "estado",
        "activo",
    )

    list_filter = (
        "aula",
        "estado",
        "activo",
    )

    search_fields = (
        "codigo_inventario",
        "marca",
        "modelo",
    )

    inlines = [
        ComponenteComputadorInline,
    ]


# ============================================================
# EQUIPOS TECNOLÓGICOS
# ============================================================

@admin.register(EquipoTecnologico)
class EquipoTecnologicoAdmin(admin.ModelAdmin):

    list_display = (
        "codigo_inventario",
        "tipo",
        "aula",
        "marca",
        "modelo",
        "estado",
        "activo",
    )

    list_filter = (
        "tipo",
        "aula",
        "estado",
        "activo",
    )

    search_fields = (
        "codigo_inventario",
        "marca",
        "modelo",
        "serial",
    )


# ============================================================
# MOBILIARIO
# ============================================================

@admin.register(Mobiliario)
class MobiliarioAdmin(admin.ModelAdmin):

    list_display = (
        "codigo_inventario",
        "tipo",
        "aula",
        "estado",
        "activo",
    )

    list_filter = (
        "tipo",
        "aula",
        "estado",
        "activo",
    )

    search_fields = (
        "codigo_inventario",
    )


# ============================================================
# MOVIMIENTOS DE ACTIVOS
# ============================================================

@admin.register(MovimientoActivo)
class MovimientoActivoAdmin(admin.ModelAdmin):

    form = MovimientoActivoForm

    list_display = (
        "fecha",
        "tipo",
        "activo",
        "aula_origen",
        "aula_destino",
        "motivo",
        "responsable",
    )

    list_filter = (
        "tipo",
        "aula_origen",
        "aula_destino",
        "responsable",
    )

    search_fields = (
        "motivo",
        "observaciones",
    )

    autocomplete_fields = (
        "aula_destino",
        "responsable",
    )

    date_hierarchy = "fecha"

    ordering = (
        "-fecha",
    )

    class Media:
        js = (
            "inventario/js/movimiento_activo.js",
        )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        super().save_model(
            request,
            obj,
            form,
            change
        )

        from .services import actualizar_ubicacion

        if obj.aula_destino:

            actualizar_ubicacion(
                obj.activo,
                obj.aula_destino
            )


# ============================================================
# MANTENIMIENTOS
# ============================================================

@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):

    form = MantenimientoForm

    list_display = (
        "fecha",
        "tipo",
        "activo",
        "responsable",
        "estado_anterior",
        "estado_posterior",
    )

    list_filter = (
        "tipo",
        "responsable",
        "estado_anterior",
        "estado_posterior",
    )

    search_fields = (
        "descripcion",
        "observaciones",
    )

    autocomplete_fields = (
        "responsable",
    )

    date_hierarchy = "fecha"

    ordering = (
        "-fecha",
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        super().save_model(
            request,
            obj,
            form,
            change
        )

        from .services import actualizar_estado

        actualizar_estado(
            obj.activo,
            obj.estado_posterior
        )