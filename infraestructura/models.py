from django.db import models


class Piso(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['numero']
        verbose_name = 'Piso'
        verbose_name_plural = 'Pisos'

    def __str__(self):
        if self.nombre:
            return f'Piso {self.numero} - {self.nombre}'
        return f'Piso {self.numero}'


class Aula(models.Model):
    piso = models.ForeignKey(
        Piso,
        on_delete=models.PROTECT,
        related_name='aulas'
    )

    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['piso__numero', 'codigo']
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        constraints = [
            models.UniqueConstraint(
                fields=['piso', 'codigo'],
                name='unique_aula_por_piso'
            )
        ]

    def __str__(self):
        return f'Aula {self.codigo}'