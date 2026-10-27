
document.addEventListener("DOMContentLoaded", function () {
    const tipoSelect = document.getElementById("id_tipo_activo");
    const activoSelect = document.getElementById("id_activo_seleccionado");

    if (!tipoSelect || !activoSelect || typeof TomSelect === "undefined") {
        console.error("No se encontró Tom Select o los campos del formulario.");
        return;
    }

    const opcionesOriginales = Array.from(activoSelect.options).map(opcion => ({
        value: opcion.value,
        text: opcion.text
    }));

    const buscadorActivo = new TomSelect(activoSelect, {
        placeholder: "Seleccione o escriba para buscar un activo...",
        searchField: ["text"],
        create: false,
        allowEmptyOption: true,
        maxOptions: null,
        closeAfterSelect: true
    });

    function filtrarActivos() {
        const tipo = tipoSelect.value;
        const valorAnterior = buscadorActivo.getValue();

        buscadorActivo.clear(true);
        buscadorActivo.clearOptions();

        opcionesOriginales.forEach(opcion => {
            if (!opcion.value) return;

            const tipoOpcion = opcion.value.split(":")[0];

            if (tipoOpcion === tipo) {
                buscadorActivo.addOption({
                    value: opcion.value,
                    text: opcion.text
                });
            }
        });

        buscadorActivo.refreshOptions(false);

        if (valorAnterior && valorAnterior.startsWith(tipo + ":")) {
            buscadorActivo.setValue(valorAnterior, true);
        }

        if (tipo) {
            buscadorActivo.enable();
        } else {
            buscadorActivo.clear(true);
            buscadorActivo.disable();
        }
    }

    tipoSelect.addEventListener("change", filtrarActivos);

    filtrarActivos();
});
