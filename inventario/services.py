from .models import (
    Computador,
    ComponenteComputador,
    EquipoTecnologico,
    Mobiliario,
)


def actualizar_ubicacion(activo, aula_destino):
    """
    Actualiza la ubicación del activo cuando corresponde.
    """

    if isinstance(activo, Computador):
        activo.aula = aula_destino
        activo.save(update_fields=['aula'])

    elif isinstance(activo, EquipoTecnologico):
        activo.aula = aula_destino
        activo.save(update_fields=['aula'])

    elif isinstance(activo, Mobiliario):
        activo.aula = aula_destino
        activo.save(update_fields=['aula'])

    elif isinstance(activo, ComponenteComputador):
        # Los componentes pertenecen al computador.
        # Su ubicación se obtiene a través del computador.
        if aula_destino:
            activo.computador.aula = aula_destino
            activo.computador.save(update_fields=['aula'])

def actualizar_estado(activo, nuevo_estado):
    """
    Actualiza el estado del activo.
    """

    if isinstance(activo, Computador):
        activo.estado = nuevo_estado
        activo.save(update_fields=['estado'])

    elif isinstance(activo, ComponenteComputador):
        activo.estado = nuevo_estado
        activo.save(update_fields=['estado'])

    elif isinstance(activo, EquipoTecnologico):
        activo.estado = nuevo_estado
        activo.save(update_fields=['estado'])

    elif isinstance(activo, Mobiliario):
        activo.estado = nuevo_estado
        activo.save(update_fields=['estado'])