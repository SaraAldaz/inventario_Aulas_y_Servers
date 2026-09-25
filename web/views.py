from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from django.contrib.contenttypes.models import ContentType
from infraestructura.models import Piso, Aula
from django.contrib.auth.models import User
from inventario.models import (
    Computador,
    ComponenteComputador,
    EquipoTecnologico,
    Mobiliario,
    Mantenimiento,
    MovimientoActivo,
)

from inventario.forms import (
    ComputadorForm,
    MovimientoActivoForm,
    MantenimientoForm,
    EquipoTecnologicoForm,
    PisoForm,
    AulaForm,
    PersonalForm,
)


def login_usuario(request):

    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:

            login(request, usuario)

            return redirect("inicio")

        contexto = {"error": "Usuario o contraseña incorrectos."}

        return render(request, "web/login.html", contexto)

    return render(request, "web/login.html")


def logout_usuario(request):
    logout(request)
    return redirect("login")


@login_required
def inicio(request):

    pisos = Piso.objects.all().order_by("numero")

    es_admin = request.user.groups.filter(
        name="Administradores"
    ).exists()

    es_personal = request.user.groups.filter(
        name="Personal"
    ).exists()

    contexto = {
        "pisos": pisos,
        "es_admin": es_admin,
        "es_personal": es_personal,
    }

    return render(request, "web/inicio.html", contexto)


def aulas_por_piso(request, piso_id):

    piso = get_object_or_404(Piso, id=piso_id)

    aulas = Aula.objects.filter(piso=piso).order_by("codigo")

    contexto = {
        "piso": piso,
        "aulas": aulas,
    }

    return render(request, "web/aulas.html", contexto)


def inventario_aula(request, aula_id):

    aula = get_object_or_404(Aula, id=aula_id)

    computadores = aula.computadores.all()

    equipos = aula.equipos_tecnologicos.all()

    mobiliario = aula.mobiliario.all()

    cantidad_mesas = mobiliario.filter(tipo="MESA").count()

    cantidad_sillas = mobiliario.filter(tipo="SILLA").count()

    contexto = {
        "aula": aula,
        "computadores": computadores,
        "equipos": equipos,
        "mobiliario": mobiliario,
        "cantidad_computadores": computadores.count(),
        "cantidad_equipos": equipos.count(),
        "cantidad_mesas": cantidad_mesas,
        "cantidad_sillas": cantidad_sillas,
    }

    return render(request, "web/inventario_aula.html", contexto)


def detalle_computador(request, computador_id):

    computador = get_object_or_404(Computador, id=computador_id)

    componentes = computador.componentes.all().order_by("tipo")

    mantenimientos = (
        Mantenimiento.objects.filter(
            content_type=ContentType.objects.get_for_model(Computador),
            object_id=computador.id,
        )
        .select_related("responsable")
        .order_by("-fecha")
    )

    movimientos = (
        MovimientoActivo.objects.filter(
            content_type=ContentType.objects.get_for_model(Computador),
            object_id=computador.id,
        )
        .select_related("aula_origen", "aula_destino", "responsable")
        .order_by("-fecha")
    )

    contexto = {
        "computador": computador,
        "componentes": componentes,
        "mantenimientos": mantenimientos,
        "movimientos": movimientos,
    }

    return render(request, "web/detalle_computador.html", contexto)


def detalle_equipo(request, equipo_id):

    equipo = get_object_or_404(EquipoTecnologico, id=equipo_id)

    mantenimientos = (
        Mantenimiento.objects.filter(
            content_type=ContentType.objects.get_for_model(EquipoTecnologico),
            object_id=equipo.id,
        )
        .select_related("responsable")
        .order_by("-fecha")
    )

    movimientos = (
        MovimientoActivo.objects.filter(
            content_type=ContentType.objects.get_for_model(EquipoTecnologico),
            object_id=equipo.id,
        )
        .select_related("aula_origen", "aula_destino", "responsable")
        .order_by("-fecha")
    )

    contexto = {
        "equipo": equipo,
        "mantenimientos": mantenimientos,
        "movimientos": movimientos,
    }

    return render(request, "web/detalle_equipo.html", contexto)


# CRUD EQUIPOS


def equipos_lista(request):
    buscar = request.GET.get("buscar", "").strip()

    equipos = EquipoTecnologico.objects.select_related("aula").all()

    if buscar:

        equipos = equipos.filter(
            models.Q(codigo_inventario__icontains=buscar)
            | models.Q(marca__icontains=buscar)
            | models.Q(modelo__icontains=buscar)
            | models.Q(serial__icontains=buscar)
        )

    equipos = equipos.order_by("tipo", "codigo_inventario")

    contexto = {
        "equipos": equipos,
        "buscar": buscar,
    }

    return render(request, "web/equipos_lista.html", contexto)


def equipo_crear(request):
    if request.method == "POST":

        form = EquipoTecnologicoForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("equipos_lista")

    else:

        form = EquipoTecnologicoForm()

    contexto = {
        "form": form,
        "titulo": "Agregar equipo tecnológico",
    }

    return render(request, "web/equipo_form.html", contexto)


