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
    echo "⚠️  N'oubliez pas de modifier SERVER_URL dans source/main.c"
    echo "    avec l'adresse de votre serveur Flask avant compilation!"
else
    echo "❌ Erreur de compilation"
    echo "💡 Vérifiez que vous avez installé:"
    echo "   - 3ds-dev (outils de base)"
    echo "   - Variables d'environnement DEVKITPRO et DEVKITARM"
    echo ""
    echo "Installation: sudo dkp-pacman -S 3ds-dev"
    exit 1
fi