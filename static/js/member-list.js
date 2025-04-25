// Member list management
class MemberListManager {
    constructor() {
      this.serverMembers = new Map();
      this.socket = null;
      this.initialized = false;
      this.currentServerId = null;
    }
    
    init(socket) {
      if (this.initialized) return;
      
      this.socket = socket;
      this.initialized = true;
      
      // Get current server ID from the page
      const serverElement = document.querySelector('.server-header');
      if (serverElement) {
        this.currentServerId = serverElement.dataset.serverId;
        
        if (this.currentServerId) {
          // Join server room for member updates
          this.socket.emit('join_server', { server_id: this.currentServerId });
          
          // Request current server members
          this.socket.emit('get_server_members', { server_id: this.currentServerId });
        }
      }
      
      // Listen for server member events
      this.socket.on('server_members', (data) => {
        if (data.server_id === this.currentServerId) {
          this.serverMembers.set(data.server_id, data.members);
          this.updateMemberList();
        }
      });
      
      this.socket.on('server_member_joined', (data) => {
        if (data.server_id === this.currentServerId) {
          const members = this.serverMembers.get(data.server_id) || [];
          
          // Check if member already exists
          const existingMemberIndex = members.findIndex(m => m.id === data.user.id);
          if (existingMemberIndex === -1) {
            members.push(data.user);
            this.serverMembers.set(data.server_id, members);
            this.updateMemberList();
            
            // Show notification
            this.showNotification(`${data.user.username} joined the server`);
          }
        }
      });
      
      this.socket.on('server_member_left', (data) => {
        if (data.server_id === this.currentServerId) {
          const members = this.serverMembers.get(data.server_id) || [];
          
          // Find and remove the member
          const memberIndex = members.findIndex(m => m.id === data.user_id);
          if (memberIndex !== -1) {
            const username = members[memberIndex].username;
            members.splice(memberIndex, 1);
            this.serverMembers.set(data.server_id, members);
            this.updateMemberList();
            
            // Show notification
            this.showNotification(`${username} left the server`);
          }
        }
      });
    }
    
    updateMemberList() {
      const memberListElement = document.querySelector('.member-list');
      const memberCountElement = document.querySelector('.member-category');
      
      if (!memberListElement || !this.currentServerId) return;
      
      const members = this.serverMembers.get(this.currentServerId) || [];
      
      // Update member count
      if (memberCountElement) {
        memberCountElement.textContent = `Members - ${members.length}`;
      }
      
      // Clear current list
      memberListElement.innerHTML = '';
      
      // Add each member to the list
      members.forEach(member => {
        const memberElement = document.createElement('div');
        memberElement.className = 'member-item';
        memberElement.setAttribute('data-user-id', member.id);
        
        const isOnline = onlineStatusManager && onlineStatusManager.isUserOnline(member.id);
        
        memberElement.innerHTML = `
          <div class="member-avatar">
            <img src="${member.image_url || '/static/images/default_avatar.svg'}" alt="${member.username}">
          </div>
          <div class="member-name">${member.username}</div>
          <div class="member-status ${isOnline ? 'online' : 'offline'}"></div>
        `;
        
        memberListElement.appendChild(memberElement);
      });
    }
    
    showNotification(message) {
      // Create notification element
      const notification = document.createElement('div');
      notification.className = 'server-notification';
      notification.textContent = message;
      
      // Add to page
      document.body.appendChild(notification);
      
      // Remove after 3 seconds
      setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
          notification.remove();
        }, 500);
      }, 3000);
    }
  }
  
  // Create global instance
  const memberListManager = new MemberListManager();
  
  // Initialize when socket is ready
  document.addEventListener('DOMContentLoaded', () => {
    // Wait for socket to be initialized in socket.js
    const checkSocketInterval = setInterval(() => {
      if (window.socket) {
        memberListManager.init(window.socket);
        clearInterval(checkSocketInterval);
      }
    }, 100);
  });
  