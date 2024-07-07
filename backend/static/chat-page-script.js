document.addEventListener('DOMContentLoaded', function () {
    const menuButton = document.getElementById('menu-button');
    const sidebar = document.getElementById('sidebar');
    const menuItems = document.getElementById('menu-items');
    const menuItem = document.querySelectorAll('.menu-item');
    const userProfile = document.getElementById('user-profile');
    const dropdownContent = document.getElementById('dropdown-content');
    const logoutButton = document.getElementById('logout-button');
    const popup = document.getElementById('popup');
    const cancelButton = document.getElementById('cancel-button');
    const confirmButton = document.getElementById('confirm-button');
    const chatId = document.getElementById('chat-id').value;

    menuButton.addEventListener('click', function () {
        sidebar.classList.toggle('closed');
        menuItems.classList.toggle('closed');
        userProfile.classList.toggle('closed');
        menuButton.classList.toggle('closed');
    });

    menuItem.forEach(item => {
        if (item.getAttribute('data-chat-id') === chatId) {
            item.classList.add('selected');
            item.nextElementSibling.classList.add('visible');
        }
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

    const profilePic = sender === 'user' ? '/static/img/male.PNG' : '/static/img/dog.PNG';

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

    logToServer("Message appended to chat: " + sender + ": " + message);  // Debug output
}



document.getElementById('send-button').addEventListener('click', sendMessage);

async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    const chatId = document.getElementById('chat-id').value;

    if (message) {
        appendMessage('user', message);
        userInput.value = '';

        // Await the bot's response
        const botMessage = await getBotResponse(message, chatId);
        logToServer("Bot response: " + JSON.stringify(botMessage));
        if (botMessage.newChatId) {
            logToServer("Redirecting to new chat page: " + botMessage.newChatId);  // Debug output
            window.location.href = `/chatpage/${botMessage.newChatId}`;
        } else {
            logToServer("Appending bot response to chat: " + botMessage.response);  // Debug output
            appendMessage('bot', botMessage.response);
        }
    }
}

async function getBotResponse(message, chatId) {
    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message, chatId: chatId }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        logToServer("Response data: " + JSON.stringify(data));  // Debug output
        if (data.error) {
            logToServer("Error in response data: " + data.error);
            throw new Error(data.error);
        }

        if (data.response === undefined || data.chatId === undefined) {
            logToServer("Unexpected response structure: " + JSON.stringify(data));
            throw new Error("Unexpected response structure");
        }

        return {
            response: data.response,
            newChatId: data.chatId && data.chatId !== chatId ? data.chatId : null,
        };
    } catch (error) {
        logToServer('Error fetching bot response: ' + error);  // Debug output
        return 'Sorry, something went wrong. Please try again.';
    }
    
}

function logToServer(message) {
    fetch('/log', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    }).catch(error => console.error('Error logging message:', error));
}