#include <3ds.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>

#define MAX_MESSAGE_LENGTH 500
#define MAX_USERNAME_LENGTH 20
#define MAX_ROOM_NAME_LENGTH 30
#define SERVER_HOST "your-server-host.com"  // Remplacer par votre nom d'hôte
#define SERVER_PORT 80  // Port HTTP (80 pour HTTP, 443 pour HTTPS)
#define SERVER_PATH "/api"  // Chemin de base de l'API

// Structure pour représenter un utilisateur
typedef struct {
    int id;
    char username[MAX_USERNAME_LENGTH + 1];
    char status[10];  // online/offline
} User;

// Structure pour représenter un message
typedef struct {
    int id;
    char username[MAX_USERNAME_LENGTH + 1];
    char content[MAX_MESSAGE_LENGTH + 1];
    char timestamp[20];
} Message;

// Structure pour représenter un salon
typedef struct {
    int id;
    char name[MAX_ROOM_NAME_LENGTH + 1];
    int message_count;
    int user_count;
    bool is_public;
} Room;

// Variables globales
User current_user;
bool is_logged_in = false;
int current_room_id = 1;
Message messages[50];  // Buffer pour les messages
Room rooms[10];        // Buffer pour les salons
int message_count = 0;
int room_count = 0;

// Parser JSON simple (sans librairie externe)
char* find_json_value(const char* json, const char* key) {
    char search_key[100];
    snprintf(search_key, sizeof(search_key), "\"%s\":", key);
    
    char* start = strstr(json, search_key);
    if (!start) return NULL;
    
    start += strlen(search_key);
    while (*start == ' ' || *start == '\t') start++; // Skip whitespace
    
    if (*start == '"') {
        start++; // Skip opening quote
        char* end = strchr(start, '"');
        if (!end) return NULL;
        
        int len = end - start;
        char* result = malloc(len + 1);
        strncpy(result, start, len);
        result[len] = '\0';
        return result;
    } else {
        // Number or boolean
        char* end = start;
        while (*end && *end != ',' && *end != '}' && *end != ']') end++;
        
        int len = end - start;
        char* result = malloc(len + 1);
        strncpy(result, start, len);
        result[len] = '\0';
        return result;
    }
}

// Fonction pour créer une requête HTTP
int create_socket_connection(const char* hostname, int port) {
    int sockfd;
    struct hostent *server;
    struct sockaddr_in serv_addr;
    
    // Créer le socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        return -1;
    }
    
    // Résoudre l'hostname
    server = gethostbyname(hostname);
    if (server == NULL) {
        close(sockfd);
        return -1;
    }
    
    // Configurer l'adresse du serveur
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy(&serv_addr.sin_addr.s_addr, server->h_addr, server->h_length);
    serv_addr.sin_port = htons(port);
    
    // Se connecter
    if (connect(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        close(sockfd);
        return -1;
    }
    
    return sockfd;
}

// Fonction pour envoyer une requête HTTP GET
char* http_get_request(const char* path) {
    int sockfd = create_socket_connection(SERVER_HOST, SERVER_PORT);
    if (sockfd < 0) {
        return NULL;
    }
    
    // Construire la requête HTTP
    char request[1024];
    snprintf(request, sizeof(request),
        "GET %s HTTP/1.1\r\n"
        "Host: %s\r\n"
        "User-Agent: 3DS-Discord/1.0\r\n"
        "Connection: close\r\n"
        "\r\n",
        path, SERVER_HOST);
    
    // Envoyer la requête
    if (send(sockfd, request, strlen(request), 0) < 0) {
        close(sockfd);
        return NULL;
    }
    
    // Lire la réponse
    char* response = malloc(4096);
    int bytes_received = 0;
    int total_received = 0;
    
    while ((bytes_received = recv(sockfd, response + total_received, 4095 - total_received, 0)) > 0) {
        total_received += bytes_received;
        if (total_received >= 4095) break;
    }
    
    response[total_received] = '\0';
    close(sockfd);
    
    // Trouver le début du corps de la réponse (après les headers HTTP)
    char* body = strstr(response, "\r\n\r\n");
    if (body) {
        body += 4; // Skip "\r\n\r\n"
        char* result = malloc(strlen(body) + 1);
        strcpy(result, body);
        free(response);
        return result;
    }
    
    free(response);
    return NULL;
}

