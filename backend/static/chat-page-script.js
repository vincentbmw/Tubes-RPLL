document.addEventListener('DOMContentLoaded', function () {
    const menuButton = document.getElementById('menu-button');
    const sidebar = document.getElementById('sidebar');
    const menuItems = document.getElementById('menu-items');
    const userProfile = document.getElementById('user-profile');
    const dropdownContent = document.getElementById('dropdown-content');
    const logoutButton = document.getElementById('logout-button');
    const popup = document.getElementById('popup');
    const cancelButton = document.getElementById('cancel-button');
    const confirmButton = document.getElementById('confirm-button');

    menuButton.addEventListener('click', function () {
        sidebar.classList.toggle('closed');
        menuItems.classList.toggle('closed');
        userProfile.classList.toggle('closed');
        menuButton.classList.toggle('closed');
    });

    userProfile.addEventListener('click', function () {
        userProfile.classList.toggle('show');
    });

    logoutButton.addEventListener('click', function () {
        popup.style.display = 'flex';
    });

    cancelButton.addEventListener('click', function () {
        popup.style.display = 'none';
    });

    confirmButton.addEventListener('click', function () {
        // Add your logout logic here
        alert('Logged out!');
        popup.style.display = 'none';
    });

});

function appendMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    const profilePic = sender === 'user' ? 'img/male.PNG' : 'img/dog.PNG';

    if (sender === 'bot') {
        messageElement.innerHTML = `
            <img src="${profilePic}" alt="${sender}">
            <div class="content">${message}</div>
        `;
    } else {
        messageElement.innerHTML = `
            <div class="content">${message}</div>
            <img src="${profilePic}" alt="${sender}">
        `;
    }

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}



document.getElementById('send-button').addEventListener('click', sendMessage);

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (message) {
        appendMessage('user', message);
        userInput.value = '';

        // Simulate bot response (replace with actual AJAX/WebSocket call)
        setTimeout(() => {
            const botMessage = getBotResponse(message);
            appendMessage('bot', botMessage);
        }, 1000);
    }
}

function getBotResponse(message) {

    return "This is a bot response.";
}