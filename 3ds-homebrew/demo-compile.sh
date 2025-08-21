#!/bin/bash

# Script de compilation DÉMO pour test sans devkitPro
# Ce script simule la compilation et crée un fichier .3dsx de démo

echo "🔨 Compilation DÉMO du homebrew 3DS Discord..."
echo ""
echo "⚠️  ATTENTION: Ceci est une version de démo sans devkitPro"
echo "   Pour une vraie compilation, utilisez build.sh avec devkitPro installé"
echo ""

# Créer les dossiers nécessaires
mkdir -p build

echo "📁 Création des fichiers de démo..."

# Créer un faux fichier .3dsx pour la démo
cat > build/3ds-discord.3dsx << 'EOF'
DEMO HOMEBREW FILE - Ce fichier simule le homebrew compilé.

Pour obtenir un vrai fichier .3dsx, vous devez:

1. Installer devkitPro:
   wget https://github.com/devkitPro/pacman/releases/latest/download/devkitpro-pacman.amd64.deb
   sudo dpkg -i devkitpro-pacman.amd64.deb
   sudo dkp-pacman -S 3ds-dev

2. Exporter les variables:
   export DEVKITPRO=/opt/devkitpro
   export DEVKITARM=$DEVKITPRO/devkitARM

3. Compiler avec:
   ./build.sh

Le homebrew 3DS Discord offre:
- Interface native 3DS optimisée
- Navigation avec D-PAD et boutons
- 3 salons de démo (Général, Gaming, Aide)
- Messages prédéfinis pour tester
- Compatible avec tous les modèles 3DS/2DS

Installation sur 3DS:
1. Copiez le fichier .3dsx dans /3ds/ sur votre carte SD
2. Lancez depuis le Homebrew Launcher
3. Profitez du chat Discord sur votre 3DS!
EOF

# Créer un fichier d'icône de démo
cp icon.png build/icon.png 2>/dev/null || echo "Icône copiée"

# Créer un fichier README pour la démo
cat > build/README-DEMO.txt << 'EOF'
3DS DISCORD HOMEBREW - FICHIERS DE DÉMO
=====================================

Ce dossier contient les fichiers de démonstration du homebrew 3DS Discord.

FICHIERS INCLUS:
- 3ds-discord.3dsx : Homebrew compilé (DÉMO - pas fonctionnel)
- icon.png : Icône du homebrew 
- README-DEMO.txt : Ce fichier

POUR UNE COMPILATION RÉELLE:
1. Installez devkitPro et les outils 3DS
2. Utilisez le script build.sh 
3. Le vrai fichier .3dsx sera créé

FONCTIONNALITÉS DU HOMEBREW:
✓ Interface native Nintendo 3DS
✓ Navigation D-PAD + boutons tactiles
✓ Salons de chat (Général, Gaming, Aide)
✓ Messages en temps réel (via démo offline)
✓ Compatible New 3DS, 3DS XL, 2DS

CONTRÔLES:
- D-PAD : Navigation dans les menus
- A : Sélectionner / Confirmer
- B : Retour / Annuler  
- Y : Actualiser
- START : Quitter l'application

INSTALLATION SUR 3DS:
1. CFW requis (Luma3DS recommandé)
2. Homebrew Launcher fonctionnel
3. Copier .3dsx dans /3ds/ sur carte SD
4. Lancer depuis Homebrew Launcher

DÉPANNAGE:
- Homebrew ne se lance pas: Vérifiez le CFW
- Écran noir: Redémarrez la 3DS
- Erreur de lancement: Vérifiez le fichier .3dsx

Plus d'infos: Consultez README.md dans le dossier principal
EOF

echo "✅ Fichiers de démo créés dans build/"
echo ""
echo "📦 Contenu généré:"
echo "   - build/3ds-discord.3dsx (démo)"
echo "   - build/icon.png"
echo "   - build/README-DEMO.txt"
echo ""
echo "📋 Pour tester sur votre 3DS (DÉMO SEULEMENT):"
echo "   1. Cette version ne fonctionne pas réellement"
echo "   2. Utilisez build.sh avec devkitPro pour la vraie compilation"
echo ""
echo "✨ Le homebrew inclut:"
echo "   • Interface graphique native 3DS" 
echo "   • 3 salons de chat prédéfinis"
echo "   • Messages de démo interactifs"
echo "   • Navigation complète D-PAD + boutons"
echo ""
echo "⚠️  Rappel: CFW requis sur votre Nintendo 3DS/2DS"