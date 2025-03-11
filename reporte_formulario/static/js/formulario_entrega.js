// Variables globales
let usuarios = [];
let indiceSeleccionado = -1;

// Elementos del DOM
const dispositivoSelect = document.getElementById('dispositivo');
const telefonoField = document.getElementById('nro_telefono');
//const leasingCheckboxDiv = document.getElementById('leasing-checkbox');
const modeloTelefonoField = document.getElementById('modelo'); // Cambiado a 'modelo' para no confundir
const inputAsignado = document.getElementById('asignado');
const sugerenciasAsignado = document.getElementById('sugerencias');
const etiquetaInput = document.getElementById('etiqueta');
const mensajeError = document.createElement('div');
mensajeError.style.color = 'red';
let formValido = true; // Variable para controlar la validez del formulario

// Esperar a que el DOM esté completamente cargado para insertar el mensaje de error
document.addEventListener('DOMContentLoaded', function () {
    etiquetaInput.parentNode.insertBefore(mensajeError, etiquetaInput.nextSibling);
});

// Funcionalidades iniciales (mostrar/ocultar campos)
/*dispositivoSelect.addEventListener('change', function () {
    if (this.value === 'Telefono') {
        telefonoField.style.display = 'block';
        modeloTelefonoField.style.display = 'block';
    } else {
        telefonoField.style.display = 'none';
        modeloTelefonoField.style.display = 'none';
    }

    if (this.value === 'Laptop nueva' || this.value === 'Laptop uma') {
        leasingCheckboxDiv.style.display = 'block';
    } else {
        leasingCheckboxDiv.style.display = 'none';
    }
});*/

// Fecha actual
const today = new Date().toISOString().split('T')[0];
document.getElementById("fecha").value = today;

// Carga de usuarios y sugerencias PARA EL CAMPO "ASIGNADO"
fetch('static/usuarios_ad.txt')
    .then(response => response.text())
    .then(data => {
        usuarios = data.split('\n');

        inputAsignado.addEventListener('input', function () {
            const valorInput = this.value.trim().toLowerCase();
            sugerenciasAsignado.innerHTML = ''; // Limpia sugerencias anteriores
            const coincidencias = usuarios.filter(usuario => usuario.toLowerCase().startsWith(valorInput));

            coincidencias.forEach(coincidencia => {
                const suggestion = document.createElement('div');
                suggestion.classList.add('sugerencia');
                suggestion.textContent = coincidencia;
                suggestion.addEventListener('click', function () {
                    inputAsignado.value = coincidencia;
                    sugerenciasAsignado.innerHTML = '';
                });
                sugerenciasAsignado.appendChild(suggestion);
            });
        });

        inputAsignado.addEventListener('keydown', function (event) {
            const sugerencias = Array.from(document.querySelectorAll('.sugerencia'));
            let index = sugerencias.findIndex(sugerencia => sugerencia.classList.contains('focus'));

            if (event.key === 'ArrowDown') {
                event.preventDefault();
                index = (index + 1) % sugerencias.length;
                sugerencias[index].classList.add('focus');
                sugerencias[(index + sugerencias.length - 1) % sugerencias.length].classList.remove('focus');
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                index = (index - 1 + sugerencias.length) % sugerencias.length;
                sugerencias[index].classList.add('focus');
                sugerencias[(index + 1) % sugerencias.length].classList.remove('focus');
            } else if (event.key === 'Enter') {
                if (index !== -1) {
                    event.preventDefault();
                    inputAsignado.value = sugerencias[index].textContent;
                    sugerenciasAsignado.innerHTML = '';
                }
            }
        });

        inputAsignado.addEventListener('blur', function () {
            setTimeout(() => {
                sugerenciasAsignado.innerHTML = '';
            }, 200);
        });
    })
    .catch(error => console.error('Error al cargar el archivo:', error));


// Validación de etiqueta y envío de formulario
etiquetaInput.addEventListener('input', function () {
    const etiqueta = this.value;
    if (etiqueta.trim() !== '') {
        fetch('/validar_etiqueta', {
            method: 'POST',
            body: new FormData(this.form) // Usar this.form para enviar todos los datos
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error) }); // Lanza el error del backend
                }
                return response.json(); // Devuelve la respuesta JSON para el siguiente .then
            })
            .then(data => { // Ahora data es el objeto JSON
                if (data.existe) {
                    mensajeError.textContent = `Esta etiqueta ya está asignada a ${data.asignado}.`;
                    etiquetaInput.classList.add('is-invalid');
                    formValido = false; // El formulario no es válido
                } else {
                    mensajeError.textContent = '';
                    etiquetaInput.classList.remove('is-invalid');
                    formValido = true; // El formulario es válido
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mensajeError.textContent = 'Error al validar la etiqueta.';
                etiquetaInput.classList.add('is-invalid');
                formValido = false; // El formulario no es válido
            });
    } else {
        mensajeError.textContent = '';
        etiquetaInput.classList.remove('is-invalid');
        formValido = true; // El formulario es válido
    }
});


document.getElementById('formulario').addEventListener('submit', function (event) {
    event.preventDefault();

    if (!formValido) { // Si el formulario no es válido
        alert("Por favor, corrige los errores en el formulario.");
        return; // No enviar el formulario
    }

    fetch('/generar_reporte', {
        method: 'POST',
        body: new FormData(this)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error) });
            }
            return response.blob();
        })
        .then(blob => {
            // ... (código para mostrar el PDF)
        })
        .catch(error => {
            alert(error.message);
        });
});