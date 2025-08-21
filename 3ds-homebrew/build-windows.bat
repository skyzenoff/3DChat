@echo off
echo.
echo 🔨 Compilation 3DS Discord pour Windows
echo.

REM Vérifier que devkitPro est installé
if not defined DEVKITPRO (
    echo ❌ ERREUR: devkitPro n'est pas installé
    echo.
    echo 📋 Pour installer devkitPro:
    echo    1. Téléchargez depuis: https://github.com/devkitPro/installer/releases
    echo    2. Lancez devkitProUpdater.exe en tant qu'administrateur
    echo    3. Sélectionnez "Nintendo 3DS Development"
    echo    4. Redémarrez votre invite de commande
    echo.
    pause
    exit /b 1
)

REM Afficher les chemins
echo 📁 Répertoires devkitPro:
echo    DEVKITPRO: %DEVKITPRO%
echo    DEVKITARM: %DEVKITARM%
echo.

REM Nettoyer les anciens fichiers (sans utiliser make clean à cause des espaces)
echo 🧹 Nettoyage des anciens fichiers...
if exist build rmdir /s /q build
if exist 3ds-discord.3dsx del 3ds-discord.3dsx
if exist 3ds-discord.smdh del 3ds-discord.smdh  
if exist 3ds-discord.elf del 3ds-discord.elf

REM Créer le répertoire build
if not exist build mkdir build

echo.
echo ⚙️  Compilation en cours...
echo    (Cela peut prendre quelques minutes)
echo.

REM Compiler avec make en gérant les espaces dans les chemins
make 2>error.log

if %errorlevel%==0 (
    echo ✅ Compilation réussie!
    echo.
    echo 📦 Fichiers générés:
    if exist 3ds-discord.3dsx (
        echo    ✓ 3ds-discord.3dsx - Homebrew principal
    )
    if exist 3ds-discord.smdh (
        echo    ✓ 3ds-discord.smdh - Métadonnées
    )
    echo.
    echo 📋 Installation sur 3DS:
    echo    1. Copiez 3ds-discord.3dsx dans le dossier /3ds/ de votre carte SD
    echo    2. Lancez depuis le Homebrew Launcher
    echo.
    echo ⚠️  N'oubliez pas de configurer SERVER_HOST dans source/main.c
    echo    avec l'adresse de votre serveur Replit avant utilisation!
) else (
    echo ❌ Erreur de compilation
    echo.
    echo 📋 Erreurs détaillées:
    if exist error.log (
        type error.log
        echo.
    )
    echo 💡 Solutions possibles:
    echo    1. Vérifiez que devkitPro est correctement installé
    echo    2. Déplacez le projet vers un dossier sans espaces ni caractères spéciaux
    echo    3. Exemple: C:\dev\3ds-homebrew au lieu de "Downloads\3DChat-main (6)"
    echo    4. Redémarrez votre invite de commande après installation devkitPro
)

if exist error.log del error.log
echo.
pause