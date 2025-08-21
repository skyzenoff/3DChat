// Script minimal pour 3DS - compatible avec anciens navigateurs
var pollingInterval;
var currentRoom;

function startPolling(roomId) {
    currentRoom = roomId;
    
    // Arrêter le polling précédent s'il existe
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    // Polling toutes les 3 secondes pour éviter de surcharger la 3DS
    pollingInterval = setInterval(function() {
        updateMessages();
    }, 3000);
}

function updateMessages() {
    if (!currentRoom) return;
    
    // Utiliser XMLHttpRequest pour compatibilité 3DS (pas de fetch)
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_messages/' + currentRoom, true);
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var messagesContainer = document.getElementById('messages');
            var usersDisplay = document.getElementById('users-display');
            
            if (messagesContainer) {
                var response = xhr.responseText;
                
                // Séparer les messages de la liste des utilisateurs
                var parts = response.split('<div id="users-list">');
                if (parts.length === 2) {
                    // Mettre à jour les messages
                    messagesContainer.innerHTML = parts[0];
                    
                    // Mettre à jour la liste des utilisateurs
                    if (usersDisplay) {
                        var usersPart = parts[1].replace('</div>', '');
                        usersDisplay.innerHTML = usersPart;
                    }
                } else {
                    // Fallback: tout mettre dans messages
                    messagesContainer.innerHTML = response;
                }
                
                // Scroller vers le bas automatiquement
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    };
    
    xhr.send();
}

// Arrêter le polling quand on quitte la page
window.onbeforeunload = function() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
};

// Auto-focus sur le champ de message si présent
document.addEventListener('DOMContentLoaded', function() {
    var messageInput = document.querySelector('input[name="message"]');
    if (messageInput) {
        messageInput.focus();
    }
});
