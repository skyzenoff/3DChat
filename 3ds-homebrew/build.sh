#!/bin/bash

# Script de compilation pour le homebrew 3DS Discord
# Ce script nécessite devkitPro installé

echo "🔨 Compilation du homebrew 3DS Discord..."

# Vérifier que devkitPro est installé
if [ -z "$DEVKITPRO" ]; then
    echo "❌ ERREUR: devkitPro n'est pas installé ou DEVKITPRO n'est pas défini"
    echo "📋 Pour installer devkitPro:"
    echo "   1. Téléchargez devkitpro-pacman depuis https://github.com/devkitPro/pacman/releases"
    echo "   2. Installez-le: sudo dpkg -i devkitpro-pacman.amd64.deb"
    echo "   3. Installez les outils 3DS: sudo dkp-pacman -S 3ds-dev"
    echo "   4. Exportez les variables: export DEVKITPRO=/opt/devkitpro"
    echo ""
    echo "💡 Alternative pour Replit/développement:"
    echo "   Utilisez ./compile-replit.sh pour une version de démonstration"
    exit 1
fi

# Vérifier que les variables d'environnement sont définies
if [ -z "$DEVKITARM" ]; then
    export DEVKITARM=$DEVKITPRO/devkitARM
fi

echo "📁 Répertoires devkitPro:"
echo "   DEVKITPRO: $DEVKITPRO"
echo "   DEVKITARM: $DEVKITARM"

# Nettoyer les anciens builds
echo "🧹 Nettoyage..."
make clean

# Compiler
echo "⚙️  Compilation en cours..."
if make; then
    echo "✅ Compilation réussie!"
    echo "📦 Fichier généré: 3ds-discord.3dsx"
    echo ""
    echo "📋 Pour installer sur votre 3DS:"
    echo "   1. Copiez 3ds-discord.3dsx dans le dossier /3ds/ de votre carte SD"
    echo "   2. Lancez-le depuis le Homebrew Launcher"
    echo ""
    echo "⚠️  Configuration requise dans source/main.c:"
    echo "    - SERVER_HOST: votre nom d'hôte (ex: mon-app.replit.app)"
    echo "    - SERVER_PORT: 80 pour HTTP, 443 pour HTTPS" 
    echo "    - SERVER_PATH: /api (chemin de l'API)"
else
    echo "❌ Erreur de compilation"
    echo "💡 Vérifiez que vous avez installé:"
    echo "   - 3ds-dev (outils de base)"
    echo "   - Variables d'environnement DEVKITPRO et DEVKITARM"
    echo ""
    echo "Installation: sudo dkp-pacman -S 3ds-dev"
    exit 1
fi