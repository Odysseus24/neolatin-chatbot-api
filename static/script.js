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
        // First, escape any existing HTML to prevent injection
        text = text.replace(/&/g, '&amp;')
                  .replace(/</g, '&lt;')
                  .replace(/>/g, '&gt;');
        
        // Process in specific order to avoid conflicts
        
        // 1. Handle code blocks first (```code```)
        text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // 2. Handle inline code (`code`)
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // 3. Handle bold text (must come before italic to avoid conflicts)
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                  .replace(/__([^_]+)__/g, '<strong>$1</strong>');
        
        // 4. Handle italic text (more restrictive patterns)
        text = text.replace(/\*([^*\s][^*]*[^*\s]|\S)\*/g, '<em>$1</em>')
                  .replace(/_([^_\s][^_]*[^_\s]|\S)_/g, '<em>$1</em>');
        
        // 5. Handle bullet points - process line by line
        const lines = text.split('\n');
        let inList = false;
        const processedLines = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Check if this line is a bullet point
            if (/^[\*\-\+]\s+(.+)/.test(line)) {
                const content = line.replace(/^[\*\-\+]\s+/, '');
                if (!inList) {
                    processedLines.push('<ul>');
                    inList = true;
                }
                processedLines.push(`<li>${content}</li>`);
            } else {
                // If we were in a list and this line isn't a bullet, close the list
                if (inList) {
                    processedLines.push('</ul>');
                    inList = false;
                }
                processedLines.push(line);
            }
        }
        
        // Close any open list at the end
        if (inList) {
            processedLines.push('</ul>');
        }
        
        // 6. Convert line breaks to <br> (but not inside lists)
        text = processedLines.join('\n').replace(/\n(?!<\/ul>|<ul>|<li>|<\/li>)/g, '<br>');
        
        return text;
    }
});
