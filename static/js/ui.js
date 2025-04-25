// UI interactions for Discord clone

document.addEventListener('DOMContentLoaded', () => {
    // Server dropdown menu functionality
    const serverDropdownBtn = document.getElementById('server-dropdown-btn');
    const serverDropdownMenu = document.getElementById('server-dropdown-menu');
    
    if (serverDropdownBtn && serverDropdownMenu) {
        serverDropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            serverDropdownMenu.style.display = serverDropdownMenu.style.display === 'none' ? 'block' : 'none';
            
            // Hide settings menu if open
            if (settingsMenu) {
                settingsMenu.style.display = 'none';
            }
        });
    }
    
    // Settings menu functionality
    const settingsBtn = document.getElementById('settings-btn');
    const settingsMenu = document.getElementById('settings-menu');
    const userSettingsBtn = document.getElementById('user-settings-btn');
    const userSettingsModal = document.getElementById('user-settings-modal');
    const closeSettingsModal = document.getElementById('close-settings-modal');
    const saveSettingsBtn = document.getElementById('save-settings');
    const cancelSettingsBtn = document.getElementById('cancel-settings');
    const logoutBtn = document.getElementById('logout-btn');
    
    if (settingsBtn && settingsMenu) {
        settingsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            settingsMenu.style.display = settingsMenu.style.display === 'none' ? 'block' : 'none';
            
            // Hide server dropdown if open
            if (serverDropdownMenu) {
                serverDropdownMenu.style.display = 'none';
            }
        });
    }
    
    if (userSettingsBtn && userSettingsModal) {
        userSettingsBtn.addEventListener('click', () => {
            userSettingsModal.style.display = 'block';
            settingsMenu.style.display = 'none';
        });
    }
    
    if (closeSettingsModal) {
        closeSettingsModal.addEventListener('click', () => {
            userSettingsModal.style.display = 'none';
        });
    }
    
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', () => {
            // Save settings logic would go here
            userSettingsModal.style.display = 'none';
            alert('Settings saved!');
        });
    }
    
    if (cancelSettingsBtn) {
        cancelSettingsBtn.addEventListener('click', () => {
            userSettingsModal.style.display = 'none';
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            window.location.href = '/auth/logout';
        });
    }
    
    // Invite modal functionality
    const inviteBtn = document.getElementById('invite-people-btn');
    const inviteModal = document.getElementById('invite-modal');
    const closeModal = document.querySelector('.close-modal');
    const copyInviteBtn = document.getElementById('copy-invite-link');
    
    if (inviteBtn && inviteModal) {
        inviteBtn.addEventListener('click', () => {
            inviteModal.style.display = 'block';
            serverDropdownMenu.style.display = 'none';
        });
    }
    
    if (closeModal) {
        closeModal.addEventListener('click', () => {
            inviteModal.style.display = 'none';
        });
    }
    
    if (copyInviteBtn) {
        copyInviteBtn.addEventListener('click', () => {
            const inviteLink = document.getElementById('invite-link');
            inviteLink.select();
            document.execCommand('copy');
            
            // Show copied notification
            copyInviteBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyInviteBtn.textContent = 'Copy';
            }, 2000);
        });
    }
    
    // Close dropdowns and modals when clicking outside
    document.addEventListener('click', (e) => {
        if (serverDropdownMenu && !serverDropdownBtn.contains(e.target)) {
            serverDropdownMenu.style.display = 'none';
        }
        
        if (settingsMenu && !settingsBtn.contains(e.target)) {
            settingsMenu.style.display = 'none';
        }
        
        if (inviteModal && e.target === inviteModal) {
            inviteModal.style.display = 'none';
        }
    });
});
