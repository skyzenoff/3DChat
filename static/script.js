// Script minimal pour 3DS - compatible avec anciens navigateurs
var pollingInterval;
var currentRoom;
var currentUser;

// Détection du navigateur
var is3DS = navigator.userAgent.indexOf('Nintendo 3DS') !== -1;
var isModernBrowser = !is3DS && 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices;

// Variables pour l'audio
var mediaRecorder;
var audioChunks = [];
var isRecording = false;

function startPolling(roomId, username) {
    currentRoom = roomId;
    currentUser = username;
    
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
    if (!currentRoom || !currentUser) return;
    
    // Utiliser XMLHttpRequest pour compatibilité 3DS (pas de fetch)
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_messages/' + currentRoom + '?user=' + encodeURIComponent(currentUser), true);
    
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

// Fonctions audio pour navigateurs modernes
function initAudio() {
    if (!isModernBrowser) return;
    
    // Demander permission microphone au chargement de la page
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            // Arrêter le stream immédiatement, on l'utilisera à la demande
            stream.getTracks().forEach(track => track.stop());
        })
        .catch(function(err) {
            console.log('Microphone non autorisé:', err);
        });
}

function startVoiceRecording() {
    if (!isModernBrowser || isRecording) return;
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = function(event) {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = function() {
                var audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendVoiceMessage(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            isRecording = true;
            
            // Mettre à jour l'interface
            var voiceBtn = document.getElementById('voice-btn');
            if (voiceBtn) {
                voiceBtn.textContent = '🔴 Arrêter';
                voiceBtn.onclick = stopVoiceRecording;
            }
        })
        .catch(function(err) {
            alert('Erreur microphone: ' + err.message);
        });
}

function stopVoiceRecording() {
    if (!mediaRecorder || !isRecording) return;
    
    mediaRecorder.stop();
    isRecording = false;
    
    // Mettre à jour l'interface
    var voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) {
        voiceBtn.textContent = '🎤 Vocal';
        voiceBtn.onclick = startVoiceRecording;
    }
}

function sendVoiceMessage(audioBlob) {
    var formData = new FormData();
    formData.append('user', currentUser);
    formData.append('voice_message', audioBlob);
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/send_voice/' + currentRoom, true);
    
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Message vocal envoyé avec succès
            updateMessages();
        }
    };
    
    xhr.send(formData);
}

function startVoiceCall() {
    if (!isModernBrowser) return;
    alert('Appel vocal démarré ! (Fonctionnalité en développement)');
}

// Auto-focus sur le champ de message si présent
document.addEventListener('DOMContentLoaded', function() {
    var messageInput = document.querySelector('input[name="message"]');
    if (messageInput) {
        messageInput.focus();
    }
    
    // Initialiser l'audio pour navigateurs modernes
    initAudio();
});
