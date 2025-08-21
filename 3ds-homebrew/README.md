# 3DS Discord Homebrew

Un homebrew Nintendo 3DS/2DS pour utiliser Discord de manière native sur votre console.

## Fonctionnalités

- ✅ Interface native 3DS optimisée
- ✅ Connexion aux salons de chat
- ✅ Envoi et réception de messages en temps réel
- ✅ Système de navigation tactile et boutons
- ✅ Compatible avec tous les modèles 3DS/2DS
- ✅ Connexion sécurisée au serveur

## Prérequis

### Pour compiler :
- devkitPro avec devkitARM
- libctru
- libcurl (portlib)
- json-c (portlib)

### Pour utiliser :
- Nintendo 3DS/2DS avec CFW (Custom Firmware)
- Homebrew Launcher
- Connexion Internet Wi-Fi

## Installation

### 1. Télécharger le homebrew
Téléchargez le fichier `3ds-discord.3dsx` depuis les releases.

### 2. Copier sur votre carte SD
Placez le fichier dans le dossier `/3ds/` de votre carte SD.

### 3. Configuration du serveur
Modifiez l'URL du serveur dans le fichier `source/main.c` ligne 10 :
```c
#define SERVER_URL "http://your-server-url.com"
```

## Compilation

```bash
# Installer devkitPro
sudo dkp-pacman -S 3ds-dev

# Installer les dépendances
sudo dkp-pacman -S 3ds-curl 3ds-json-c

# Compiler
make clean
make
```

## Utilisation

### Contrôles

**Écran de connexion :**
- D-PAD : Navigation
- A : Se connecter
- START : Quitter

**Liste des salons :**
- D-PAD Haut/Bas : Sélectionner un salon
- A : Rejoindre le salon sélectionné
- Y : Actualiser la liste
- START : Quitter

**Salon de chat :**
- A : Écrire un message
- Y : Actualiser les messages
- B : Retourner aux salons
- START : Quitter

**Saisie de message :**
- Clavier tactile pour écrire
- A : Envoyer le message
- B : Annuler

### Premier lancement

1. Lancez le homebrew depuis le Homebrew Launcher
2. Entrez vos identifiants de connexion
3. Sélectionnez un salon de chat
4. Commencez à discuter !

## Architecture

Le homebrew utilise une architecture client-serveur :

### Client 3DS (C/libctru)
- Interface utilisateur native
- Gestion des contrôles et affichage
- Communication HTTP avec le serveur
- Parser JSON pour les données

### Serveur (Flask/Python)
- API REST pour les opérations
- Base de données PostgreSQL
- Authentification des utilisateurs
- Gestion des messages et salons

## API du serveur

### Endpoints utilisés par le homebrew :

- `POST /api/login` - Connexion utilisateur
- `GET /api/rooms?user=username` - Liste des salons
- `GET /api/room/{id}/messages?user=username` - Messages d'un salon
- `POST /api/room/{id}/send` - Envoyer un message

## Développement

### Structure du projet
```
3ds-homebrew/
├── source/           # Code source C
│   └── main.c       # Fichier principal
├── include/         # Headers
├── gfx/            # Ressources graphiques
├── Makefile        # Configuration de compilation
└── README.md       # Documentation
```

### Fonctionnalités à venir
- [ ] Messages privés
- [ ] Système d'amis
- [ ] Notifications sonores
- [ ] Émojis et réactions
- [ ] Photos et images
- [ ] Salons vocaux (si possible)

## Dépannage

### Problèmes courants :

**"Erreur de connexion"**
- Vérifiez votre connexion Internet
- Assurez-vous que l'URL du serveur est correcte
- Le serveur doit être accessible depuis Internet

**"Impossible de se connecter"**
- Vérifiez vos identifiants
- Le serveur Flask doit être en marche
- Ports 80/443 ouverts sur le serveur

**"Homebrew ne se lance pas"**
- CFW correctement installé
- Homebrew Launcher fonctionnel
- Fichier .3dsx dans le bon dossier

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche feature
3. Committer vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Crédits

- devkitPro pour les outils de développement
- libctru pour les fonctions 3DS
- La communauté homebrew 3DS

## Avertissement

Ce homebrew n'est pas affilié à Discord Inc. Il s'agit d'un projet indépendant créé par des passionnés.

L'utilisation de ce homebrew nécessite un Custom Firmware, ce qui peut annuler la garantie de votre console. Utilisez-le à vos propres risques.