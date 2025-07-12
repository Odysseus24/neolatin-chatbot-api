document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const clearChatBtn = document.getElementById('clear-chat-btn');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        appendMessage(message, 'user');
        messageInput.value = '';

        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `message=${encodeURIComponent(message)}`,
        });

        const data = await response.json();
        appendMessage(data.answer || data.error, 'bot');
    });

    clearChatBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Clear the UI
            clearChatWindow();
            
            // Clear the backend memory
            await fetch('/clear_chat', {
                method: 'POST',
            });
        }
    });

    function clearChatWindow() {
        // Remove all messages except the initial message
        const messages = chatWindow.querySelectorAll('.message:not(#initial-message)');
        messages.forEach(message => message.remove());
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        appendMessage(message, 'user');
        messageInput.value = '';

        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `message=${encodeURIComponent(message)}`,
        });

        const data = await response.json();
        appendMessage(data.answer || data.error, 'bot');
    });

    function appendMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);

        const avatar = document.createElement('div');
        avatar.classList.add('message-avatar');
        avatar.textContent = sender === 'user' ? 'U' : 'J';

        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble');
        
        if (sender === 'bot') {
            // Convert markdown formatting to HTML for bot messages
            const formattedMessage = formatMarkdown(message);
            bubble.innerHTML = formattedMessage;
        } else {
            // Keep user messages as plain text
            bubble.textContent = message;
        }

        messageElement.appendChild(avatar);
        messageElement.appendChild(bubble);
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function formatMarkdown(text) {
        return text
            // Bold text: **text** or __text__
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/__(.*?)__/g, '<strong>$1</strong>')
            // Italic text: *text* or _text_
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/_(.*?)_/g, '<em>$1</em>')
            // Convert bullet points
            .replace(/^\* (.+)$/gm, '<li>$1</li>')
            // Wrap consecutive list items in <ul>
            .replace(/(<li>.*<\/li>)/gs, function(match) {
                return '<ul>' + match + '</ul>';
            })
            // Convert line breaks to <br>
            .replace(/\n/g, '<br>');
    }
});
