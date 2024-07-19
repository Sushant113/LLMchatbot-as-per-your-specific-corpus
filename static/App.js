function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    
    if (message) {
        appendMessage('You', message, 'user');
        userInput.value = '';
        
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message }),
        })
        .then(response => response.json())
        .then(data => {
            appendMessage('Chatbot', data.answer, 'chatbot');
            updateMetrics(data.latency);
        })
        .catch(error => {
            console.error('Error:', error);
            appendMessage('Chatbot', 'Sorry, there was an error processing your request.', 'chatbot');
        });
    }
}

function appendMessage(sender, message, className) {
    const chatbox = document.getElementById('chatbox');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function updateMetrics(latency) {
    const metricsDiv = document.getElementById('metrics');
    metricsDiv.innerHTML = `
        <p>Response time: ${latency.toFixed(3)} seconds</p>
    `;
}

// Add event listener for Enter key
document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});