document.addEventListener("DOMContentLoaded", function () {

    const pisoSelect = document.getElementById("id_piso");
    const aulaSelect = document.getElementById("id_aula");

    if (!pisoSelect || !aulaSelect) {
        return;
    }

    function cargarAulas(pisoId, aulaSeleccionada = null) {

        aulaSelect.innerHTML = "";

        const opcionInicial = document.createElement("option");

        opcionInicial.value = "";
        opcionInicial.textContent = "Seleccione un aula";

        aulaSelect.appendChild(opcionInicial);

        if (!pisoId) {
            aulaSelect.disabled = true;
            return;
        }

        aulaSelect.disabled = true;

        fetch(
            `/api/aulas-por-piso/${pisoId}/`
        )
            .then(response => {

                if (!response.ok) {
                    throw new Error(
                        "No se pudieron cargar las aulas."
                    );
                }

                return response.json();
            })
            .then(data => {

                data.aulas.forEach(aula => {

                    const opcion =
                        document.createElement("option");

                    opcion.value = aula.id;

                    opcion.textContent =
                        `${aula.codigo} - ${aula.nombre}`;

                    if (
                        aulaSeleccionada &&
                        String(aula.id) ===
                        String(aulaSeleccionada)
                    ) {
                        opcion.selected = true;
                    }

                    aulaSelect.appendChild(opcion);
                });

                aulaSelect.disabled = false;
            })
            .catch(error => {

                console.error(error);

                aulaSelect.innerHTML = "";

                const opcionError =
                    document.createElement("option");

                opcionError.value = "";

                opcionError.textContent =
                    "Error al cargar las aulas";

                aulaSelect.appendChild(opcionError);

                aulaSelect.disabled = true;
            });
    }


    pisoSelect.addEventListener(
        "change",
        function () {

            cargarAulas(
                this.value
            );

        }
    );


    // ============================================================
    // EDICIÓN
    // ============================================================

    const pisoInicial =
        pisoSelect.value;

    const aulaInicial =
        aulaSelect.value;

    if (pisoInicial) {

        cargarAulas(
            pisoInicial,
            aulaInicial
        );

    } else {

        aulaSelect.disabled = true;

    }

});
