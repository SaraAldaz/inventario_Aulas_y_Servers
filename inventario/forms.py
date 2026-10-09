from django import forms
from django.contrib.contenttypes.models import ContentType
from infraestructura.models import Aula, Piso
from django.contrib.auth.models import User
from .models import (
    Computador,
    ComponenteComputador,
    EquipoTecnologico,
    Mobiliario,
    MovimientoActivo,
    Mantenimiento,
    SoftwareInstalado,
)


class MovimientoActivoForm(forms.ModelForm):

    TIPO_ACTIVO_CHOICES = [
        ("computador", "Computador"),
        ("componente", "Componente de computador"),
        ("equipo", "Equipo tecnológico"),
        ("mobiliario", "Mobiliario"),
    ]

    tipo_activo = forms.ChoiceField(
        choices=TIPO_ACTIVO_CHOICES,
        label="Tipo de activo",
    )

    activo_seleccionado = forms.ChoiceField(
        choices=[],
        label="Activo",
    )

    aula_origen_mostrada = forms.CharField(
        label="Aula actual",
        required=False,
        disabled=True,
    )

    class Meta:
        model = MovimientoActivo

        fields = [
            "tipo_activo",
            "activo_seleccionado",
            "aula_origen_mostrada",
            "fecha",
            "tipo",
            "aula_destino",
            "motivo",
            "observaciones",
            "responsable",
        ]

        widgets = {
            "fecha": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["fecha"].input_formats = ["%Y-%m-%dT%H:%M"]

        self.fields["responsable"].queryset = User.objects.filter(
            is_active=True
        ).order_by("first_name", "last_name")

        self.fields["responsable"].empty_label = "Seleccione el responsable"

        opciones = []

        for objeto in Computador.objects.select_related("aula").all():

            opciones.append(
                (
                    f"computador:{objeto.pk}",
                    f"Computador - {objeto.codigo_inventario}",
                )
            )

        for objeto in ComponenteComputador.objects.select_related(
            "computador__aula"
        ).all():

            opciones.append(
                (
                    f"componente:{objeto.pk}",
                    f"Componente - {objeto}",
                )
            )

        for objeto in EquipoTecnologico.objects.select_related("aula").all():

            opciones.append(
                (
                    f"equipo:{objeto.pk}",
                    f"{objeto.get_tipo_display()} - " f"{objeto.codigo_inventario}",
                )
            )

        for objeto in Mobiliario.objects.select_related("aula").all():

            opciones.append(
                (
                    f"mobiliario:{objeto.pk}",
                    f"{objeto.get_tipo_display()} - " f"{objeto.codigo_inventario}",
                )
            )

        self.fields["activo_seleccionado"].choices = opciones

        # Mostrar el aula del primer activo seleccionado

        if opciones:

            valor = opciones[0][0]

            tipo_activo, activo_id = valor.split(":")

            modelos = {
                "computador": Computador,
                "componente": ComponenteComputador,
                "equipo": EquipoTecnologico,
                "mobiliario": Mobiliario,
            }

            modelo = modelos[tipo_activo]

            objeto = modelo.objects.get(pk=activo_id)

            aula = self.obtener_aula_activo(objeto)

            if aula:

                self.fields["aula_origen_mostrada"].initial = str(aula)

        if self.instance and self.instance.pk:

            activo = self.instance.activo

            if activo:

                aula = self.obtener_aula_activo(activo)

                if aula:

                    self.fields["aula_origen_mostrada"].initial = str(aula)

    @staticmethod
    def obtener_aula_activo(activo):

        if isinstance(activo, Computador):
            return activo.aula

        if isinstance(activo, EquipoTecnologico):
            return activo.aula

        if isinstance(activo, Mobiliario):
            return activo.aula

        if isinstance(activo, ComponenteComputador):
            return activo.computador.aula

        return None

    def clean(self):

        cleaned_data = super().clean()

        activo_seleccionado = cleaned_data.get("activo_seleccionado")

        tipo_movimiento = cleaned_data.get("tipo")

        aula_destino = cleaned_data.get("aula_destino")

        if not activo_seleccionado:

            return cleaned_data

        try:

            tipo_activo, activo_id = activo_seleccionado.split(":")

        except ValueError:

            raise forms.ValidationError("El activo seleccionado no es válido.")

        modelos = {
            "computador": Computador,
            "componente": ComponenteComputador,
            "equipo": EquipoTecnologico,
            "mobiliario": Mobiliario,
        }

        modelo = modelos.get(tipo_activo)

        if not modelo:

            raise forms.ValidationError("El tipo de activo seleccionado no es válido.")

        try:

            objeto = modelo.objects.get(pk=activo_id)

        except modelo.DoesNotExist:

            raise forms.ValidationError("El activo seleccionado no existe.")

        aula_actual = self.obtener_aula_activo(objeto)

        # Para los movimientos que requieren conocer el origen
        if tipo_movimiento in (
            "TRASLADO",
            "SALIDA",
            "BAJA",
            "REINGRESO",
        ):

            if not aula_actual:

                raise forms.ValidationError(
                    "El activo seleccionado no tiene " "un aula asignada."
                )

        # ------------------------------------------------------------
        # Guardar aula origen automáticamente
        # ------------------------------------------------------------

        if aula_actual:

            cleaned_data["aula_origen"] = aula_actual

            self.fields["aula_origen_mostrada"].initial = str(aula_actual)

        # Traslado

        if tipo_movimiento == "TRASLADO":

            if not aula_destino:

                raise forms.ValidationError(
                    "Para un traslado debe seleccionar " "un aula de destino."
                )

            if aula_actual and aula_actual.pk == aula_destino.pk:

                raise forms.ValidationError(
                    f"El activo ya se encuentra en el aula "
                    f"{aula_actual.codigo}. "
                    f"El aula de destino debe ser diferente "
                    f"al aula actual."
                )

        elif tipo_movimiento == "SALIDA":

            if aula_destino:

                raise forms.ValidationError(
                    "Una salida temporal no debe tener " "un aula de destino."
                )

        elif tipo_movimiento == "BAJA":

            if aula_destino:

                raise forms.ValidationError(
                    "Una baja no debe tener " "un aula de destino."
                )

        elif tipo_movimiento == "REINGRESO":

            if not aula_destino:

                raise forms.ValidationError(
                    "Para un reingreso debe seleccionar " "el aula de origen."
                )

            if aula_actual and aula_destino.pk != aula_actual.pk:

                raise forms.ValidationError(
                    f"El reingreso debe realizarse en el aula " f"{aula_actual.codigo}."
                )

        return cleaned_data

    def save(self, commit=True):

        movimiento = super().save(commit=False)

        valor = self.cleaned_data["activo_seleccionado"]

        tipo_activo, activo_id = valor.split(":")

        modelos = {
            "computador": Computador,
            "componente": ComponenteComputador,
            "equipo": EquipoTecnologico,
            "mobiliario": Mobiliario,
        }

        modelo = modelos[tipo_activo]

        objeto = modelo.objects.get(pk=activo_id)

        # ------------------------------------------------------------
        # CONTENT TYPE Y OBJECT ID
        # ------------------------------------------------------------

        movimiento.content_type = ContentType.objects.get_for_model(modelo)

        movimiento.object_id = objeto.pk

        # ------------------------------------------------------------
        # AULA DE ORIGEN
        # ------------------------------------------------------------

        movimiento.aula_origen = self.obtener_aula_activo(objeto)

        # ------------------------------------------------------------
        # GUARDAR MOVIMIENTO
        # ------------------------------------------------------------

        if commit:

            movimiento.save()

            # ========================================================
            # TRASLADO
            # ========================================================

            if movimiento.tipo == "TRASLADO" and movimiento.aula_destino:

                if tipo_activo == "computador":

                    objeto.aula = movimiento.aula_destino
                    objeto.save(update_fields=["aula"])

                elif tipo_activo == "equipo":

                    objeto.aula = movimiento.aula_destino
                    objeto.save(update_fields=["aula"])

                elif tipo_activo == "mobiliario":

                    objeto.aula = movimiento.aula_destino
                    objeto.save(update_fields=["aula"])

                elif tipo_activo == "componente":

                    objeto.computador.aula = movimiento.aula_destino
                    objeto.computador.save(update_fields=["aula"])

            # ========================================================
            # BAJA
            # ========================================================

            elif movimiento.tipo == "BAJA":

                objeto.estado = "BAJA"

                objeto.save(update_fields=["estado"])

            # ========================================================
            # REINGRESO
            # ========================================================

            elif movimiento.tipo == "REINGRESO":

                if tipo_activo == "mobiliario":

                    objeto.estado = "BUENO"

                else:

                    objeto.estado = "OPERATIVO"

                objeto.save(update_fields=["estado"])

                # ----------------------------------------------------
                # Actualizar ubicación
                # ----------------------------------------------------

                if movimiento.aula_destino:

                    if tipo_activo == "computador":

                        objeto.aula = movimiento.aula_destino
                        objeto.save(update_fields=["aula"])

                    elif tipo_activo == "equipo":

                        objeto.aula = movimiento.aula_destino
                        objeto.save(update_fields=["aula"])

                    elif tipo_activo == "mobiliario":

                        objeto.aula = movimiento.aula_destino
                        objeto.save(update_fields=["aula"])

                    elif tipo_activo == "componente":

                        objeto.computador.aula = movimiento.aula_destino
                        objeto.computador.save(update_fields=["aula"])

        return movimiento


# ====================================================================
# FORMULARIO DE MANTENIMIENTOS
# ====================================================================


class MantenimientoForm(forms.ModelForm):

    TIPO_ACTIVO_CHOICES = [
        ("computador", "Computador"),
        ("componente", "Componente de computador"),
        ("equipo", "Equipo tecnológico"),
        ("mobiliario", "Mobiliario"),
    ]

    tipo_activo = forms.ChoiceField(
        choices=TIPO_ACTIVO_CHOICES,
        label="Tipo de activo",
    )

    activo_seleccionado = forms.ChoiceField(
        choices=[],
        label="Activo",
    )

    class Meta:
        model = Mantenimiento

        fields = [
            "tipo_activo",
            "activo_seleccionado",
            "fecha",
            "tipo",
            "descripcion",
            "responsable",
            "estado_anterior",
            "estado_posterior",
            "observaciones",
        ]
        widgets = {
            "fecha": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["fecha"].input_formats = ["%Y-%m-%dT%H:%M"]

        self.fields["responsable"].queryset = User.objects.filter(
            is_active=True
        ).order_by("first_name", "last_name")
        self.fields["responsable"].label = "Responsable"
        self.fields["responsable"].empty_label = "Seleccione el responsable"

        opciones = []

        for objeto in Computador.objects.all():

            opciones.append(
                (
                    f"computador:{objeto.pk}",
                    f"Computador - " f"{objeto.codigo_inventario}",
                )
            )

        for objeto in ComponenteComputador.objects.all():

            opciones.append(
                (
                    f"componente:{objeto.pk}",
                    f"Componente - {objeto}",
                )
            )

        for objeto in EquipoTecnologico.objects.all():

            opciones.append(
                (
                    f"equipo:{objeto.pk}",
                    f"{objeto.get_tipo_display()} - " f"{objeto.codigo_inventario}",
                )
            )

        for objeto in Mobiliario.objects.all():

            opciones.append(
                (
                    f"mobiliario:{objeto.pk}",
                    f"{objeto.get_tipo_display()} - " f"{objeto.codigo_inventario}",
                )
            )

        self.fields["activo_seleccionado"].choices = opciones

    def save(self, commit=True):

        mantenimiento = super().save(commit=False)

        valor = self.cleaned_data["activo_seleccionado"]

        tipo_activo, activo_id = valor.split(":")

        modelos = {
            "computador": Computador,
            "componente": ComponenteComputador,
            "equipo": EquipoTecnologico,
            "mobiliario": Mobiliario,
        }

        modelo = modelos[tipo_activo]

        objeto = modelo.objects.get(pk=activo_id)

        mantenimiento.content_type = ContentType.objects.get_for_model(modelo)

        mantenimiento.object_id = objeto.pk

        if commit:

            mantenimiento.save()

        return mantenimiento


class ComputadorForm(forms.ModelForm):
    class Meta:
        model = Computador

        fields = [
            "codigo_inventario",
            "aula",
            "marca",
            "modelo",
            "estado",
            "observaciones",
            "activo",
        ]

        widgets = {
            "codigo_inventario": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código de inventario",
                }
            ),
            "aula": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "marca": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Marca",
                }
            ),
            "modelo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Modelo",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observaciones",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class EquipoTecnologicoForm(forms.ModelForm):
    piso = forms.ModelChoiceField(
        queryset=Piso.objects.filter(activo=True),
        required=True,
        label="Piso",
        empty_label="Seleccione un piso",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "id_piso",
            }
        ),
    )

    class Meta:

        model = EquipoTecnologico

        fields = [
            "codigo_inventario",
            "piso",
            "aula",
            "tipo",
            "marca",
            "modelo",
            "serial",
            "estado",
            "observaciones",
            "activo",
        ]

        widgets = {
            "codigo_inventario": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código de inventario",
                }
            ),
            "aula": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "id_aula",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "marca": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Marca",
                }
            ),
            "modelo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Modelo",
                }
            ),
            "serial": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Número de serial",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observaciones",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ============================================================
        # AULA VACÍA INICIALMENTE
        # ============================================================

        self.fields["aula"].queryset = Aula.objects.none()

        # ============================================================
        # SI EL FORMULARIO YA TIENE UN AULA
        # ============================================================

        if self.instance and self.instance.pk:

            if self.instance.aula:

                self.fields["piso"].initial = self.instance.aula.piso

                self.fields["aula"].queryset = Aula.objects.filter(
                    piso=self.instance.aula.piso,
                    activo=True,
                ).order_by("codigo")

        # ============================================================
        # CUANDO EL USUARIO SELECCIONA UN PISO
        # ============================================================

        if "piso" in self.data:

            try:

                piso_id = int(self.data.get("piso"))

                self.fields["aula"].queryset = Aula.objects.filter(
                    piso_id=piso_id,
                    activo=True,
                ).order_by("codigo")

            except (ValueError, TypeError):

                self.fields["aula"].queryset = Aula.objects.none()

    def clean(self):

        cleaned_data = super().clean()

        piso = cleaned_data.get("piso")
        aula = cleaned_data.get("aula")

        if piso and aula:

            if aula.piso_id != piso.id:

                raise forms.ValidationError(
                    "El aula seleccionada no pertenece " "al piso seleccionado."
                )

        return cleaned_data


