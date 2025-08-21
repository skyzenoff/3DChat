3DS Discord Homebrew - Instructions de compilation
==================================================

IMPORTANT: Cette version de démo ne peut pas être compilée dans Replit
car l'environnement ne dispose pas de devkitPro.

Pour compiler le vrai homebrew:

1. INSTALLER DEVKITPRO
   - Téléchargez devkitPro: https://devkitpro.org/wiki/Getting_Started
   - Suivez les instructions d'installation pour votre OS

2. INSTALLER LES DÉPENDANCES
   sudo dkp-pacman -S 3ds-dev

3. COMPILER LE PROJET
   cd 3ds-homebrew
   make clean
   make

4. FICHIERS GÉNÉRÉS
   - 3ds-discord.3dsx : Le homebrew à copier sur carte SD
   - 3ds-discord.smdh : Métadonnées de l'application

5. INSTALLATION SUR 3DS
   - Copiez 3ds-discord.3dsx dans le dossier /3ds/ de votre carte SD
   - Lancez depuis le Homebrew Launcher

CONFIGURATION SERVEUR:
- Modifiez SERVER_HOST, SERVER_PORT et SERVER_PATH dans source/main.c
- Voir configuration-exemple.c pour des exemples

