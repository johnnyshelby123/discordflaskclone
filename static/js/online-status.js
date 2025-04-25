// Online status management
class OnlineStatusManager {
  constructor() {
    this.onlineUsers = new Set();
    this.socket = null;
    this.initialized = false;
  }
  
  init(socket) {
    if (this.initialized) return;
    
    this.socket = socket;
    this.initialized = true;
    
    // Add current user to online users
    this.addUser(currentUserId);
    
    // Listen for online status events
    this.socket.on('user_online', (data) => {
      this.addUser(data.user_id);
      this.updateStatusIndicators();
    });
    
    this.socket.on('user_offline', (data) => {
      this.removeUser(data.user_id);
      this.updateStatusIndicators();
    });
    
    // Request current online users
    this.socket.emit('get_online_users');
    
    // Listen for online users list
    this.socket.on('online_users_list', (data) => {
      this.onlineUsers = new Set(data.users);
      this.updateStatusIndicators();
    });
    
    // Update status when window gains focus
    window.addEventListener('focus', () => {
      this.socket.emit('user_active', { user_id: currentUserId });
      this.addUser(currentUserId);
      this.updateStatusIndicators();
    });
    
    // Update status when window loses focus
    window.addEventListener('blur', () => {
      // Keep user online even when tab is not focused
      // Could implement "away" status here if desired
    });
    
    // Update status before page unload
    window.addEventListener('beforeunload', () => {
      this.socket.emit('user_inactive', { user_id: currentUserId });
    });
    
    // Initial update
    this.updateStatusIndicators();
  }
  
  addUser(userId) {
    if (userId) {
      this.onlineUsers.add(userId);
      this.updateStatusIndicators();
    }
  }
  
  removeUser(userId) {
    if (userId) {
      this.onlineUsers.delete(userId);
      this.updateStatusIndicators();
    }
  }
  
  isUserOnline(userId) {
    return this.onlineUsers.has(userId);
  }
  
  updateStatusIndicators() {
    // Update all user status indicators in the UI
    document.querySelectorAll('[data-user-id]').forEach(element => {
      const userId = element.getAttribute('data-user-id');
      const statusIndicator = element.querySelector('.member-status');
      
      if (statusIndicator) {
        if (this.isUserOnline(userId)) {
          statusIndicator.classList.remove('offline');
          statusIndicator.classList.add('online');
        } else {
          statusIndicator.classList.remove('online');
          statusIndicator.classList.add('offline');
        }
      }
    });
    
    // Update current user status
    const userStatusElement = document.querySelector('.user-status');
    if (userStatusElement) {
      userStatusElement.textContent = 'Online';
      userStatusElement.classList.add('status-online');
    }
  }
}

// Create global instance
const onlineStatusManager = new OnlineStatusManager();

// Initialize when socket is ready
document.addEventListener('DOMContentLoaded', () => {
  // Wait for socket to be initialized in socket.js
  const checkSocketInterval = setInterval(() => {
    if (window.socket) {
      onlineStatusManager.init(window.socket);
      clearInterval(checkSocketInterval);
    }
  }, 100);
});
