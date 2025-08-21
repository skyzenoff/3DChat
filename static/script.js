// Script minimal pour 3DS - compatible avec anciens navigateurs
var pollingInterval;
var currentRoom;
var currentUser;
var currentFriend; // Pour les messages privés

// Détection du navigateur
var is3DS = navigator.userAgent.indexOf('Nintendo 3DS') !== -1;
var isModernBrowser = !is3DS && 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices;

// Variables pour l'audio
var mediaRecorder;
var audioChunks = [];
var isRecording = false;

// Variables pour les appels
var localStream;
var peerConnection;
var isInCall = false;

// Variables pour l'envoi d'images
var imageInput;

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

// Polling pour les messages privés
function startPrivatePolling(friendUsername, username) {
    currentFriend = friendUsername;
    currentUser = username;
    
    // Arrêter le polling précédent s'il existe
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    // Polling toutes les 3 secondes
    pollingInterval = setInterval(function() {
        updatePrivateMessages();
    }, 3000);
}

function updatePrivateMessages() {
    if (!currentFriend || !currentUser) return;
    
    // Utiliser XMLHttpRequest pour compatibilité 3DS
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_private_messages/' + encodeURIComponent(currentFriend) + '?user=' + encodeURIComponent(currentUser), true);
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var messagesContainer = document.getElementById('messages');
            
            if (messagesContainer) {
                messagesContainer.innerHTML = xhr.responseText;
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
    
    if (isInCall) {
        endVoiceCall();
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then(function(stream) {
            localStream = stream;
            isInCall = true;
            
            // Mettre à jour l'interface
            var callBtn = document.getElementById('call-btn');
            if (callBtn) {
                callBtn.textContent = '📞 Raccrocher';
                callBtn.style.backgroundColor = '#f04747';
            }
            
            // Notifier les autres utilisateurs de l'appel
            sendCallNotification('start');
            
            // Simuler la connexion audio (en réalité il faudrait WebRTC complet)
            alert('📞 Appel démarré ! Microphone actif pour le salon.');
        })
        .catch(function(err) {
            alert('Erreur microphone pour appel: ' + err.message);
        });
}

function endVoiceCall() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    
    isInCall = false;
    
    // Mettre à jour l'interface
    var callBtn = document.getElementById('call-btn');
    if (callBtn) {
        callBtn.textContent = '📞 Appel';
        callBtn.style.backgroundColor = '#7289da';
    }
    
    sendCallNotification('end');
}

function sendCallNotification(action) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/call_notification/' + currentRoom, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    
    var data = 'user=' + encodeURIComponent(currentUser) + 
               '&action=' + encodeURIComponent(action);
    
    xhr.send(data);
}

function selectImage() {
    if (!imageInput) {
        // Créer l'input file s'il n'existe pas
        imageInput = document.createElement('input');
        imageInput.type = 'file';
        imageInput.accept = 'image/*';
        imageInput.style.display = 'none';
        document.body.appendChild(imageInput);
        
        imageInput.onchange = function() {
            if (this.files && this.files[0]) {
                sendImageMessage(this.files[0]);
            }
        };
    }
    
    imageInput.click();
}

function sendImageMessage(file) {
    // Vérifier la taille du fichier (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('Image trop grande (max 5MB)');
        return;
    }
    
    var formData = new FormData();
    formData.append('user', currentUser);
    formData.append('image', file);
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/send_image/' + currentRoom, true);
    
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Image envoyée avec succès
            updateMessages();
        } else {
            alert('Erreur lors de l\'envoi de l\'image');
        }
    };
    
    xhr.onerror = function() {
        alert('Erreur réseau lors de l\'envoi de l\'image');
    };
    
    xhr.send(formData);
}

function showVoiceControlsIfNeeded() {
    // Vérifier si c'est un navigateur moderne
    var voiceControls = document.getElementById('voice-controls');
    if (voiceControls) {
        var urlParts = window.location.pathname.split('/');
        if (urlParts[1] === 'room') {
            var isPrivateRoom = document.body.getAttribute('data-room-private') === 'true';
            
            // Masquer les boutons sur 3DS
            var voiceBtn = document.getElementById('voice-btn');
            var callBtn = document.getElementById('call-btn');
            var imageBtn = document.getElementById('image-btn');
            
            if (is3DS) {
                // 3DS : pas de fonctionnalités multimédias
                voiceControls.style.display = 'none';
            } else {
                // PC/Mobile : afficher le panneau
                voiceControls.style.display = 'flex';
                
                // Masquer les boutons vocaux dans les salons publics
                if (voiceBtn) voiceBtn.style.display = (isModernBrowser && isPrivateRoom) ? 'inline-block' : 'none';
                if (callBtn) callBtn.style.display = (isModernBrowser && isPrivateRoom) ? 'inline-block' : 'none';
                
                // Image disponible sur PC/Mobile dans tous les salons
                if (imageBtn) imageBtn.style.display = 'inline-block';
            }
        }
    }
}

// Auto-focus sur le champ de message si présent
document.addEventListener('DOMContentLoaded', function() {
    var messageInput = document.querySelector('input[name="message"]');
    if (messageInput) {
        messageInput.focus();
    }
    
    // Initialiser l'audio pour navigateurs modernes
    initAudio();
    
    // Afficher les contrôles vocaux si nécessaire
    showVoiceControlsIfNeeded();
});
