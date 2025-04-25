// Channel list management
class ChannelListManager {
    constructor() {
      this.serverChannels = new Map();
      this.socket = null;
      this.initialized = false;
      this.currentServerId = null;
    }
    
    init(socket) {
      if (this.initialized) return;
      
      this.socket = socket;
      this.initialized = true;
      
      // Get current server ID from the page
      const serverHeader = document.querySelector('.server-header');
      if (serverHeader) {
        this.currentServerId = serverHeader.dataset.serverId;
        
        if (this.currentServerId) {
          // Request current server channels
          this.socket.emit('get_server_channels', { server_id: this.currentServerId });
        }
      }
      
      // Listen for server channel events
      this.socket.on('server_channels', (data) => {
        if (data.server_id === this.currentServerId) {
          this.serverChannels.set(data.server_id, data.channels);
          this.updateChannelList();
        }
      });
      
      this.socket.on('channel_created', (data) => {
        if (data.server_id === this.currentServerId) {
          const channels = this.serverChannels.get(data.server_id) || [];
          
          // Check if channel already exists
          const existingChannelIndex = channels.findIndex(c => c.id === data.channel.id);
          if (existingChannelIndex === -1) {
            channels.push(data.channel);
            this.serverChannels.set(data.server_id, channels);
            this.updateChannelList();
            
            // Show notification
            this.showNotification(`New channel created: #${data.channel.name}`);
          }
        }
      });
      
      this.socket.on('channel_deleted', (data) => {
        if (data.server_id === this.currentServerId) {
          const channels = this.serverChannels.get(data.server_id) || [];
          
          // Find and remove the channel
          const channelIndex = channels.findIndex(c => c.id === data.channel_id);
          if (channelIndex !== -1) {
            const channelName = channels[channelIndex].name;
            channels.splice(channelIndex, 1);
            this.serverChannels.set(data.server_id, channels);
            this.updateChannelList();
            
            // Show notification
            this.showNotification(`Channel deleted: #${channelName}`);
          }
        }
      });
    }
    
    updateChannelList() {
      const channelListElement = document.querySelector('.channel-list');
      
      if (!channelListElement || !this.currentServerId) return;
      
      const channels = this.serverChannels.get(this.currentServerId) || [];
      
      // Get the channel category element
      const channelCategory = channelListElement.querySelector('.channel-category');
      if (!channelCategory) return;
      
      // Clear current list (except for the category)
      const existingChannels = channelListElement.querySelectorAll('.channel-item');
      existingChannels.forEach(channel => channel.remove());
      
      // Add each channel to the list
      channels.forEach(channel => {
        const channelElement = document.createElement('a');
        channelElement.className = 'channel-item';
        channelElement.href = `/channel/${channel.id}`;
        
        // Check if this is the current channel
        const currentChannelElement = document.getElementById('current-channel');
        if (currentChannelElement && currentChannelElement.dataset.channelId === channel.id) {
          channelElement.classList.add('active');
        }
        
        channelElement.innerHTML = `
          <span class="channel-icon">#</span>
          <span class="channel-name">${channel.name}</span>
        `;
        
        channelListElement.appendChild(channelElement);
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
  const channelListManager = new ChannelListManager();
  
  // Initialize when socket is ready
  document.addEventListener('DOMContentLoaded', () => {
    // Wait for socket to be initialized in socket.js
    const checkSocketInterval = setInterval(() => {
      if (window.socket) {
        channelListManager.init(window.socket);
        clearInterval(checkSocketInterval);
      }
    }, 100);
  });
  