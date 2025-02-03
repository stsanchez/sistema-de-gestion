
// Variable global para almacenar la lista de resultados
    let usuarios = [];
    // Variable para el índice del usuario seleccionado
    let indiceSeleccionado = -1;

    const dispositivoSelect = document.getElementById('dispositivo');
    const telefonoField = document.getElementById('nro_telefono');
    const leasingCheckboxDiv = document.getElementById('leasing-checkbox');
    const modeloTelefonoField = document.getElementById('modelo_telefono');
    
    dispositivoSelect.addEventListener('change', function() {
      if (this.value === 'Telefono') {
        telefonoField.style.display = 'block';
        modeloTelefonoField.style.display = 'block';
        console.log('Campos de teléfono y modelo mostrados');
      }
      if (this.value === 'Laptop nueva'|| this.value === 'Laptop uma') {
        leasingCheckboxDiv.style.display = 'block';  // Muestra el checkbox
    } else {
        telefonoField.style.display = 'none';
        modeloTelefonoField.style.display = 'none';
      }
    });

    // Obtener la fecha actual
var today = new Date().toISOString().split('T')[0];
// Asignar la fecha actual al campo de fecha
document.getElementById("fecha").value = today;

// Cargar lista de usuarios del archivo de texto
fetch('static/usuarios_ad.txt')
.then(response => response.text())
.then(data => {
    const usuarios = data.split('\n');
    const inputUsuario = document.getElementById('asignado');
    const sugerenciasDiv = document.getElementById('sugerencias');

    inputUsuario.addEventListener('input', function() {
        const valorInput = this.value.trim().toLowerCase();
        sugerenciasDiv.innerHTML = '';
        const coincidencias = usuarios.filter(usuario => usuario.toLowerCase().startsWith(valorInput));
        coincidencias.forEach(coincidencia => {
            const suggestion = document.createElement('div');
            suggestion.classList.add('sugerencia');
            suggestion.textContent = coincidencia;
            suggestion.addEventListener('click', function() {
                inputUsuario.value = coincidencia;
                sugerenciasDiv.innerHTML = '';
            });
            sugerenciasDiv.appendChild(suggestion);
        });
    });

    inputUsuario.addEventListener('keydown', function(event) {
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
                inputUsuario.value = sugerencias[index].textContent;
                sugerenciasDiv.innerHTML = '';
            }
        }
    });

    inputUsuario.addEventListener('blur', function() {
        setTimeout(() => {
            sugerenciasDiv.innerHTML = '';
        }, 200);
    });
})
.catch(error => console.error('Error al cargar el archivo:', error));

// Envío del formulario al backend
document.getElementById('formulario').addEventListener('submit', function(event) {
event.preventDefault(); // Evitar que el formulario se envíe automáticamente
const usuarioSeleccionado = document.getElementById('usuario').value;
// Aquí puedes enviar el usuarioSeleccionado al backend usando fetch() u otro método
console.log('Usuario seleccionado:', usuarioSeleccionado);

});


