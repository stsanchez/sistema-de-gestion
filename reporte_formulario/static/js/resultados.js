// Cargar lista de usuarios del archivo de texto
fetch('static/usuarios_ad.txt')
.then(response => response.text())
.then(data => {
    const usuarios = data.split('\n');
    const inputUsuario = document.getElementById('usuario');
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
// Por ejemplo:
// fetch('/backend', {
//     method: 'POST',
//     body: JSON.stringify({ usuario: usuarioSeleccionado }),
//     headers: {
//         'Content-Type': 'application/json'
//     }
// })
// .then(response => response.json())
// .then(data => console.log(data))
// .catch(error => console.error('Error:', error));
});