document.addEventListener("DOMContentLoaded", function () {

    const tipoActivo = document.getElementById("id_tipo_activo");
    const activoSeleccionado = document.getElementById("id_activo_seleccionado");
    const aulaActual = document.getElementById("id_aula_origen_mostrada");

    if (!tipoActivo || !activoSeleccionado || !aulaActual) {
        console.error(
            "No se encontraron los campos necesarios del formulario."
        );
        return;
    }

    function limpiarAula() {
        aulaActual.value = "";
    }

    function consultarAula() {

        const valor = activoSeleccionado.value;

        if (!valor) {
            limpiarAula();
            return;
        }

        const partes = valor.split(":");

        if (partes.length !== 2) {
            limpiarAula();
            return;
        }

        const tipo = partes[0];
        const activoId = partes[1];

        limpiarAula();

        aulaActual.value = "Consultando...";

        fetch(
            `/api/aula-activo/${tipo}/${activoId}/`
        )
            .then(response => {

                if (!response.ok) {
                    throw new Error(
                        "No fue posible consultar el aula."
                    );
                }

                return response.json();
            })
            .then(data => {

                if (data.aula) {

                    aulaActual.value = data.aula;

                } else {

                    aulaActual.value =
                        "Sin aula asignada";
                }
            })
            .catch(error => {

                console.error(
                    "Error consultando el aula:",
                    error
                );

                aulaActual.value =
                    "Error al consultar";
            });
    }

    // Cuando cambia el tipo de activo
    tipoActivo.addEventListener(
        "change",
        function () {

            limpiarAula();

        }
    );

    // Cuando cambia el activo
    activoSeleccionado.addEventListener(
        "change",
        function () {

            consultarAula();

        }
    );

    // Si el formulario ya tiene un activo seleccionado
    if (activoSeleccionado.value) {

        consultarAula();

    }

});