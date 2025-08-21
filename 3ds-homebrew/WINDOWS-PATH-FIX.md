# Résoudre les problèmes de chemins Windows

## Problème actuel

Votre projet se trouve dans :
```
C:\Users\mioch\Downloads\3DChat-main (6)\3DChat-main\3ds-homebrew
```

**Problèmes :**
- ❌ Espaces dans le nom `3DChat-main (6)`
- ❌ Parenthèses `(6)` causent des erreurs bash
- ❌ Chemin trop long et complexe

## Solution recommandée

### Étape 1: Déplacer le projet

1. **Créer un nouveau dossier simple :**
   ```cmd
   mkdir C:\dev
   ```

2. **Copier le projet :**
   ```cmd
   xcopy "C:\Users\mioch\Downloads\3DChat-main (6)\3DChat-main" "C:\dev\3ds-discord" /E /I
   ```

3. **Naviguer vers le nouveau dossier :**
   ```cmd
   cd C:\dev\3ds-discord\3ds-homebrew
   ```

### Étape 2: Compiler

```cmd
# Utiliser le script Windows spécial
build-windows.bat

# Ou utiliser make si pas d'espaces
make clean
make
```

## Alternative rapide

Si vous ne voulez pas déplacer le projet :

1. **Utiliser le script Windows :**
   ```cmd
   cd "C:\Users\mioch\Downloads\3DChat-main (6)\3DChat-main\3ds-homebrew"
   build-windows.bat
   ```

2. **Le script gère automatiquement :**
   - ✅ Nettoyage sans `make clean`
   - ✅ Chemins avec espaces
   - ✅ Messages d'erreur clairs

## Bonnes pratiques pour l'avenir

### ✅ Bons noms de dossiers
```
C:\dev\3ds-discord
C:\projects\homebrew
C:\code\nintendo-3ds
```

### ❌ Noms problématiques
```
C:\Users\nom\Downloads\Projet (1)\dossier
C:\Program Files\mon projet
C:\Mes Documents\3DS Homebrew
```

## Test de votre installation

Après déplacement, testez :

```cmd
cd C:\dev\3ds-discord\3ds-homebrew
echo %DEVKITPRO%
echo %DEVKITARM%
build-windows.bat
```

## Si ça marche toujours pas

1. **Vérifiez devkitPro :**
   - Réinstallez devkitProUpdater.exe
   - Cochez "Nintendo 3DS Development"
   - Redémarrez Windows

2. **Utilisez PowerShell :**
   ```powershell
   Set-Location "C:\dev\3ds-discord\3ds-homebrew"
   .\build-windows.bat
   ```

3. **Vérifiez l'antivirus :**
   - Ajoutez C:\devkitPro aux exclusions
   - Désactivez temporairement la protection temps réel