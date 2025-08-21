# 3DS Discord Homebrew

Un homebrew Nintendo 3DS/2DS pour utiliser Discord de manière native sur votre console.

## Fonctionnalités

- ✅ Interface native 3DS optimisée
- ✅ Connexion aux salons de chat
- ✅ Envoi et réception de messages en temps réel
- ✅ Système de navigation tactile et boutons
- ✅ Compatible avec tous les modèles 3DS/2DS
- ✅ Connexion sécurisée au serveur

## Version actuelle : HYBRIDE INTELLIGENTE

Cette version s'adapte automatiquement à votre environnement :
- **Mode connecté** : Communique avec votre serveur Flask via HTTP natif
- **Fallback démo** : Fonctionne hors ligne si pas de réseau
- **Parser JSON natif** : Pas besoin de json-c ou autres dépendances
- **Interface complète** : Navigation D-PAD, saisie interactive, 3 utilisateurs test

## Prérequis

### Pour compiler :
- **devkitPro avec devkitARM** - Environnement de développement 3DS
- **libctru** - Bibliothèque système 3DS (incluse avec devkitPro)
- **Pas de dépendances externes** - HTTP et JSON natifs en C

### Environnements supportés :
- **Windows** avec devkitPro installé
- **Mac/Linux** avec devkitPro installé  
- **Replit** en mode démonstration seulement (pas de vraie compilation)

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
Modifiez l'adresse du serveur dans `source/main.c` lignes 17-19 :
```c
#define SERVER_HOST "votre-app.replit.app"
#define SERVER_PORT 443  // HTTPS recommandé
#define SERVER_PATH "/api"
```

Voir `configuration-exemple.c` pour plus d'exemples de configuration.

## Compilation

### Version complète (recommandée) :
```bash
# 1. Installer devkitPro
sudo dkp-pacman -S 3ds-dev

# 2. Compiler le homebrew
make clean
make

# Alternative avec le script
./build.sh
```

### Dans Replit (démonstration seulement) :
```bash
# Simulation de compilation (génère des fichiers de démo)
./compile-replit.sh
```

### Problèmes de compilation courants :
- **"Please set DEVKITARM"** → devkitPro n'est pas installé → [Guide Windows](WINDOWS-SETUP.md) | [Guide général](COMPILATION-GUIDE.md)
- **"missing separator (TAB instead of spaces)"** → Makefile corrigé ✅
- **Erreurs de liens** → Vérifiez que libctru est installé  
- **Headers manquants** → Installez 3ds-dev complètement
- **Environnement Replit** → Utilisez `./compile-replit.sh` pour la démonstration

## Utilisation

### Contrôles

**Écran de connexion :**
- A : Se connecter comme Skyzen
- X : Se connecter comme Alice  
- Y : Se connecter comme Bob
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
- D-PAD Haut/Bas : Sélectionner un message prédéfini
- A : Confirmer et envoyer
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