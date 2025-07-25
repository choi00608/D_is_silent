interface MessageData {
    message: string;
    timestamp: string;
}

// Define the structure for an action option based on our new backend response
interface ActionOption {
    text: string;
    next_point_id?: string | null;
    is_major?: boolean;
}

interface ApiResponse {
    user_message: MessageData;
    ai_message: MessageData;
    next_action_options?: ActionOption[]; // Use the new interface
}

document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chat-log') as HTMLDivElement | null;
    const chatInput = document.getElementById('chat-input') as HTMLInputElement | null;
    const sendButton = document.getElementById('send-button') as HTMLButtonElement | null;
    const actionOptionsContainer = document.getElementById('action-options-container') as HTMLDivElement | null;
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement | null;

    if (!chatLog || !chatInput || !sendButton || !actionOptionsContainer || !csrfTokenElement) {
        console.error('Essential DOM element not found. Chat functionality disabled.');
        return;
    }

    const sessionId = chatLog.dataset.sessionId;
    const csrftoken = csrfTokenElement.value;

    if (!sessionId) {
        console.error('Session ID not found. Chat functionality disabled.');
        return;
    }

    const addMessageToLog = (message: MessageData, sender: 'user' | 'ai') => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = message.message.replace(/\n/g, '<br>');
        const timeDiv = document.createElement('div');
        timeDiv.classList.add('message-time');
        timeDiv.textContent = message.timestamp;
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    const renderActionOptions = (options: ActionOption[]) => {
        actionOptionsContainer.innerHTML = ''; // Clear previous options
        if (options && options.length > 0) {
            options.forEach(option => {
                const button = document.createElement('button');
                button.classList.add('action-option-button');
                button.textContent = option.text;
                // Store the extra data on the button itself using data-* attributes
                button.dataset.isMajor = option.is_major ? 'true' : 'false';
                if (option.next_point_id) {
                    button.dataset.nextPointId = option.next_point_id;
                }

                button.addEventListener('click', () => {
                    sendMessage(option.text, {
                        is_major: option.is_major,
                        next_point_id: option.next_point_id
                    });
                    actionOptionsContainer.innerHTML = ''; // Clear options after click
                });
                actionOptionsContainer.appendChild(button);
            });
        }
    };

    const sendMessage = async (messageText?: string, options?: { is_major?: boolean, next_point_id?: string | null }) => {
        const textToSend = messageText || chatInput.value.trim();
        if (textToSend === '') return;

        const now = new Date();
        const temporaryUserMessage: MessageData = {
            message: textToSend,
            timestamp: `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        };
        addMessageToLog(temporaryUserMessage, 'user');

        const lastMessageElement = chatLog.lastElementChild;

        if (!messageText) {
            chatInput.value = '';
        }

        try {
            const url = `/api/send_message/${sessionId}/`;
            const payload = {
                message: textToSend,
                is_major: options?.is_major || false,
                next_point_id: options?.next_point_id || null
            };

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Network response was not ok. Status: ${response.status}`);
            }

            const data: ApiResponse = await response.json();

            setTimeout(() => {
                addMessageToLog(data.ai_message, 'ai');
                renderActionOptions(data.next_action_options || []);
            }, 500);

        } catch (error) {
            console.error('Error sending message:', error);
            if (lastMessageElement) {
                chatLog.removeChild(lastMessageElement);
            }
            if (!messageText) {
                chatInput.value = textToSend;
            }
        }
    };

    sendButton.addEventListener('click', () => sendMessage());
    chatInput.addEventListener('keypress', (event: KeyboardEvent) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    // Initial fetch or setup can go here if needed
    // For example, to get the first set of actions when the page loads.
    chatLog.scrollTop = chatLog.scrollHeight;
});