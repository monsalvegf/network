
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document is ready and event listeners are being set up.');

    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            console.log('Edit button clicked for post:', postId);
            editPost(postId);
        });
    });
    
    // Guardar cambios del post editado
    document.querySelectorAll('.save-button').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            savePost(postId);
        });
    });

    // Toggle like
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            toggleLike(postId, event);
        });
    });
});

function editPost(postId) {
    let contentP = document.getElementById('post-content-' + postId);
    let editForm = document.getElementById('edit-form-' + postId);
    let editButton = document.getElementById('edit-button-' + postId);

    contentP.style.display = 'none';
    editForm.style.display = 'block';
    editButton.style.display = 'none';
}


function savePost(postId) {
    let editedContent = document.getElementById('edit-content-' + postId).value;
    fetch(`/save_post/${postId}/`, {
        method: 'POST',
        body: JSON.stringify({
            content: editedContent
        }),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP status ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        let contentP = document.getElementById('post-content-' + postId);
        let editForm = document.getElementById('edit-form-' + postId);
        let editButton = document.getElementById('edit-button-' + postId);

        contentP.innerText = editedContent;
        contentP.style.display = 'block';
        editForm.style.display = 'none';
        editButton.style.display = 'inline';
    })
    .catch(error => console.error('Error:', error));
}

// Resto de funciones (getCookie, toggleLike)



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleLike(postId, event) {
    const button = event.target;
    if (!button) {
        console.error('Error: No button found');
        return;  // Salir de la función si no se encuentra el botón
    }
    const liked = button.getAttribute('data-liked') === 'true';
    const url = `/toggle_like/${postId}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Asegurar que el CSRF token es incluido
        },
        body: JSON.stringify({ liked: !liked })  // Invertir el estado de 'liked'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP status ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Asegurar que la respuesta contiene los datos esperados
        if (data.hasOwnProperty('liked') && data.hasOwnProperty('likes_count')) {
            button.setAttribute('data-liked', data.liked ? 'true' : 'false');
            button.classList.toggle('btn-success', data.liked);
            button.classList.toggle('btn-outline-secondary', !data.liked);
            document.getElementById(`like-count-${postId}`).innerText = `${data.likes_count} likes`;
        } else {
            throw new Error('Invalid response data');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while toggling the like status.');  // Opcional: notificar al usuario
    });
}


