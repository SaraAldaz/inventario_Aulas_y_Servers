from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from infraestructura.models import Aula


class Computador(models.Model):
    codigo_inventario = models.CharField(max_length=50, unique=True)

    aula = models.ForeignKey(
        Aula, on_delete=models.PROTECT, related_name="computadores"
    )

    marca = models.CharField(max_length=100, blank=True)

    modelo = models.CharField(max_length=100, blank=True)

    estado = models.CharField(
        max_length=30,
        choices=[
            ("OPERATIVO", "Operativo"),
            ("MANTENIMIENTO", "En mantenimiento"),
            ("DANADO", "Dañado"),
            ("BAJA", "De baja"),
        ],
        default="OPERATIVO",
    )

    observaciones = models.TextField(blank=True)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["codigo_inventario"]
        verbose_name = "Computador"
        verbose_name_plural = "Computadores"

    def __str__(self):
        return self.codigo_inventario


class ComponenteComputador(models.Model):
    TIPOS_COMPONENTE = [
        ("CPU", "CPU"),
        ("PANTALLA", "Pantalla"),
        ("TECLADO", "Teclado"),
        ("MOUSE", "Mouse"),
    ]

    computador = models.ForeignKey(
        Computador, on_delete=models.CASCADE, related_name="componentes"
    )

    tipo = models.CharField(max_length=20, choices=TIPOS_COMPONENTE)

    marca = models.CharField(max_length=100, blank=True)

    modelo = models.CharField(max_length=100, blank=True)

    serial = models.CharField(max_length=100, blank=True)

    estado = models.CharField(
        max_length=30,
        choices=[
            ("OPERATIVO", "Operativo"),
            ("MANTENIMIENTO", "En mantenimiento"),
            ("DANADO", "Dañado"),
            ("BAJA", "De baja"),
        ],
        default="OPERATIVO",
    )

    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["computador__codigo_inventario", "tipo"]
        verbose_name = "Componente de computador"
        verbose_name_plural = "Componentes de computadores"

        constraints = [
            models.UniqueConstraint(
                fields=["computador", "tipo"], name="un_componente_por_tipo"
            )
        ]

    def __str__(self):
        return f"{self.computador.codigo_inventario} - {self.get_tipo_display()}"


class EquipoTecnologico(models.Model):
    TIPOS_EQUIPO = [
        ("VIDEO_BEAM", "Video Beam"),
        ("BARRA_SONIDO", "Barra de sonido"),
        ("AIRE_ACONDICIONADO", "Aire acondicionado"),
        ("TELON_PROYECCION", "Telón de proyección"),
    ]

    codigo_inventario = models.CharField(max_length=50, unique=True)

    aula = models.ForeignKey(
        Aula, on_delete=models.PROTECT, related_name="equipos_tecnologicos"
    )

    tipo = models.CharField(max_length=30, choices=TIPOS_EQUIPO)

    marca = models.CharField(max_length=100, blank=True)

    modelo = models.CharField(max_length=100, blank=True)

    serial = models.CharField(max_length=100, blank=True)

    estado = models.CharField(
        max_length=30,
        choices=[
            ("OPERATIVO", "Operativo"),
            ("MANTENIMIENTO", "En mantenimiento"),
            ("DANADO", "Dañado"),
            ("BAJA", "De baja"),
        ],
        default="OPERATIVO",
    )

    observaciones = models.TextField(blank=True)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tipo", "codigo_inventario"]
        verbose_name = "Equipo tecnológico"
        verbose_name_plural = "Equipos tecnológicos"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.codigo_inventario}"


class Mobiliario(models.Model):
    TIPOS_MOBILIARIO = [
        ("MESA", "Mesa"),
        ("SILLA", "Silla"),
    ]

    codigo_inventario = models.CharField(max_length=50, unique=True)

    aula = models.ForeignKey(Aula, on_delete=models.PROTECT, related_name="mobiliario")

    tipo = models.CharField(max_length=20, choices=TIPOS_MOBILIARIO)

    estado = models.CharField(
        max_length=30,
        choices=[
            ("BUENO", "Bueno"),
            ("REGULAR", "Regular"),
            ("DANADO", "Dañado"),
            ("BAJA", "De baja"),
        ],
        default="BUENO",
    )

    observaciones = models.TextField(blank=True)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tipo", "codigo_inventario"]
        verbose_name = "Elemento de mobiliario"
        verbose_name_plural = "Elementos de mobiliario"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.codigo_inventario}"


