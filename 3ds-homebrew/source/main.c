#include <3ds.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <json-c/json.h>

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

// Structure pour la réponse HTTP
struct HTTPResponse {
    char *data;
    size_t size;
};

// Callback pour écrire les données reçues
static size_t WriteCallback(void *contents, size_t size, size_t nmemb, struct HTTPResponse *response) {
    size_t total_size = size * nmemb;
    response->data = realloc(response->data, response->size + total_size + 1);
    if (response->data) {
        memcpy(&(response->data[response->size]), contents, total_size);
        response->size += total_size;
        response->data[response->size] = 0;  // Null terminer
    }
    return total_size;
}

// Fonction pour faire une requête HTTP GET
char* http_get(const char* url) {
    CURL *curl;
    CURLcode res;
    struct HTTPResponse response = {0};
    
    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);  // Timeout 10 secondes
        
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);
        
        if (res != CURLE_OK) {
            if (response.data) {
                free(response.data);
            }
            return NULL;
        }
    }
    
    return response.data;
}

// Fonction pour faire une requête HTTP POST
char* http_post(const char* url, const char* data) {
    CURL *curl;
    CURLcode res;
    struct HTTPResponse response = {0};
    struct curl_slist *headers = NULL;
    
    curl = curl_easy_init();
    if (curl) {
        headers = curl_slist_append(headers, "Content-Type: application/json");
        
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
        
        res = curl_easy_perform(curl);
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        
        if (res != CURLE_OK) {
            if (response.data) {
                free(response.data);
            }
            return NULL;
        }
    }
    
    return response.data;
}

// Fonction pour se connecter au serveur
bool login(const char* username, const char* password) {
    char url[256];
    char post_data[512];
    char* response;
    
    snprintf(url, sizeof(url), "%s/api/login", SERVER_URL);
    snprintf(post_data, sizeof(post_data), 
             "{\"username\":\"%s\",\"password\":\"%s\"}", 
             username, password);
    
    response = http_post(url, post_data);
    if (!response) {
        return false;
    }
    
    // Parser la réponse JSON
    json_object *root = json_tokener_parse(response);
    json_object *success_obj, *user_obj, *id_obj, *username_obj;
    
    bool login_success = false;
    if (json_object_object_get_ex(root, "success", &success_obj)) {
        if (json_object_get_boolean(success_obj)) {
            if (json_object_object_get_ex(root, "user", &user_obj)) {
                json_object_object_get_ex(user_obj, "id", &id_obj);
                json_object_object_get_ex(user_obj, "username", &username_obj);
                
                current_user.id = json_object_get_int(id_obj);
                strncpy(current_user.username, json_object_get_string(username_obj), MAX_USERNAME_LENGTH);
                strcpy(current_user.status, "online");
                
                is_logged_in = true;
                login_success = true;
            }
        }
    }
    
    json_object_put(root);
    free(response);
    return login_success;
}

// Fonction pour récupérer les salons
void fetch_rooms() {
    char url[256];
    char* response;
    
    snprintf(url, sizeof(url), "%s/api/rooms?user=%s", SERVER_URL, current_user.username);
    response = http_get(url);
    
    if (!response) {
        return;
    }
    
    // Parser la réponse JSON
    json_object *root = json_tokener_parse(response);
    json_object *rooms_array;
    
    if (json_object_object_get_ex(root, "rooms", &rooms_array)) {
        int array_length = json_object_array_length(rooms_array);
        room_count = (array_length > 10) ? 10 : array_length;
        
        for (int i = 0; i < room_count; i++) {
            json_object *room_obj = json_object_array_get_idx(rooms_array, i);
            json_object *id_obj, *name_obj, *user_count_obj, *message_count_obj, *is_public_obj;
            
            json_object_object_get_ex(room_obj, "id", &id_obj);
            json_object_object_get_ex(room_obj, "name", &name_obj);
            json_object_object_get_ex(room_obj, "user_count", &user_count_obj);
            json_object_object_get_ex(room_obj, "message_count", &message_count_obj);
            json_object_object_get_ex(room_obj, "is_public", &is_public_obj);
            
            rooms[i].id = json_object_get_int(id_obj);
            strncpy(rooms[i].name, json_object_get_string(name_obj), MAX_ROOM_NAME_LENGTH);
            rooms[i].user_count = json_object_get_int(user_count_obj);
            rooms[i].message_count = json_object_get_int(message_count_obj);
            rooms[i].is_public = json_object_get_boolean(is_public_obj);
        }
    }
    
    json_object_put(root);
    free(response);
}

// Fonction pour récupérer les messages d'un salon
void fetch_messages(int room_id) {
    char url[256];
    char* response;
    
    snprintf(url, sizeof(url), "%s/api/room/%d/messages?user=%s", SERVER_URL, room_id, current_user.username);
    response = http_get(url);
    
    if (!response) {
        return;
    }
    
    // Parser la réponse JSON
    json_object *root = json_tokener_parse(response);
    json_object *messages_array;
    
    if (json_object_object_get_ex(root, "messages", &messages_array)) {
        int array_length = json_object_array_length(messages_array);
        message_count = (array_length > 50) ? 50 : array_length;
        
        for (int i = 0; i < message_count; i++) {
            json_object *msg_obj = json_object_array_get_idx(messages_array, i);
            json_object *id_obj, *username_obj, *content_obj, *timestamp_obj;
            
            json_object_object_get_ex(msg_obj, "id", &id_obj);
            json_object_object_get_ex(msg_obj, "username", &username_obj);
            json_object_object_get_ex(msg_obj, "content", &content_obj);
            json_object_object_get_ex(msg_obj, "timestamp", &timestamp_obj);
            
            messages[i].id = json_object_get_int(id_obj);
            strncpy(messages[i].username, json_object_get_string(username_obj), MAX_USERNAME_LENGTH);
            strncpy(messages[i].content, json_object_get_string(content_obj), MAX_MESSAGE_LENGTH);
            strncpy(messages[i].timestamp, json_object_get_string(timestamp_obj), 19);
        }
    }
    
    json_object_put(root);
    free(response);
}

// Fonction pour envoyer un message
bool send_message(int room_id, const char* content) {
    char url[256];
    char post_data[1024];
    char* response;
    
    snprintf(url, sizeof(url), "%s/api/room/%d/send", SERVER_URL, room_id);
    snprintf(post_data, sizeof(post_data), 
             "{\"user\":\"%s\",\"message\":\"%s\"}", 
             current_user.username, content);
    
    response = http_post(url, post_data);
    if (!response) {
        return false;
    }
    
    // Vérifier le succès
    json_object *root = json_tokener_parse(response);
    json_object *success_obj;
    bool success = false;
    
    if (json_object_object_get_ex(root, "success", &success_obj)) {
        success = json_object_get_boolean(success_obj);
    }
    
    json_object_put(root);
    free(response);
    return success;
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
    printf("Tapez votre texte puis appuyez sur START:\n");
    printf("> ");
    
    // Simulation d'entrée de texte (dans un vrai homebrew 3DS, 
    // il faudrait utiliser le clavier virtuel ou capturer les touches)
    // Pour cet exemple, on utilise une entrée prédéfinie
    strcpy(buffer, "Message par défaut");
    printf("%s\n", buffer);
    printf("\nAppuyez sur A pour continuer...");
}

int main(int argc, char* argv[]) {
    gfxInitDefault();
    consoleInit(GFX_TOP, NULL);
    
    curl_global_init(CURL_GLOBAL_DEFAULT);
    
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
    
    curl_global_cleanup();
    gfxExit();
    return 0;
}