// Custom context menu functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create context menu element
    const contextMenu = document.createElement('div');
    contextMenu.className = 'context-menu';
    contextMenu.id = 'context-menu';
    document.body.appendChild(contextMenu);
    
    // Message context menu items
    const messageContextItems = {
        'message': [
            { icon: '📋', label: 'Copy Text', action: 'copyText' },
            { icon: '📝', label: 'Edit Message', action: 'editMessage', ownerOnly: true },
            { separator: true },
            { icon: '🗑️', label: 'Delete Message', action: 'deleteMessage', ownerOnly: true, danger: true }
        ],
        'channel': [
            { icon: '📌', label: 'Pin Channel', action: 'pinChannel' },
            { icon: '🔔', label: 'Mute Channel', action: 'muteChannel' },
            { separator: true },
            { icon: '📝', label: 'Edit Channel', action: 'editChannel', adminOnly: true },
            { icon: '🗑️', label: 'Delete Channel', action: 'deleteChannel', adminOnly: true, danger: true }
        ],
        'user': [
            { icon: '💬', label: 'Message', action: 'messageUser' },
            { icon: '👤', label: 'View Profile', action: 'viewProfile' },
            { separator: true },
            { icon: '🔇', label: 'Mute', action: 'muteUser' },
            { icon: '⛔', label: 'Block', action: 'blockUser', danger: true }
        ]
    };
    
    // Prevent default context menu
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        
        // Close any open context menu
        contextMenu.style.display = 'none';
        
        // Determine context type
        let contextType = 'default';
        let targetElement = e.target;
        let targetId = null;
        
        // Check if clicked on a message
        if (targetElement.closest('.message')) {
            contextType = 'message';
            targetId = targetElement.closest('.message').id.replace('message-', '');
        } 
        // Check if clicked on a channel
        else if (targetElement.closest('.channel-item')) {
            contextType = 'channel';
            targetId = targetElement.closest('.channel-item').getAttribute('href').split('/').pop();
        }
        // Check if clicked on a user
        else if (targetElement.closest('.member-item')) {
            contextType = 'user';
            targetId = targetElement.closest('.member-item').getAttribute('data-user-id');
        }
        
        // Build context menu based on context type
        buildContextMenu(contextType, targetId);
        
        // Position and show context menu
        contextMenu.style.left = e.pageX + 'px';
        contextMenu.style.top = e.pageY + 'px';
        contextMenu.style.display = 'block';
    });
    
    // Close context menu when clicking elsewhere
    document.addEventListener('click', function() {
        contextMenu.style.display = 'none';
    });
    
    // Build context menu based on context type
    function buildContextMenu(contextType, targetId) {
        // Clear existing menu items
        contextMenu.innerHTML = '';
        
        // Get menu items for context type
        const menuItems = messageContextItems[contextType] || [
            { icon: '📋', label: 'Copy', action: 'copy' }
            // Paste option removed as requested
        ];
        
        // Add items to menu
        menuItems.forEach(item => {
            if (item.separator) {
                const separator = document.createElement('div');
                separator.className = 'context-menu-separator';
                contextMenu.appendChild(separator);
            } else {
                const menuItem = document.createElement('div');
                menuItem.className = 'context-menu-item';
                if (item.danger) menuItem.classList.add('danger');
                
                // Check if this item should be shown based on permissions
                const isCurrentUserOwner = targetId && isMessageOwner(targetId);
                const isServerOwner = isUserServerOwner();
                
                if ((item.ownerOnly && !isCurrentUserOwner) || 
                    (item.adminOnly && !isServerOwner)) {
                    return; // Skip this item
                }
                
                menuItem.innerHTML = `
                    <div class="context-menu-icon">${item.icon}</div>
                    <div class="context-menu-label">${item.label}</div>
                    ${item.shortcut ? `<div class="context-menu-shortcut">${item.shortcut}</div>` : ''}
                `;
                
                menuItem.addEventListener('click', function() {
                    handleContextMenuAction(item.action, targetId, contextType);
                });
                
                contextMenu.appendChild(menuItem);
            }
        });
    }
    
    // Handle context menu actions
    function handleContextMenuAction(action, targetId, contextType) {
        console.log(`Action: ${action}, Target ID: ${targetId}, Context: ${contextType}`);
        
        switch(action) {
            case 'copyText':
                const messageText = document.querySelector(`#message-${targetId} .message-text`).textContent;
                navigator.clipboard.writeText(messageText);
                break;
                
            case 'editMessage':
                // Implement edit message functionality
                startEditMessage(targetId);
                break;
                
            case 'deleteMessage':
                // Implement delete message functionality
                confirmDeleteMessage(targetId);
                break;
                
            case 'deleteChannel':
                // Implement delete channel functionality
                if (confirm('Are you sure you want to delete this channel? This action cannot be undone.')) {
                    window.location.href = `/channel/${targetId}/delete`;
                }
                break;
                
            case 'editChannel':
                // Implement edit channel functionality
                alert('Edit channel functionality coming soon!');
                break;
                
            case 'pinChannel':
                // Implement pin channel functionality
                alert('Pin channel functionality coming soon!');
                break;
                
            case 'muteChannel':
                // Implement mute channel functionality
                alert('Mute channel functionality coming soon!');
                break;
                
            case 'messageUser':
                // Implement message user functionality
                alert('Direct messaging functionality coming soon!');
                break;
                
            case 'viewProfile':
                // Implement view profile functionality
                alert('User profile view functionality coming soon!');
                break;
                
            case 'muteUser':
                // Implement mute user functionality
                alert('Mute user functionality coming soon!');
                break;
                
            case 'blockUser':
                // Implement block user functionality
                alert('Block user functionality coming soon!');
                break;
                
            case 'copy':
                // Implement copy functionality
                const selection = window.getSelection().toString();
                if (selection) {
                    navigator.clipboard.writeText(selection);
                }
                break;
                
            default:
                console.log('Action not implemented yet');
        }
    }
    
    // Helper functions
    function isMessageOwner(messageId) {
        const message = document.getElementById(`message-${messageId}`);
        return message && message.querySelector('.message-content').classList.contains('message-own');
    }
    
    function isUserServerOwner() {
        // Check if current user is the server owner by looking at the server header data attribute
        const serverHeader = document.querySelector('.server-header');
        if (!serverHeader) return false;
        
        const serverId = serverHeader.getAttribute('data-server-id');
        if (!serverId) return false;
        
        // Check if the current user is marked as the owner in the DOM
        // This assumes there's a data attribute on the body or another element indicating ownership
        const isOwner = document.body.getAttribute('data-is-server-owner') === 'true';
        return isOwner;
    }
});