def detalle_mobiliario(request, mobiliario_id):

    mobiliario = get_object_or_404(Mobiliario, id=mobiliario_id)

    mantenimientos = (
        Mantenimiento.objects.filter(
            content_type=ContentType.objects.get_for_model(Mobiliario),
            object_id=mobiliario.id,
        )
        .select_related("responsable")
        .order_by("-fecha")
    )

    contexto = {
        "mobiliario": mobiliario,
        "mantenimientos": mantenimientos,
    }

    return render(request, "web/detalle_mobiliario.html", contexto)


def mobiliario_lista(request):

    buscar = request.GET.get("buscar", "").strip()

    mobiliario = Mobiliario.objects.select_related("aula").all()

    if buscar:

        mobiliario = mobiliario.filter(
            models.Q(codigo_inventario__icontains=buscar)
            | models.Q(aula__codigo__icontains=buscar)
        )

    mobiliario = mobiliario.order_by("tipo", "codigo_inventario")

    contexto = {
        "mobiliario": mobiliario,
        "buscar": buscar,
    }

    return render(request, "web/mobiliario_lista.html", contexto)


def aula_activo(request, tipo, activo_id):

    modelos = {
        "computador": Computador,
        "componente": ComponenteComputador,
        "equipo": EquipoTecnologico,
        "mobiliario": Mobiliario,
    }

    modelo = modelos.get(tipo)

    if not modelo:

        return JsonResponse({"error": "Tipo de activo no válido."}, status=400)

    try:

        activo = modelo.objects.get(pk=activo_id)

    except modelo.DoesNotExist:

        return JsonResponse({"error": "El activo no existe."}, status=404)

    # ============================================================
    # OBTENER AULA
    # ============================================================

    if isinstance(activo, Computador):

        aula = activo.aula

    elif isinstance(activo, EquipoTecnologico):

        aula = activo.aula

    elif isinstance(activo, Mobiliario):

        aula = activo.aula

    elif isinstance(activo, ComponenteComputador):

        aula = activo.computador.aula

    else:

        aula = None

    # ============================================================
    # VALIDAR AULA
    # ============================================================

    if not aula:

        return JsonResponse(
            {"aula": "", "error": "El activo no tiene un aula asignada."}
        )

    # ============================================================
    # RESPUESTA
    # ============================================================

    return JsonResponse(
        {
            "aula": str(aula),
            "aula_id": aula.id,
            "codigo": aula.codigo,
        }
    )


# Crud computadores


def computadores_lista(request):
    buscar = request.GET.get("buscar", "").strip()
    computadores = (
        Computador.objects.select_related("aula").all().order_by("codigo_inventario")
    )

    if buscar:
        computadores = computadores.filter(
            models.Q(codigo_inventario__icontains=buscar)
            | models.Q(marca__icontains=buscar)
            | models.Q(modelo__icontains=buscar)
        )
    computadores = computadores.order_by("codigo_inventario")
    contexto = {
        "computadores": computadores,
        "buscar": buscar,
    }

    return render(request, "web/computadores_lista.html", contexto)


def computador_crear(request):
    if request.method == "POST":
        form = ComputadorForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("computadores_lista")
    else:
        form = ComputadorForm()

    contexto = {
        "form": form,
        "titulo": "Agregar computador",
    }

    return render(request, "web/computador_form.html", contexto)


def computador_editar(request, computador_id):
    computador = get_object_or_404(Computador, id=computador_id)
    if request.method == "POST":

        form = ComputadorForm(request.POST, instance=computador)

        if form.is_valid():

            form.save()

            return redirect("computadores_lista")

    else:
        form = ComputadorForm(instance=computador)

    contexto = {
        "form": form,
        "computador": computador,
        "titulo": "Editar computador",
    }

    return render(request, "web/computador_form.html", contexto)


def computador_desactivar(request, computador_id):

    computador = get_object_or_404(Computador, id=computador_id)

    if request.method == "POST":

        computador.activo = False

        computador.save(update_fields=["activo"])

        return redirect("computadores_lista")

    contexto = {"computador": computador}

    return render(request, "web/computador_desactivar.html", contexto)


def computador_activar(request, computador_id):
    computador = get_object_or_404(Computador, id=computador_id)

    if request.method == "POST":
        computador.activo = True
        computador.save(update_fields=["activo"])
        return redirect("computadores_lista")

    contexto = {"computador": computador}
    return render(request, "web/computador_activar.html", contexto)


def aulas_por_piso_api(request, piso_id):

    aulas = Aula.objects.filter(
        piso_id=piso_id,
        activo=True,
    ).order_by("codigo")

    datos = []

    for aula in aulas:

        datos.append(
            {
                "id": aula.id,
                "codigo": aula.codigo,
                "nombre": aula.nombre,
            }
        )

    return JsonResponse(
        {
            "aulas": datos,
        }
    )


def pisos_lista(request):
    pisos = Piso.objects.all().order_by("numero")

    contexto = {
        "pisos": pisos,
    }

    return render(request, "web/pisos_lista.html", contexto)


