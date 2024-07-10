document.addEventListener('DOMContentLoaded', function () {
    const trashIcon = document.getElementById('trash-icon');
    const popupDelete = document.getElementById('popup-delete');
    const cancelDeleteButton = document.getElementById('cancel-delete-button');
    const confirmDeleteButton = document.querySelector('.confirm-delete-button');

    if (!trashIcon.disabled) {
        trashIcon.addEventListener('click', function () {
            popupDelete.style.display = 'flex';
        });
    }


    /*
    trashIcon.addEventListener('click', function () {
        popupDelete.style.display = 'flex';
    });
    */
   
    cancelDeleteButton.addEventListener('click', function () {
        popupDelete.style.display = 'none';
    });

    confirmDeleteButton.addEventListener('click', async function () {
        const chatId = this.getAttribute('data-chat-id');
        try {
            const response = await fetch(`/delete_chats/${chatId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log(data.message);
                window.location.href = '/chatpage';
            } else {
                const errorData = await response.json();
                console.error(errorData.error);
            }
        } catch (error) {
            console.error('Error deleting chat:', error);
        }

        popupDelete.style.display = 'none';
    });
});