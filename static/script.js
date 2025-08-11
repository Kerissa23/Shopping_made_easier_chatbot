document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // --- Client-Side State Management ---
    let sessionState = {
        chat_history: [], // Add chat history here
        session_products: [],
        current_view: [],
        display_offset: 0
    };

    appendBotMessage("Hello! What can I help you find today?");

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        appendUserMessage(userMessage);
        userInput.value = '';
        showSpinner();

        // Add user message to history before sending
        sessionState.chat_history.push(["user", userMessage]);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    state: sessionState 
                }),
            });

            if (!response.ok) {
                if (response.status === 422) {
                    console.error("Validation Error:", await response.json());
                    throw new Error("Data validation error (422).");
                }
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // The backend now returns the complete, updated state
            sessionState = data.new_state;

            hideSpinner();
            appendBotMessage(data.bot_message, data.products_to_display);

        } catch (error) {
            console.error('Error:', error);
            hideSpinner();
            appendBotMessage("Oops! Something went wrong on the server.");
        }
    });

    // ... (rest of the JS functions: appendUserMessage, appendBotMessage, etc. remain the same)
    
    function appendUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'user-message');
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        scrollToBottom();
    }

    function appendBotMessage(message, products = []) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'bot-message');

        const textElement = document.createElement('p');
        textElement.textContent = message;
        messageElement.appendChild(textElement);

        if (products && products.length > 0) {
            const productGrid = document.createElement('div');
            productGrid.classList.add('product-grid');

            products.forEach(p => {
                const thumbnail = p.thumbnail && p.thumbnail !== 'N/A' ? p.thumbnail : 'https://via.placeholder.com/150';
                const title = p.title || 'No Title';
                const price = p.price || 'N/A';
                const link = p.link || '#';
                const source = p.source || 'Unknown';

                const card = document.createElement('div');
                card.classList.add('product-card');
                card.innerHTML = `
                    <div class="product-source">${source}</div>
                    <img src="${thumbnail}" alt="${title}">
                    <div class="product-title">${title}</div>
                    <div class="product-price">${price}</div>
                    <a href="${link}" target="_blank" class="product-link">View Product</a>
                `;
                productGrid.appendChild(card);
            });
            messageElement.appendChild(productGrid);
        }
        
        chatBox.appendChild(messageElement);
        scrollToBottom();
    }

    function showSpinner() {
        const spinnerElement = document.createElement('div');
        spinnerElement.id = 'spinner';
        spinnerElement.classList.add('message', 'bot-message', 'spinner');
        spinnerElement.innerHTML = `<div><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>`;
        chatBox.appendChild(spinnerElement);
        scrollToBottom();
    }

    function hideSpinner() {
        const spinner = document.getElementById('spinner');
        if (spinner) spinner.remove();
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});