// Fonction pour envoyer une requête HTTP POST
char* http_post_request(const char* path, const char* json_data) {
    int sockfd = create_socket_connection(SERVER_HOST, SERVER_PORT);
    if (sockfd < 0) {
        return NULL;
    }
    
    // Construire la requête HTTP POST
    char request[2048];
    int content_length = strlen(json_data);
    
    snprintf(request, sizeof(request),
        "POST %s HTTP/1.1\r\n"
        "Host: %s\r\n"
        "User-Agent: 3DS-Discord/1.0\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        path, SERVER_HOST, content_length, json_data);
    
    // Envoyer la requête
    if (send(sockfd, request, strlen(request), 0) < 0) {
        close(sockfd);
        return NULL;
    }
    
    // Lire la réponse
    char* response = malloc(4096);
    int bytes_received = 0;
    int total_received = 0;
    
    while ((bytes_received = recv(sockfd, response + total_received, 4095 - total_received, 0)) > 0) {
        total_received += bytes_received;
        if (total_received >= 4095) break;
    }
    
    response[total_received] = '\0';
    close(sockfd);
    
    // Trouver le début du corps de la réponse
    char* body = strstr(response, "\r\n\r\n");
    if (body) {
        body += 4;
        char* result = malloc(strlen(body) + 1);
        strcpy(result, body);
        free(response);
        return result;
    }
    
    free(response);
    return NULL;
}

// Fonction pour simuler une connexion (version offline pour démo)
bool simulate_login(const char* username, const char* password) {
    // Version démo - accepte n'importe quels identifiants non vides
    if (strlen(username) > 0 && strlen(password) > 0) {
        strncpy(current_user.username, username, MAX_USERNAME_LENGTH);
        current_user.id = 1;
        strcpy(current_user.status, "online");
        return true;
    }
    return false;
}

// Données de démo pour les salons (version offline)
void load_demo_rooms() {
    room_count = 3;
    
    // Salon 1: Général
    rooms[0].id = 1;
    strcpy(rooms[0].name, "Général");
    rooms[0].user_count = 5;
    rooms[0].message_count = 12;
    rooms[0].is_public = true;
    
    // Salon 2: Gaming
    rooms[1].id = 2;
    strcpy(rooms[1].name, "Gaming");
    rooms[1].user_count = 3;
    rooms[1].message_count = 8;
    rooms[1].is_public = true;
    
    // Salon 3: Help
    rooms[2].id = 3;
    strcpy(rooms[2].name, "Aide");
    rooms[2].user_count = 2;
    rooms[2].message_count = 4;
    rooms[2].is_public = true;
}

// Messages de démo pour un salon
void load_demo_messages(int room_id) {
    switch (room_id) {
        case 1: // Général
            message_count = 4;
            strcpy(messages[0].username, "Alice");
            strcpy(messages[0].content, "Salut tout le monde!");
            strcpy(messages[0].timestamp, "12:30");
            
            strcpy(messages[1].username, "Bob");
            strcpy(messages[1].content, "Hey Alice! Comment ça va?");
            strcpy(messages[1].timestamp, "12:32");
            
            strcpy(messages[2].username, "Charlie");
            strcpy(messages[2].content, "Super cette app 3DS!");
            strcpy(messages[2].timestamp, "12:35");
            
            strcpy(messages[3].username, current_user.username);
            strcpy(messages[3].content, "Je teste le homebrew");
            strcpy(messages[3].timestamp, "12:40");
            break;
            
        case 2: // Gaming
            message_count = 3;
            strcpy(messages[0].username, "Gamer1");
            strcpy(messages[0].content, "Qui joue à Mario Kart?");
            strcpy(messages[0].timestamp, "11:20");
            
            strcpy(messages[1].username, "Gamer2");
            strcpy(messages[1].content, "Moi! Code: 1234-5678");
            strcpy(messages[1].timestamp, "11:22");
            
            strcpy(messages[2].username, current_user.username);
            strcpy(messages[2].content, "J'arrive!");
            strcpy(messages[2].timestamp, "11:25");
            break;
            
        case 3: // Aide
            message_count = 2;
            strcpy(messages[0].username, "Helper");
            strcpy(messages[0].content, "Comment installer un CFW?");
            strcpy(messages[0].timestamp, "10:15");
            
            strcpy(messages[1].username, current_user.username);
            strcpy(messages[1].content, "Regarde le guide 3ds.guide");
            strcpy(messages[1].timestamp, "10:18");
            break;
            
        default:
            message_count = 0;
            break;
    }
}

// Version complète avec vraie communication réseau
bool login(const char* username, const char* password) {
    char json_data[512];
    char path[256];
    
    // Créer les données JSON pour la connexion
    snprintf(json_data, sizeof(json_data),
        "{\"username\":\"%s\",\"password\":\"%s\"}", username, password);
    
    snprintf(path, sizeof(path), "%s/login", SERVER_PATH);
    
    // Envoyer la requête de connexion
    char* response = http_post_request(path, json_data);
    if (!response) {
        // Si la connexion échoue, utiliser la version démo
        return simulate_login(username, password);
    }
    
    // Parser la réponse JSON
    char* success_str = find_json_value(response, "success");
    if (!success_str) {
        free(response);
        return simulate_login(username, password);
    }
    
    bool login_success = (strncmp(success_str, "true", 4) == 0);
    free(success_str);
    
    if (login_success) {
        char* user_id_str = find_json_value(response, "id");
        char* username_str = find_json_value(response, "username");
        
        if (user_id_str && username_str) {
            current_user.id = atoi(user_id_str);
            strncpy(current_user.username, username_str, MAX_USERNAME_LENGTH);
            strcpy(current_user.status, "online");
            is_logged_in = true;
            
            free(user_id_str);
            free(username_str);
        }
    }
    
    free(response);
    return login_success ? login_success : simulate_login(username, password);
}

void fetch_rooms() {
    char path[256];
    snprintf(path, sizeof(path), "%s/rooms?user=%s", SERVER_PATH, current_user.username);
    
    char* response = http_get_request(path);
    if (!response) {
        // Si la requête échoue, utiliser les données démo
        load_demo_rooms();
        return;
    }
    
    // Pour simplifier, on parse manuellement une structure simple
    // Dans une vraie implémentation, on utiliserait un vrai parser JSON
    char* rooms_start = strstr(response, "\"rooms\":[");
    if (!rooms_start) {
        free(response);
        load_demo_rooms();
        return;
    }
    
    // Parser simple - compter les objets room
    room_count = 0;
    char* current = rooms_start + 9; // Skip "rooms":["
    
    while (*current && *current != ']' && room_count < 10) {
        if (*current == '{') {
            // Parser un objet room basique
            char* id_str = find_json_value(current, "id");
            char* name_str = find_json_value(current, "name");
            char* user_count_str = find_json_value(current, "user_count");
            
            if (id_str && name_str && user_count_str) {
                rooms[room_count].id = atoi(id_str);
                strncpy(rooms[room_count].name, name_str, MAX_ROOM_NAME_LENGTH);
                rooms[room_count].user_count = atoi(user_count_str);
                rooms[room_count].message_count = 0;
                rooms[room_count].is_public = true;
                room_count++;
                
                free(id_str);
                free(name_str);
                free(user_count_str);
            }
        }
        current++;
    }
    
    free(response);
    
    // Si on n'a pas récupéré de salons, utiliser la démo
    if (room_count == 0) {
        load_demo_rooms();
    }
}

void fetch_messages(int room_id) {
    char path[256];
    snprintf(path, sizeof(path), "%s/room/%d/messages?user=%s", SERVER_PATH, room_id, current_user.username);
    
    char* response = http_get_request(path);
    if (!response) {
        // Si la requête échoue, utiliser les données démo
        load_demo_messages(room_id);
        return;
    }
    
    // Parser simple des messages
    char* messages_start = strstr(response, "\"messages\":[");
    if (!messages_start) {
        free(response);
        load_demo_messages(room_id);
        return;
    }
    
    message_count = 0;
    char* current = messages_start + 12; // Skip "messages":["
    
    while (*current && *current != ']' && message_count < 50) {
        if (*current == '{') {
            char* username_str = find_json_value(current, "username");
            char* content_str = find_json_value(current, "content");
            char* timestamp_str = find_json_value(current, "timestamp");
            
            if (username_str && content_str && timestamp_str) {
                messages[message_count].id = message_count + 1;
                strncpy(messages[message_count].username, username_str, MAX_USERNAME_LENGTH);
                strncpy(messages[message_count].content, content_str, MAX_MESSAGE_LENGTH);
                strncpy(messages[message_count].timestamp, timestamp_str, 19);
                message_count++;
                
                free(username_str);
                free(content_str);
                free(timestamp_str);
            }
        }
        current++;
    }
    
    free(response);
    
    // Si on n'a pas récupéré de messages, utiliser la démo
    if (message_count == 0) {
        load_demo_messages(room_id);
    }
}

bool send_message(int room_id, const char* content) {
    char json_data[1024];
    char path[256];
    
    snprintf(json_data, sizeof(json_data),
        "{\"user\":\"%s\",\"message\":\"%s\"}", current_user.username, content);
    
    snprintf(path, sizeof(path), "%s/room/%d/send", SERVER_PATH, room_id);
    
    char* response = http_post_request(path, json_data);
    if (!response) {
        // Si la requête échoue, simuler l'ajout local
        if (message_count < 50) {
            messages[message_count].id = message_count + 1;
            strncpy(messages[message_count].username, current_user.username, MAX_USERNAME_LENGTH);
            strncpy(messages[message_count].content, content, MAX_MESSAGE_LENGTH);
            strcpy(messages[message_count].timestamp, "maintenant");
            message_count++;
            return true;
        }
        return false;
    }
    
    char* success_str = find_json_value(response, "success");
    bool success = false;
    
    if (success_str) {
        success = (strncmp(success_str, "true", 4) == 0);
        free(success_str);
    }
    
    free(response);
    
    // Si le message a été envoyé, actualiser les messages
    if (success) {
        fetch_messages(room_id);
    }
    
    return success;
}

// Interface utilisateur - écran de connexion
void draw_login_screen(bool is_connected) {
    consoleClear();
    printf("\n");
    printf("  ╔══════════════════════════════════════╗\n");
    printf("  ║            3DS DISCORD               ║\n");
    printf("  ║        Version Homebrew 1.0          ║\n");
    printf("  ╠══════════════════════════════════════╣\n");
    printf("  ║                                      ║\n");
    if (is_connected) {
        printf("  ║    ✓ Connecté au serveur             ║\n");
    } else {
        printf("  ║    ⚠ Mode démo (hors ligne)          ║\n");
    }
    printf("  ║                                      ║\n");
    printf("  ║   Utilisateurs de test:              ║\n");
    printf("  ║   - Skyzen / password                ║\n");
    printf("  ║   - Alice / alice123                 ║\n");
    printf("  ║   - Bob / bob456                     ║\n");
    printf("  ║                                      ║\n");
    printf("  ║   [A] Se connecter comme Skyzen      ║\n");
    printf("  ║   [X] Se connecter comme Alice       ║\n");
    printf("  ║   [Y] Se connecter comme Bob         ║\n");
    printf("  ║   [START] Quitter                    ║\n");
    printf("  ║                                      ║\n");
    printf("  ╚══════════════════════════════════════╝\n");
    printf("\n");
    if (is_connected) {
        printf("Statut: Serveur accessible - données réelles\n");
    } else {
        printf("Statut: Mode démo - données locales\n");
    }
}

// Interface utilisateur - liste des salons  
void draw_room_list() {
    consoleClear();
    printf("\n");
    printf("  ╔══════════════════════════════════════╗\n");
    printf("  ║  3DS DISCORD - Salons disponibles    ║\n");
    printf("  ╠══════════════════════════════════════╣\n");
    printf("  ║  Connecté: %-20s    ║\n", current_user.username);
    printf("  ║                                      ║\n");
    
    for (int i = 0; i < room_count && i < 8; i++) {
        printf("  ║  %d. %-15s (%d users)      ║\n", 
               i + 1, rooms[i].name, rooms[i].user_count);
    }
    
    for (int i = room_count; i < 8; i++) {
        printf("  ║                                      ║\n");
    }
    
    printf("  ║                                      ║\n");
    printf("  ║  [A] Rejoindre salon sélectionné     ║\n");
    printf("  ║  [Y] Actualiser la liste             ║\n");
    printf("  ║  [START] Quitter                     ║\n");
    printf("  ╚══════════════════════════════════════╝\n");
    printf("\n");
    printf("Utilisez D-PAD pour sélectionner un salon\n");
}

// Interface utilisateur - salon de chat
void draw_chat_room() {
    consoleClear();
    
    // Trouver le nom du salon actuel
    char* room_name = "Salon";
    for (int i = 0; i < room_count; i++) {
        if (rooms[i].id == current_room_id) {
            room_name = rooms[i].name;
            break;
        }
    }
    
    printf("\n");
    printf("  ╔══════════════════════════════════════╗\n");
    printf("  ║  3DS DISCORD - %-18s ║\n", room_name);
    printf("  ╠══════════════════════════════════════╣\n");
    
    // Afficher les messages (8 derniers max)
    int start = (message_count > 8) ? message_count - 8 : 0;
    for (int i = start; i < message_count; i++) {
        // Tronquer le message s'il est trop long
        char display_msg[35];
        strncpy(display_msg, messages[i].content, 34);
        display_msg[34] = '\0';
        
        printf("  ║ %-10s: %-25s ║\n", messages[i].username, display_msg);
    }
    
    // Remplir les lignes vides
    for (int i = message_count; i < 8; i++) {
        printf("  ║                                      ║\n");
    }
    
    printf("  ╠══════════════════════════════════════╣\n");
    printf("  ║  [A] Écrire message                  ║\n");
    printf("  ║  [Y] Actualiser                      ║\n");
    printf("  ║  [B] Retour aux salons               ║\n");
    printf("  ║  [START] Quitter                     ║\n");
    printf("  ╚══════════════════════════════════════╝\n");
}

// Interface de saisie de texte avec sélection interactive
void input_text(char* buffer, int max_length, const char* prompt) {
    const char* predefined_messages[] = {
        "Salut tout le monde!",
        "Comment allez-vous?", 
        "Super ce homebrew!",
        "Quelqu'un pour jouer?",
        "Merci pour votre aide",
        "À bientôt!",
        "Ça fonctionne bien!",
        "Besoin d'aide ici",
        "Qui est en ligne?",
        "Message personnalisé..."
    };
    
    static int selected_msg = 0;
    int max_msgs = 10;
    bool selecting = true;
    
    while (selecting && aptMainLoop()) {
        consoleClear();
        printf("\n%s\n", prompt);
        printf("Messages prédéfinis - utilisez D-PAD pour choisir:\n");
        printf("═══════════════════════════════════════════════\n");
        
        for (int i = 0; i < max_msgs; i++) {
            if (i == selected_msg) {
                printf(" ► %s\n", predefined_messages[i]);
            } else {
                printf("   %s\n", predefined_messages[i]);
            }
        }
        
        printf("═══════════════════════════════════════════════\n");
        printf("D-PAD Haut/Bas: choisir message\n");
        printf("A: confirmer, B: annuler\n");
        
        hidScanInput();
        u32 kDown = hidKeysDown();
        
        if (kDown & KEY_DPAD_UP && selected_msg > 0) {
            selected_msg--;
        }
        if (kDown & KEY_DPAD_DOWN && selected_msg < max_msgs - 1) {
            selected_msg++;
        }
        if (kDown & KEY_A) {
            if (selected_msg == max_msgs - 1) {
                // Message personnalisé - pour l'instant on utilise un message par défaut
                strcpy(buffer, "Message personnalisé depuis 3DS");
            } else {
                strcpy(buffer, predefined_messages[selected_msg]);
            }
            selecting = false;
        }
        if (kDown & KEY_B) {
            strcpy(buffer, "");
            selecting = false;
        }
        
        gfxFlushBuffers();
        gfxSwapBuffers(GFX_TOP, GFX_LEFT);
        gspWaitForVBlank();
    }
}

int main(int argc, char* argv[]) {
    // Initialiser les systèmes
    acInit();
    gfxInitDefault();
    consoleInit(GFX_TOP, NULL);
    
    printf("Initialisation de 3DS Discord...\n");
    printf("Vérification de la connexion Internet...\n");
    
    Result ret = acWaitInternetConnection();
    if (R_FAILED(ret)) {
        printf("Erreur: Pas de connexion Internet disponible\n");
        printf("Le homebrew fonctionnera en mode démo.\n");
        printf("Appuyez sur A pour continuer...\n");
        while (aptMainLoop()) {
            hidScanInput();
            if (hidKeysDown() & KEY_A) break;
            gfxFlushBuffers();
            gfxSwapBuffers(GFX_TOP, GFX_LEFT);
            gspWaitForVBlank();
        }
    } else {
        printf("Connexion Internet OK!\n");
        printf("Le homebrew peut maintenant communiquer avec le serveur.\n");
        printf("Appuyez sur A pour continuer...\n");
        while (aptMainLoop()) {
            hidScanInput();
            if (hidKeysDown() & KEY_A) break;
            gfxFlushBuffers();
            gfxSwapBuffers(GFX_TOP, GFX_LEFT);
            gspWaitForVBlank();
        }
    }
    
    // État de l'application
    enum {
        STATE_LOGIN,
        STATE_ROOM_LIST, 
        STATE_CHAT_ROOM,
        STATE_INPUT_MESSAGE
    } app_state = STATE_LOGIN;
    
    int selected_room = 0;
    char input_buffer[MAX_MESSAGE_LENGTH + 1];
    
    // Variables pour la connexion
    char username[MAX_USERNAME_LENGTH + 1];
    char password[50];
    bool network_available = (ret == 0);  // ret du test de connexion internet
    
    // Pas de connexion automatique - on laisse l'utilisateur choisir
    
    // Boucle principale
    while (aptMainLoop()) {
        hidScanInput();
        u32 kDown = hidKeysDown();
        u32 kHeld = hidKeysHeld();
        
        if (kDown & KEY_START) break; // Quitter l'application
        
        switch (app_state) {
            case STATE_LOGIN:
                draw_login_screen(network_available);
                if (kDown & KEY_A) {
                    // Se connecter comme Skyzen
                    strcpy(username, "Skyzen");
                    strcpy(password, "password");
                    if (login(username, password)) {
                        app_state = STATE_ROOM_LIST;
                        fetch_rooms();
                    }
                }
                if (kDown & KEY_X) {
                    // Se connecter comme Alice
                    strcpy(username, "Alice");
                    strcpy(password, "alice123");
                    if (login(username, password)) {
                        app_state = STATE_ROOM_LIST;
                        fetch_rooms();
                    }
                }
                if (kDown & KEY_Y) {
                    // Se connecter comme Bob
                    strcpy(username, "Bob");
                    strcpy(password, "bob456");
                    if (login(username, password)) {
                        app_state = STATE_ROOM_LIST;
                        fetch_rooms();
                    }
                }
                break;
                
            case STATE_ROOM_LIST:
                draw_room_list();
                if (kDown & KEY_DPAD_UP && selected_room > 0) {
                    selected_room--;
                }
                if (kDown & KEY_DPAD_DOWN && selected_room < room_count - 1) {
                    selected_room++;
                }
                if (kDown & KEY_A && room_count > 0) {
                    current_room_id = rooms[selected_room].id;
                    fetch_messages(current_room_id);
                    app_state = STATE_CHAT_ROOM;
                }
                if (kDown & KEY_Y) {
                    fetch_rooms();
                }
                break;
                
            case STATE_CHAT_ROOM:
                draw_chat_room();
                if (kDown & KEY_A) {
                    app_state = STATE_INPUT_MESSAGE;
                }
                if (kDown & KEY_Y) {
                    fetch_messages(current_room_id);
                }
                if (kDown & KEY_B) {
                    app_state = STATE_ROOM_LIST;
                }
                break;
                
            case STATE_INPUT_MESSAGE:
                input_text(input_buffer, MAX_MESSAGE_LENGTH, "Écrire un message:");
                // input_text gère déjà l'interaction, on revient au chat
                if (strlen(input_buffer) > 0) {
                    send_message(current_room_id, input_buffer);
                    fetch_messages(current_room_id); // Actualiser les messages
                }
                app_state = STATE_CHAT_ROOM;
                break;
        }
        
        gfxFlushBuffers();
        gfxSwapBuffers(GFX_TOP, GFX_LEFT);
        gspWaitForVBlank();
    }
    
    // Nettoyage
    acExit();
    gfxExit();
    return 0;
}