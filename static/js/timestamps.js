class TimestampFormatter {
  constructor() {
    this.timestamps = new Map();
  }

  init() {
  }

  formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric'
    }) + ' ' + date.toLocaleTimeString([], { 
      hour: 'numeric', 
      minute: '2-digit', 
      hour12: true 
    });
  }
  
  addTimestamp(elementId, timestamp) {
    this.timestamps.set(elementId, timestamp);
    return this.formatTimestamp(timestamp);
  }
  
  destroy() {
    this.timestamps.clear();
  }
}

const timestampFormatter = new TimestampFormatter();

document.addEventListener('DOMContentLoaded', () => {
  timestampFormatter.init();
  
  document.querySelectorAll('.message-timestamp').forEach(element => {
    const timestamp = element.getAttribute('data-timestamp');
    if (timestamp) {
      element.textContent = timestampFormatter.formatTimestamp(timestamp);
    }
  });
});

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function addMessageToChat(data) {
    const messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    messageElement.id = `message-${data.id}`;
    
    const timestampId = `timestamp-${data.id}`;
    
    const formattedTimestamp = timestampFormatter.addTimestamp(timestampId, data.created_at);
    
    const isCurrentUser = data.user_id === currentUserId;
    const messageClass = isCurrentUser ? 'message-own' : 'message-other';
    
    const safeContent = escapeHtml(data.content);
    
    messageElement.innerHTML = `
        <div class="message-avatar">
            <img src="${escapeHtml(data.image_url || '/static/images/default_avatar.png')}" alt="${escapeHtml(data.username)}">
        </div>
        <div class="message-content ${messageClass}">
            <div class="message-header">
                <span class="message-username">${escapeHtml(data.username)}</span>
                <span class="message-timestamp" id="${timestampId}" data-timestamp="${data.created_at}">${formattedTimestamp}</span>
            </div>
            <div class="message-text">${safeContent}</div>
            ${isCurrentUser ? `
                <div class="message-actions">
                    <button class="btn-edit" onclick="startEditMessage('${data.id}')">Edit</button>
                    <button class="btn-delete" onclick="confirmDeleteMessage('${data.id}')">Delete</button>
                </div>
            ` : ''}
        </div>
    `;
    
    messagesContainer.appendChild(messageElement);
    
    messageElement.scrollIntoView({ behavior: 'smooth' });
}

function updateMessage(data) {
    const messageElement = document.getElementById(`message-${data.id}`);
    if (!messageElement) return;
    
    const messageText = messageElement.querySelector('.message-text');
    if (messageText) {
        messageText.textContent = data.content;
    }
}
