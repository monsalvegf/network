function editPost(postId) {
    let contentP = document.getElementById('post-content-' + postId);
    let editForm = document.getElementById('edit-form-' + postId);
    let editButton = document.getElementById('edit-button-' + postId);  // Reference the Edit button

    contentP.style.display = 'none';
    editForm.style.display = 'block';
    editButton.style.display = 'none';  // Hide the Edit button when editing
}

function savePost(postId) {
    let editedContent = document.getElementById('edit-content-' + postId).value;
    fetch(`/save_post/${postId}`, {
        method: 'POST',
        body: JSON.stringify({
            content: editedContent
        }),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        let contentP = document.getElementById('post-content-' + postId);
        let editForm = document.getElementById('edit-form-' + postId);
        let editButton = document.getElementById('edit-button-' + postId);  // Reference the Edit button

        contentP.innerText = editedContent;
        contentP.style.display = 'block';
        editForm.style.display = 'none';
        editButton.style.display = 'inline';  // Show the Edit button again once editing is saved
    })
    .catch(error => console.error('Error:', error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');  // Divide el string de cookies en un array
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();  // Elimina espacios en blanco antes y después del contenido del cookie
            // Comprueba si el nombre del cookie es igual al nombre buscado
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;  // Sale del bucle una vez que encuentra el cookie
            }
        }
    }
    return cookieValue;
}
