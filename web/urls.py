from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.login_usuario, name="login"),
    path("logout/", views.logout_usuario, name="logout"),
    path("piso/<int:piso_id>/", views.aulas_por_piso, name="aulas_por_piso"),
    path("aula/<int:aula_id>/", views.inventario_aula, name="inventario_aula"),
    path(
        "api/aulas-por-piso/<int:piso_id>/",
        views.aulas_por_piso_api,
        name="aulas_por_piso_api",
    ),
    path(
        "computadores/<int:computador_id>",
        views.detalle_computador,
        name="detalle_computador",
    ),
    path("equipo/<int:equipo_id>", views.detalle_equipo, name="detalle_equipo"),
    path(
        "mobiliario/<int:mobiliario_id>/",
        views.detalle_mobiliario,
        name="detalle_mobiliario",
    ),
    path("mobiliario/", views.mobiliario_lista, name="mobiliario_lista"),
    path(
        "api/aula-activo/<str:tipo>/<int:activo_id>/",
        views.aula_activo,
        name="aula_activo",
    ),
    path(
        "inventario/api/aula-activo/<str:tipo>/<int:activo_id>/",
        views.aula_activo,
        name="aula_activo",
    ),
    path("computadores/", views.computadores_lista, name="computadores_lista"),
    path("computadores/nuevo/", views.computador_crear, name="computador_crear"),
    path(
        "computadores/<int:computador_id>/editar/",
        views.computador_editar,
        name="computador_editar",
    ),
    path(
        "computadores/<int:computador_id>/desactivar/",
        views.computador_desactivar,
        name="computador_desactivar",
    ),
    path(
        "computadores/<int:computador_id>/activar/",
        views.computador_activar,
        name="computador_activar",
    ),
    path(
        "equipos/",
        views.equipos_lista,
        name="equipos_lista",
    ),
    path(
        "equipos/nuevo/",
        views.equipo_crear,
        name="equipo_crear",
    ),
    path(
        "pisos/",
        views.pisos_lista,
        name="pisos_lista",
    ),
    path(
        "pisos/nuevo/",
        views.piso_crear,
        name="piso_crear",
    ),
    path(
        "pisos/<int:piso_id>/editar/",
        views.piso_editar,
        name="piso_editar",
    ),
    path(
        "aulas/",
        views.aulas_lista,
        name="aulas_lista",
    ),
    path(
        "aulas/nuevo/",
        views.aula_crear,
        name="aula_crear",
    ),
    path(
        "aulas/<int:aula_id>/editar/",
        views.aula_editar,
        name="aula_editar",
    ),
    path(
        "personal/",
        views.personal_lista,
        name="personal_lista",
    ),
    path(
        "personal/nuevo/",
        views.personal_crear,
        name="personal_crear",
    ),
    path(
        "mantenimientos/",
        views.mantenimientos_lista,
        name="mantenimientos_lista",
    ),
    path(
        "mantenimientos/nuevo/",
        views.mantenimiento_crear,
        name="mantenimiento_crear",
    ),
    path(
        "movimientos/nuevo/",
        views.movimiento_crear,
        name="movimiento_crear",
    ),
    path(
        "movimientos/",
        views.movimientos_lista,
        name="movimientos_lista",
    ),
]
