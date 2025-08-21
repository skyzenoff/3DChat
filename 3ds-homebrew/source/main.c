#include <3ds.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_MESSAGE_LENGTH 500
#define MAX_USERNAME_LENGTH 20
#define MAX_ROOM_NAME_LENGTH 30
#define SERVER_URL "http://your-server-url.com"  // Remplacer par votre URL de serveur

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

// Version simplifiée pour la démo (pas de réseau)
bool login(const char* username, const char* password) {
    return simulate_login(username, password);
}

void fetch_rooms() {
    load_demo_rooms();
}

void fetch_messages(int room_id) {
    load_demo_messages(room_id);
}

bool send_message(int room_id, const char* content) {
    // Simuler l'ajout d'un message
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

// Interface utilisateur - écran de connexion
void draw_login_screen() {
    consoleClear();
    printf("\n");
    printf("  ╔══════════════════════════════════════╗\n");
    printf("  ║            3DS DISCORD               ║\n");
    printf("  ║        Version Homebrew 1.0          ║\n");
    printf("  ╠══════════════════════════════════════╣\n");
    printf("  ║                                      ║\n");
    printf("  ║      Connexion au serveur...         ║\n");
    printf("  ║                                      ║\n");
    printf("  ║   Nom d'utilisateur:                 ║\n");
    printf("  ║   > ____________________             ║\n");
    printf("  ║                                      ║\n");
    printf("  ║   Mot de passe:                      ║\n");
    printf("  ║   > ____________________             ║\n");
    printf("  ║                                      ║\n");
    printf("  ║   [A] Se connecter                   ║\n");
    printf("  ║   [START] Quitter                    ║\n");
    printf("  ║                                      ║\n");
    printf("  ╚══════════════════════════════════════╝\n");
    printf("\n");
    printf("Statut: En attente de connexion...\n");
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

// Interface de saisie de texte simple
void input_text(char* buffer, int max_length, const char* prompt) {
    consoleClear();
    printf("\n%s\n", prompt);
    printf("Messages prédéfinis - utilisez D-PAD pour choisir:\n");
    printf("\n");
    
    const char* predefined_messages[] = {
        "Salut tout le monde!",
        "Comment allez-vous?", 
        "Super ce homebrew!",
        "Quelqu'un pour jouer?",
        "Merci pour votre aide",
        "À bientôt!"
    };
    
    static int selected_msg = 0;
    int max_msgs = 6;
    
    printf("Sélectionnez votre message:\n");
    for (int i = 0; i < max_msgs; i++) {
        if (i == selected_msg) {
            printf(" > %s\n", predefined_messages[i]);
        } else {
            printf("   %s\n", predefined_messages[i]);
        }
    }
    
    printf("\nD-PAD: choisir, A: envoyer, B: annuler\n");
    
    // Dans une version complète, on gérerait la sélection ici
    // Pour la démo, on prend le message sélectionné
    strcpy(buffer, predefined_messages[selected_msg]);
}

int main(int argc, char* argv[]) {
    gfxInitDefault();
    consoleInit(GFX_TOP, NULL);
    
    // Initialisation système
    
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
    char username[MAX_USERNAME_LENGTH + 1] = "TestUser";
    char password[50] = "password123";
    
    // Tentative de connexion automatique pour la démo
    if (login(username, password)) {
        app_state = STATE_ROOM_LIST;
        fetch_rooms();
    }
    
    // Boucle principale
    while (aptMainLoop()) {
        hidScanInput();
        u32 kDown = hidKeysDown();
        u32 kHeld = hidKeysHeld();
        
        if (kDown & KEY_START) break; // Quitter l'application
        
        switch (app_state) {
            case STATE_LOGIN:
                draw_login_screen();
                if (kDown & KEY_A) {
                    // Tentative de connexion
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
                if (kDown & KEY_A) {
                    if (strlen(input_buffer) > 0) {
                        send_message(current_room_id, input_buffer);
                        fetch_messages(current_room_id); // Actualiser les messages
                    }
                    app_state = STATE_CHAT_ROOM;
                }
                if (kDown & KEY_B) {
                    app_state = STATE_CHAT_ROOM;
                }
                break;
        }
        
        gfxFlushBuffers();
        gfxSwapBuffers(GFX_TOP, GFX_LEFT);
        gspWaitForVBlank();
    }
    
    // Nettoyage
    gfxExit();
    return 0;
}