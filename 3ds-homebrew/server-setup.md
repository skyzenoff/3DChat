# Configuration du serveur pour le homebrew 3DS

## Version actuelle : DÉMO OFFLINE

La version actuelle du homebrew fonctionne en mode démo offline pour éviter les problèmes de dépendances (json-c, curl). Elle inclut :

- **Données de démo** : 3 salons prédéfinis avec messages
- **Pas de réseau** : Fonctionne sans connexion Internet  
- **Interface complète** : Navigation, salons, messages, saisie

## Pour la version connectée (future)

Votre serveur Flask doit être accessible depuis Internet et supporter les requêtes HTTPS pour fonctionner avec le homebrew 3DS.

## Configuration nécessaire

### 1. Modifier l'URL du serveur

Dans `source/main.c`, ligne 10 :
```c
#define SERVER_URL "https://votre-domaine.com"  // Remplacez par votre URL
```

**Important :** Utilisez HTTPS (SSL) car la Nintendo 3DS n'accepte pas les connexions HTTP non sécurisées vers Internet.

### 2. Headers CORS (déjà configuré)

Le serveur Flask inclut déjà les routes API nécessaires :
- `/api/login` - Authentification
- `/api/rooms` - Liste des salons  
- `/api/room/{id}/messages` - Messages d'un salon
- `/api/room/{id}/send` - Envoyer un message

### 3. Déployer le serveur

Vous pouvez déployer votre serveur Flask sur :
- **Replit Deployments** (recommandé - déjà configuré)
- Heroku
- DigitalOcean
- AWS
- Google Cloud

## Test de l'API

Vous pouvez tester l'API avec curl :

```bash
# Test de connexion
curl -X POST https://votre-domaine.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"votre_username","password":"votre_password"}'

# Test récupération des salons  
curl "https://votre-domaine.com/api/rooms?user=votre_username"

# Test récupération des messages
curl "https://votre-domaine.com/api/room/1/messages?user=votre_username"

# Test envoi de message
curl -X POST https://votre-domaine.com/api/room/1/send \
  -H "Content-Type: application/json" \
  -d '{"user":"votre_username","message":"Hello depuis l API!"}'
```

## Configuration Nintendo 3DS

### Connexion Internet
1. Paramètres système → Paramètres Internet
2. Configurez votre connexion Wi-Fi
3. Testez la connexion

### Installation CFW (Custom Firmware)
Le homebrew nécessite un CFW installé sur votre 3DS :
- **Luma3DS** (recommandé)
- **Homebrew Launcher**

### Installation du homebrew
1. Copiez `3ds-discord.3dsx` dans `/3ds/` sur votre carte SD
2. Lancez le Homebrew Launcher
3. Sélectionnez "3ds-discord"

## Format de données API

### Connexion (`/api/login`)
```json
Request:
{
  "username": "nom_utilisateur",
  "password": "mot_de_passe"
}

Response:
{
  "success": true,
  "user": {
    "id": 1,
    "username": "nom_utilisateur", 
    "email": "email@example.com",
    "status": "online"
  }
}
```

### Salons (`/api/rooms`)
```json
Response:
{
  "success": true,
  "rooms": [
    {
      "id": 1,
      "name": "Général",
      "user_count": 5,
      "message_count": 42,
      "is_public": true
    }
  ]
}
```

### Messages (`/api/room/{id}/messages`)
```json
Response:
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "username": "utilisateur1",
      "content": "Hello world!",
      "timestamp": "2024-01-01 12:00:00"
    }
  ]
}
```

### Envoyer message (`/api/room/{id}/send`)
```json
Request:
{
  "user": "nom_utilisateur",
  "message": "Contenu du message"
}

Response:
{
  "success": true,
  "message": "Message envoyé"
}
```

## Dépannage

### Erreurs courantes

**"Connection failed"**
- Vérifiez que votre serveur est accessible via HTTPS
- Testez l'URL dans un navigateur
- Vérifiez les certificats SSL

**"SSL certificate error"**
- La 3DS n'accepte que les certificats SSL valides
- Utilisez Let's Encrypt ou un certificat commercial

**"API endpoint not found"**
- Vérifiez que les routes API sont bien configurées
- Testez avec curl depuis un ordinateur

**"Authentication failed"**
- Créez d'abord un compte via l'interface web
- Vérifiez username/password

## Limitations Nintendo 3DS

- **Mémoire limitée** : Limiter les messages affichés
- **Processeur lent** : Optimiser les requêtes
- **Wi-Fi limité** : Gestion d'erreur réseau robuste
- **Pas de clavier** : Interface simplifiée pour la saisie

## Sécurité

⚠️ **Important pour la production :**

1. **Chiffrez toujours les mots de passe** (fait)
2. **Utilisez HTTPS obligatoirement**
3. **Validez toutes les entrées** (fait)  
4. **Limitez le taux de requêtes** (à implémenter)
5. **Loggez les tentatives d'intrusion**

## Fonctionnalités futures

- Messages privés via API
- Système d'amis
- Upload d'images (si supporté)
- Notifications push
- Salons vocaux (très difficile sur 3DS)