class MovimientoActivo(models.Model):

    TIPOS_MOVIMIENTO = [
        ("TRASLADO", "Traslado"),
        ("SALIDA", "Salida temporal"),
        ("BAJA", "Baja"),
        ("REINGRESO", "Reingreso"),
    ]

    # Identifica qué tipo de activo estamos moviendo
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)

    # Identifica el ID del activo
    object_id = models.PositiveIntegerField()

    # Une content_type + object_id
    activo = GenericForeignKey("content_type", "object_id")

    fecha = models.DateTimeField()

    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)

    aula_origen = models.ForeignKey(
        Aula,
        on_delete=models.PROTECT,
        related_name="movimientos_origen",
        null=True,
        blank=True,
    )

    aula_destino = models.ForeignKey(
        Aula,
        on_delete=models.PROTECT,
        related_name="movimientos_destino",
        null=True,
        blank=True,
    )

    motivo = models.CharField(max_length=200)

    observaciones = models.TextField(blank=True)

    responsable = models.ForeignKey(
        "auth.User", on_delete=models.PROTECT, related_name="movimientos_realizados"
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)


class Meta:
    ordering = ["-fecha"]
    verbose_name = "Movimiento de activo"
    verbose_name_plural = "Movimientos de activos"


def __str__(self):
    return f"{self.get_tipo_display()} - {self.activo}"


def obtener_aula_actual(self):

    activo = self.activo

    if isinstance(activo, ComponenteComputador):
        return activo.computador.aula

    if isinstance(activo, Computador):
        return activo.aula

    if isinstance(activo, EquipoTecnologico):
        return activo.aula

    if isinstance(activo, Mobiliario):
        return activo.aula

    return None


class Mantenimiento(models.Model):

    TIPOS_MANTENIMIENTO = [
        ("PREVENTIVO", "Preventivo"),
        ("CORRECTIVO", "Correctivo"),
        ("LIMPIEZA", "Limpieza"),
        ("DIAGNOSTICO", "Diagnóstico"),
        ("ACTUALIZACION", "Actualización"),
        ("CAMBIO_COMPONENTE", "Cambio de componente"),
        ("OTRO", "Otro"),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)

    object_id = models.PositiveIntegerField()

    activo = GenericForeignKey("content_type", "object_id")

    fecha = models.DateTimeField()

    tipo = models.CharField(max_length=30, choices=TIPOS_MANTENIMIENTO)

    descripcion = models.TextField()

    responsable = models.ForeignKey(
        "auth.User", on_delete=models.PROTECT, related_name="mantenimientos_realizados"
    )
    ESTADOS_ACTIVO = [
        ("OPERATIVO", "Operativo"),
        ("MANTENIMIENTO", "En mantenimiento"),
        ("DANADO", "Dañado"),
        ("BAJA", "De baja"),
    ]

    estado_anterior = models.CharField(max_length=30, choices=ESTADOS_ACTIVO)

    estado_posterior = models.CharField(max_length=30, choices=ESTADOS_ACTIVO)

    observaciones = models.TextField(blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.activo}"


class SoftwareInstalado(models.Model):
    aula = models.ForeignKey(
        "infraestructura.Aula",
        on_delete=models.PROTECT,
        related_name="software_instalado",
    )

    nombre = models.CharField(max_length=150)
    version = models.CharField(max_length=80, blank=True)

    tipo_licencia = models.CharField(
        max_length=30,
        choices=[
            ("LIBRE", "Libre o gratuito"),
            ("INSTITUCIONAL", "Licencia institucional"),
            ("COMERCIAL", "Licencia comercial"),
            ("ACADEMICA", "Licencia académica"),
            ("OTRO", "Otro"),
        ],
        default="INSTITUCIONAL",
    )

    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Software instalado"
        verbose_name_plural = "Software instalado"
        constraints = [
            models.UniqueConstraint(
                fields=["aula", "nombre"],
                name="unique_software_por_aula",
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.aula}"
