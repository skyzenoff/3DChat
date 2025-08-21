# Installation devkitPro sur Windows

## Étape 1: Télécharger devkitPro

1. **Téléchargez l'installeur Windows :**
   - Allez sur : https://github.com/devkitPro/installer/releases
   - Téléchargez `devkitProUpdater-x.x.x.exe` (la version la plus récente)

## Étape 2: Installation

1. **Lancez l'installeur en tant qu'administrateur**
2. **Sélectionnez les composants à installer :**
   - ✅ `Nintendo 3DS Development`
   - ✅ `devkitARM`
   - ✅ `libctru` 
   - ✅ `General Tools`

3. **Chemin d'installation recommandé :** `C:\devkitPro`

## Étape 3: Variables d'environnement

L'installeur Windows configure automatiquement les variables, mais vérifiez :

1. **Ouvrir les variables d'environnement :**
   - `Win + R` → `sysdm.cpl` → `Variables d'environnement`

2. **Vérifier que ces variables existent :**
   ```
   DEVKITPRO = C:\devkitPro
   DEVKITARM = C:\devkitPro\devkitARM
   ```

3. **Ajouter au PATH :**
   ```
   C:\devkitPro\tools\bin
   C:\devkitPro\devkitARM\bin
   ```

## Étape 4: Test de l'installation

1. **Ouvrir une nouvelle invite de commande (cmd)**
2. **Tester les outils :**
   ```cmd
   echo %DEVKITPRO%
   echo %DEVKITARM%
   arm-none-eabi-gcc --version
   ```

## Étape 5: Compiler votre homebrew

⚠️ **IMPORTANT:** Les dossiers avec espaces causent des problèmes !

### Option A: Déplacer le projet (RECOMMANDÉ)
```cmd
# Créer un dossier simple
mkdir C:\dev
xcopy "votre-dossier-actuel" "C:\dev\3ds-discord" /E /I
cd C:\dev\3ds-discord\3ds-homebrew
```

### Option B: Script Windows spécial
```cmd
# Dans votre dossier actuel (même avec espaces)
build-windows.bat
```

### Option C: Make standard (si pas d'espaces)
```cmd
make clean  
make
```

## Résolution des problèmes Windows

### ❌ "Please set DEVKITARM"
- Redémarrez votre invite de commande après installation
- Vérifiez les variables d'environnement
- Réinstallez devkitPro si nécessaire

### ❌ "arm-none-eabi-gcc: command not found"
- Vérifiez que `C:\devkitPro\devkitARM\bin` est dans le PATH
- Redémarrez votre session Windows

### ❌ Erreurs de permissions
- Lancez l'invite de commande en tant qu'administrateur
- Assurez-vous que l'antivirus ne bloque pas devkitPro

### ❌ Erreurs de compilation avec libctru
```cmd
# Réinstaller libctru
pacman -S libctru
```

## Alternative: PowerShell

Si vous préférez PowerShell :

```powershell
# Vérifier l'installation
Get-ChildItem Env:DEVKITPRO
Get-ChildItem Env:DEVKITARM

# Compiler
Set-Location "C:\Users\mioch\Documents\3DChat-main\3ds-homebrew"
make clean
make
```

## Après compilation réussie

Vous devriez obtenir :
- ✅ `3ds-discord.3dsx` - À copier sur votre carte SD 3DS
- ✅ `3ds-discord.smdh` - Métadonnées de l'application

**Installation sur 3DS :**
1. Copiez `3ds-discord.3dsx` dans le dossier `/3ds/` de votre carte SD
2. Lancez depuis le Homebrew Launcher

## Configuration du serveur

Avant de compiler, modifiez `source/main.c` lignes 17-19 :

```c
// Pour utiliser avec votre serveur Replit
#define SERVER_HOST "votre-app.replit.dev"
#define SERVER_PORT 443
#define SERVER_PATH "/api"

// Pour test en local
#define SERVER_HOST "192.168.1.XXX"  // IP de votre PC
#define SERVER_PORT 5000
#define SERVER_PATH "/api"
```

## Support

Si vous avez encore des problèmes :
1. Vérifiez que Windows Defender ne bloque pas devkitPro
2. Essayez de réinstaller devkitPro complètement
3. Utilisez une invite de commande fraîche après installation