def piso_crear(request):

    if request.method == "POST":

        form = PisoForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("pisos_lista")

    else:

        form = PisoForm()

    contexto = {
        "form": form,
        "titulo": "Agregar piso",
    }

    return render(request, "web/piso_form.html", contexto)


def piso_editar(request, piso_id):

    piso = get_object_or_404(Piso, id=piso_id)

    if request.method == "POST":

        form = PisoForm(request.POST, instance=piso)

        if form.is_valid():

            form.save()

            return redirect("pisos_lista")

    else:

        form = PisoForm(instance=piso)

    contexto = {
        "form": form,
        "piso": piso,
        "titulo": "Editar piso",
    }

    return render(request, "web/piso_form.html", contexto)


# Crud Aulas


def aulas_lista(request):

    aulas = Aula.objects.select_related("piso").all().order_by("piso__numero", "codigo")

    contexto = {
        "aulas": aulas,
    }

    return render(request, "web/aulas_lista.html", contexto)


def aula_crear(request):

    if request.method == "POST":

        form = AulaForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("aulas_lista")

    else:

        form = AulaForm()

    contexto = {
        "form": form,
        "titulo": "Agregar aula",
    }

    return render(request, "web/aula_form.html", contexto)


def aula_editar(request, aula_id):

    aula = get_object_or_404(Aula, id=aula_id)

    if request.method == "POST":

        form = AulaForm(request.POST, instance=aula)

        if form.is_valid():

            form.save()

            return redirect("aulas_lista")

    else:

        form = AulaForm(instance=aula)

    contexto = {
        "form": form,
        "aula": aula,
        "titulo": "Editar aula",
    }

    return render(request, "web/aula_form.html", contexto)


# Crud personal


def personal_lista(request):

    personal = User.objects.all().order_by("first_name", "last_name")

    contexto = {
        "personal": personal,
    }

    return render(request, "web/personal_lista.html", contexto)


def personal_crear(request):

    if request.method == "POST":

        form = PersonalForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("personal_lista")

    else:

        form = PersonalForm()

    contexto = {
        "form": form,
        "titulo": "Agregar personal",
    }

    return render(request, "web/personal_form.html", contexto)


# Crud Mantenimiento


def mantenimientos_lista(request):

    buscar = request.GET.get("buscar", "").strip()

    mantenimientos = (
        Mantenimiento.objects.select_related("responsable", "content_type")
        .all()
        .order_by("-fecha")
    )

    if buscar:

        mantenimientos = mantenimientos.filter(
            models.Q(responsable__username__icontains=buscar)
            | models.Q(responsable__first_name__icontains=buscar)
            | models.Q(responsable__last_name__icontains=buscar)
            | models.Q(
                content_type=ContentType.objects.get_for_model(Computador),
                object_id__in=Computador.objects.filter(
                    codigo_inventario__icontains=buscar
                ).values("id"),
            )
        )

    contexto = {
        "mantenimientos": mantenimientos,
        "buscar": buscar,
    }

    return render(request, "web/mantenimientos_lista.html", contexto)


def mantenimiento_crear(request):

    if request.method == "POST":

        form = MantenimientoForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("mantenimientos_lista")

    else:

        form = MantenimientoForm()

    contexto = {
        "form": form,
        "titulo": "Registrar mantenimiento",
    }

    return render(request, "web/mantenimiento_form.html", contexto)


# Crud Movimientos


def movimiento_crear(request):

    if request.method == "POST":

        form = MovimientoActivoForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("movimientos_lista")

    else:

        form = MovimientoActivoForm()

    contexto = {
        "form": form,
        "titulo": "Registrar movimiento",
    }

    return render(request, "web/movimiento_form.html", contexto)


def movimientos_lista(request):

    buscar = request.GET.get("buscar", "").strip()

    movimientos = (
        MovimientoActivo.objects.select_related(
            "aula_origen",
            "aula_destino",
            "responsable",
            "content_type",
        )
        .all()
        .order_by("-fecha")
    )

    if buscar:

        movimientos = movimientos.filter(
            models.Q(responsable__username__icontains=buscar)
            | models.Q(responsable__first_name__icontains=buscar)
            | models.Q(responsable__last_name__icontains=buscar)
            | models.Q(
                content_type=ContentType.objects.get_for_model(Computador),
                object_id__in=Computador.objects.filter(
                    codigo_inventario__icontains=buscar
                ).values("id"),
            )
            | models.Q(
                content_type=ContentType.objects.get_for_model(EquipoTecnologico),
                object_id__in=EquipoTecnologico.objects.filter(
                    codigo_inventario__icontains=buscar
                ).values("id"),
            )
            | models.Q(
                content_type=ContentType.objects.get_for_model(Mobiliario),
                object_id__in=Mobiliario.objects.filter(
                    codigo_inventario__icontains=buscar
                ).values("id"),
            )
        )

    contexto = {
        "movimientos": movimientos,
        "buscar": buscar,
    }

    return render(request, "web/movimientos_lista.html", contexto)
