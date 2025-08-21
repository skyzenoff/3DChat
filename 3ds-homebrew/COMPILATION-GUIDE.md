# Guide de compilation pour 3DS Discord Homebrew

## Problèmes de compilation courants

### ❌ "Please set DEVKITARM in your environment"

**Cause :** devkitPro n'est pas installé sur votre système.

**Solutions :**

#### Option 1: Installer devkitPro (RECOMMANDÉE)
```bash
# Sur Ubuntu/Debian
wget https://github.com/devkitPro/pacman/releases/latest/download/devkitpro-pacman.amd64.deb
sudo dpkg -i devkitpro-pacman.amd64.deb

# Installer les outils 3DS
sudo dkp-pacman -S 3ds-dev

# Exporter les variables d'environnement
export DEVKITPRO=/opt/devkitpro
export DEVKITARM=${DEVKITPRO}/devkitARM
export PATH=${DEVKITPRO}/tools/bin:$PATH

# Compiler
make clean
make
```

#### Option 2: Dans Replit (simulation seulement)
```bash
# Génère une version de démonstration (pas un vrai homebrew)
./compile-replit.sh
```

### ❌ Erreurs de compilation avec headers

**Cause :** Installation incomplète de devkitPro.

**Solution :**
```bash
# Réinstaller complètement
sudo dkp-pacman -S 3ds-dev
sudo dkp-pacman -S libctru
```

### ❌ Erreurs de lien

**Cause :** Variables d'environnement non définies.

**Solution :**
```bash
# Ajouter à votre .bashrc ou .zshrc
echo 'export DEVKITPRO=/opt/devkitpro' >> ~/.bashrc
echo 'export DEVKITARM=${DEVKITPRO}/devkitARM' >> ~/.bashrc
echo 'export PATH=${DEVKITPRO}/tools/bin:$PATH' >> ~/.bashrc

# Recharger votre shell
source ~/.bashrc
```

## Environnements de développement

### ✅ Environnements supportés pour la vraie compilation
- **Windows** avec devkitPro installé
- **macOS** avec devkitPro installé
- **Linux (Ubuntu/Debian/Arch)** avec devkitPro installé

### ⚠️ Environnements avec limitations
- **Replit** - Simulation seulement, pas de vraie compilation
- **GitHub Codespaces** - Nécessite installation manuelle de devkitPro
- **Environnements cloud** - Généralement non supportés

## Configuration serveur

Avant de compiler, configurez votre serveur dans `source/main.c` :

```c
// Pour Replit Deployments
#define SERVER_HOST "votre-projet.username.repl.co"
#define SERVER_PORT 443  // HTTPS
#define SERVER_PATH "/api"

// Pour développement local
#define SERVER_HOST "192.168.1.100"  // IP de votre PC
#define SERVER_PORT 5000  // Port Flask
#define SERVER_PATH "/api"
```

## Scripts disponibles

| Script | Usage | Environnement |
|--------|-------|---------------|
| `make` | Compilation standard | Nécessite devkitPro |
| `./build.sh` | Script avancé avec vérifications | Nécessite devkitPro |
| `./compile-replit.sh` | Simulation pour développement | Fonctionne partout |
| `./demo-compile.sh` | Version démo simplifiée | Fonctionne partout |

## Fichiers générés

Après compilation réussie :
- `3ds-discord.3dsx` - Le homebrew à installer sur 3DS
- `3ds-discord.smdh` - Métadonnées de l'application
- `3ds-discord.elf` - Fichier debug (optionnel)

## Installation sur 3DS

1. **Prérequis :** Nintendo 3DS avec CFW (Custom Firmware)
2. **Copier :** `3ds-discord.3dsx` dans `/3ds/` de votre carte SD
3. **Lancer :** Depuis le Homebrew Launcher

## Dépannage avancé

### Vérifier l'installation de devkitPro
```bash
echo $DEVKITPRO    # Doit afficher /opt/devkitpro
echo $DEVKITARM    # Doit afficher /opt/devkitpro/devkitARM
which arm-none-eabi-gcc  # Doit trouver le compilateur
```

### Nettoyer complètement
```bash
make clean
rm -rf build/
rm -f *.3dsx *.smdh *.elf
```

### Compilation en mode debug
```bash
make clean
make DEBUG=1
```

## Support

Si vous rencontrez encore des problèmes :
1. Vérifiez que vous avez la dernière version de devkitPro
2. Consultez la [documentation officielle devkitPro](https://devkitpro.org/wiki/Getting_Started)
3. Utilisez `./compile-replit.sh` pour tester la logique du code sans compilation réelle