class PisoForm(forms.ModelForm):

    class Meta:

        model = Piso

        fields = [
            "numero",
            "nombre",
            "activo",
        ]

        widgets = {
            "numero": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Número del piso",
                    "min": "1",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del piso",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class AulaForm(forms.ModelForm):
    class Meta:

        model = Aula

        fields = [
            "piso",
            "codigo",
            "nombre",
            "capacidad",
            "activo",
            "descripcion",
        ]

        widgets = {
            "piso": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código del aula",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del aula",
                }
            ),
            "capacidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Capacidad",
                    "min": "0",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Descripción del aula",
                }
            ),
        }


class PersonalForm(forms.ModelForm):

    ROL_CHOICES = [
        ("Personal", "Personal"),
        ("Administradores", "Administrador"),
    ]

    rol = forms.ChoiceField(
        label="Rol del usuario",
        choices=ROL_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
                "autocomplete": "new-password",
            }
        ),
    )

    password_confirmacion = forms.CharField(
        label="Confirmar contraseña",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirmar contraseña",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombres"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apellidos"}
            ),
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Usuario"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Correo electrónico"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Al editar, conservar el rol actual.
        if self.instance and self.instance.pk:
            grupo = self.instance.groups.filter(
                name__in=["Administradores", "Personal"]
            ).first()

            if grupo:
                self.fields["rol"].initial = grupo.name

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirmacion = cleaned_data.get("password_confirmacion")

        if self.instance and self.instance.pk:
            # La contraseña solo se cambia si se diligencia.
            if password or confirmacion:
                if password != confirmacion:
                    raise forms.ValidationError("Las contraseñas no coinciden.")
        else:
            # Para un usuario nuevo, la contraseña es obligatoria.
            if not password:
                self.add_error("password", "La contraseña es obligatoria.")

            if password != confirmacion:
                raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if password:
            usuario.set_password(password)

        if commit:
            usuario.save()
            self.save_m2m()

            from django.contrib.auth.models import Group

            nombre_rol = self.cleaned_data["rol"]
            grupo, _ = Group.objects.get_or_create(name=nombre_rol)

            usuario.groups.remove(
                *usuario.groups.filter(name__in=["Administradores", "Personal"])
            )
            usuario.groups.add(grupo)

        return usuario


class SoftwareInstaladoForm(forms.ModelForm):
    class Meta:
        model = SoftwareInstalado
        fields = [
            "nombre",
            "version",
            "tipo_licencia",
            "observaciones",
            "activo",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej. AutoCAD, SPSS, Geo5",
                }
            ),
            "version": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej. 2025, 31.0",
                }
            ),
            "tipo_licencia": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "activo": forms.CheckboxInput(),
        }
