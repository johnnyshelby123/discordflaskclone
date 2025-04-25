// Add server ID to the server header for member list updates
document.addEventListener('DOMContentLoaded', function() {
    const serverHeader = document.querySelector('.server-header');
    if (serverHeader) {
        // Get server ID from the URL or another source
        const serverIdMatch = window.location.pathname.match(/\/server\/([a-f0-9-]+)/);
        if (serverIdMatch && serverIdMatch[1]) {
            serverHeader.dataset.serverId = serverIdMatch[1];
        }
    }
});
