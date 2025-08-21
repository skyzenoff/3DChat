/* 
 * Fichier d'exemple de configuration pour 3DS Discord Homebrew
 * Copiez ces lignes dans source/main.c aux lignes 17-19
 */

// ====== CONFIGURATION SERVEUR ======

// Pour Replit Deployments (RECOMMANDÉ)
#define SERVER_HOST "votre-projet.username.repl.co"
#define SERVER_PORT 443  // HTTPS
#define SERVER_PATH "/api"

// Pour un serveur local de développement
#define SERVER_HOST "192.168.1.100"  // IP locale de votre PC
#define SERVER_PORT 5000  // Port Flask par défaut
#define SERVER_PATH "/api"

// Pour un serveur personnalisé
#define SERVER_HOST "mon-discord-server.com"
#define SERVER_PORT 80   // HTTP (ou 443 pour HTTPS)
#define SERVER_PATH "/api"

// Pour ngrok (développement/test)
#define SERVER_HOST "abc123.ngrok.io"
#define SERVER_PORT 80
#define SERVER_PATH "/api"

// ====== NOTES IMPORTANTES ======

/*
 * HTTPS vs HTTP:
 * - HTTPS (port 443) recommandé pour la sécurité
 * - HTTP (port 80) plus simple pour le développement
 * - La 3DS supporte les deux protocols
 * 
 * Fallback automatique:
 * - Si le serveur n'est pas accessible, le homebrew
 *   fonctionne automatiquement en mode démo offline
 * 
 * Test de configuration:
 * - Testez d'abord avec un navigateur web normal
 * - URL complète: http://SERVER_HOST:SERVER_PORT/api/rooms
 * - Doit retourner du JSON avec la liste des salons
 */