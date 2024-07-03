document.addEventListener('DOMContentLoaded', function () {
    const menuButton = document.getElementById('menu-button');
    const sidebar = document.getElementById('sidebar');
    const menuItem = document.getElementById('menu-items')
    const userProfile = document.getElementById('user-profile')
    const dropdownContent = document.getElementById('dropdown-content')

    menuButton.addEventListener('click', function () {
        sidebar.classList.toggle('closed');
        menuItem.classList.toggle('closed');
        userProfile.classList.toggle('closed');
        menuButton.classList.toggle('closed');
    });

    userProfile.addEventListener('click', function () {
        userProfile.classList.toggle('show');
    });
});

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

function appendMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    const profilePic = sender === 'user' ? 'D:\\kuliah\\SP2024\\RPLL\\tubes\\Tubes-RPLL\\Tubes-RPLL\\frontend\\img\\male.png' : 'D:\\kuliah\\SP2024\\RPLL\\tubes\\Tubes-RPLL\\Tubes-RPLL\\frontend\\img\\dog.png';

    if (sender == 'bot') {
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

function getBotResponse(message) {
    // Placeholder for actual bot response logic
    return "This is a bot response.";
}
