// Socket.IO client-side implementation
const socket = io();

// Make socket available globally
window.socket = socket;

// Connect to Socket.IO server
socket.on('connect', () => {
    console.log('Connected to server');
});

// Handle connection success
socket.on('connection_success', (data) => {
    console.log('Connection successful', data);
});

// Join a channel
function joinChannel(channelId) {
    console.log('Joining channel:', channelId);
    socket.emit('join', { channel_id: channelId });
    // Store current channel ID in a data attribute for later use
    document.getElementById('message-input-form').dataset.channelId = channelId;
}

// Leave a channel
function leaveChannel(channelId) {
    console.log('Leaving channel:', channelId);
    socket.emit('leave', { channel_id: channelId });
}

// Send a message
function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const content = messageInput.value.trim();
    const channelId = document.getElementById('message-input-form').dataset.channelId;
    
    if (content && channelId) {
        socket.emit('message', {
            channel_id: channelId,
            content: content
        });
        messageInput.value = '';
        
        // Remove "No messages yet" notification if it exists
        removeNoMessagesNotification();
    }
}

// Edit a message
function editMessage(messageId, content) {
    socket.emit('edit_message', {
        message_id: messageId,
        content: content
    });
}

// Delete a message
function deleteMessage(messageId) {
    socket.emit('delete_message', {
        message_id: messageId
    });
}

// Handle new message from server
socket.on('new_message', (data) => {
    addMessageToChat(data);
    
    // Remove "No messages yet" notification if it exists
    removeNoMessagesNotification();
});

// Handle message update from server
socket.on('message_updated', (data) => {
    updateMessage(data);
});

// Handle message deletion from server
socket.on('message_deleted', (data) => {
    removeMessage(data.id);
});

// Handle user joined notification
socket.on('user_joined', (data) => {
    console.log(`${data.username} joined the channel`);
    // Could add a notification to the UI
});

// Handle user left notification
socket.on('user_left', (data) => {
    console.log(`${data.username} left the channel`);
    // Could add a notification to the UI
});

// Remove "No messages yet" notification
function removeNoMessagesNotification() {
    const noMessagesElement = document.querySelector('.no-messages');
    if (noMessagesElement) {
        noMessagesElement.remove();
    }
}

// Remove a message from the chat
function removeMessage(messageId) {
    const messageElement = document.getElementById(`message-${messageId}`);
    if (messageElement) {
        messageElement.remove();
    }
}

// Helper function to escape HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Start editing a message
function startEditMessage(messageId) {
    const messageElement = document.getElementById(`message-${messageId}`);
    if (!messageElement) return;
    
    const messageText = messageElement.querySelector('.message-text');
    const currentContent = messageText.textContent;
    
    messageText.innerHTML = `
        <form id="edit-form-${messageId}" onsubmit="submitEditMessage(event, '${messageId}')">
            <input type="text" id="edit-input-${messageId}" value="${escapeHtml(currentContent)}">
            <button type="submit">Save</button>
            <button type="button" onclick="cancelEditMessage('${messageId}', '${escapeHtml(currentContent)}')">Cancel</button>
        </form>
    `;
    
    const editInput = document.getElementById(`edit-input-${messageId}`);
    editInput.focus();
    editInput.setSelectionRange(editInput.value.length, editInput.value.length);
}

// Submit an edited message
function submitEditMessage(event, messageId) {
    event.preventDefault();
    const editInput = document.getElementById(`edit-input-${messageId}`);
    const content = editInput.value.trim();
    
    if (content) {
        editMessage(messageId, content);
    }
}

// Cancel editing a message
function cancelEditMessage(messageId, originalContent) {
    const messageElement = document.getElementById(`message-${messageId}`);
    if (!messageElement) return;
    
    const messageText = messageElement.querySelector('.message-text');
    messageText.textContent = originalContent;
}

// Confirm deletion of a message
function confirmDeleteMessage(messageId) {
    // Use custom modal instead of browser confirm
    const modal = document.getElementById('delete-confirmation-modal');
    const confirmBtn = document.getElementById('confirm-delete-btn');
    const cancelBtn = document.getElementById('cancel-delete-btn');
    const messageIdInput = document.getElementById('delete-message-id');
    
    if (modal && confirmBtn && cancelBtn && messageIdInput) {
        messageIdInput.value = messageId;
        modal.style.display = 'block';
        
        // Focus on cancel button by default (safer option)
        cancelBtn.focus();
    } else {
        // Fallback to browser confirm if modal not found
        if (confirm('Are you sure you want to delete this message?')) {
            deleteMessage(messageId);
        }
    }
}

// Set up event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set up message send button click
    const sendButton = document.getElementById('message-send-button');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    // Set up message input enter key press
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Join channel if channel ID is in the page
    const channelElement = document.getElementById('current-channel');
    if (channelElement) {
        const channelId = channelElement.dataset.channelId;
        if (channelId) {
            joinChannel(channelId);
        }
    }
    
    // Set up delete confirmation modal buttons
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const deleteModal = document.getElementById('delete-confirmation-modal');
    
    if (confirmDeleteBtn && deleteModal) {
        confirmDeleteBtn.addEventListener('click', () => {
            const messageId = document.getElementById('delete-message-id').value;
            if (messageId) {
                deleteMessage(messageId);
            }
            deleteModal.style.display = 'none';
        });
    }
    
    if (cancelDeleteBtn && deleteModal) {
        cancelDeleteBtn.addEventListener('click', () => {
            deleteModal.style.display = 'none';
        });
    }
});
