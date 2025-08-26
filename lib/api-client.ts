class GhostProtocolAPI {
  private baseUrl: string
  private wsUrl: string
  private accessToken: string | null = null
  private websocket: WebSocket | null = null
  private eventHandlers: Map<string, Function[]> = new Map()

  constructor(serverHost = "localhost", serverPort = 8080) {
    this.baseUrl = `http://${serverHost}:${serverPort}`
    this.wsUrl = `ws://${serverHost}:${serverPort}`
  }

  async authenticate(username: string, password: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      })

      if (response.ok) {
        const data = await response.json()
        this.accessToken = data.access_token
        await this.connectWebSocket(username)
        return true
      }
      return false
    } catch (error) {
      console.error("Authentication failed:", error)
      return false
    }
  }

  private async connectWebSocket(username: string): Promise<void> {
    try {
      this.websocket = new WebSocket(`${this.wsUrl}/ws/client_${username}`)

      this.websocket.onopen = () => {
        console.log("WebSocket connected to Ghost Protocol Team Server")
      }

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleWebSocketMessage(data)
      }

      this.websocket.onclose = () => {
        console.log("WebSocket disconnected")
        // Attempt reconnection
        setTimeout(() => this.connectWebSocket(username), 5000)
      }
    } catch (error) {
      console.error("WebSocket connection failed:", error)
    }
  }

  private handleWebSocketMessage(data: any): void {
    const { event_type, payload } = data
    const handlers = this.eventHandlers.get(event_type) || []
    handlers.forEach((handler) => handler(payload))
  }

  on(eventType: string, handler: Function): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, [])
    }
    this.eventHandlers.get(eventType)!.push(handler)
  }

  private async apiRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const headers = {
      "Content-Type": "application/json",
      ...(this.accessToken && { Authorization: `Bearer ${this.accessToken}` }),
      ...options.headers,
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`)
    }

    return response.json()
  }

  // Beacon Management
  async getBeacons(): Promise<any[]> {
    return this.apiRequest("/api/beacons/")
  }

  async getBeacon(beaconId: string): Promise<any> {
    return this.apiRequest(`/api/beacons/${beaconId}`)
  }

  async createBeaconTask(beaconId: string, command: string, args: any = {}): Promise<any> {
    return this.apiRequest(`/api/beacons/${beaconId}/tasks`, {
      method: "POST",
      body: JSON.stringify({ command, arguments: args }),
    })
  }

  async terminateBeacon(beaconId: string): Promise<any> {
    return this.apiRequest(`/api/beacons/${beaconId}`, { method: "DELETE" })
  }

  // Listener Management
  async getListeners(): Promise<any[]> {
    return this.apiRequest("/api/listeners/")
  }

  async createListener(config: any): Promise<any> {
    return this.apiRequest("/api/listeners/", {
      method: "POST",
      body: JSON.stringify(config),
    })
  }

  async startListener(listenerId: string): Promise<any> {
    return this.apiRequest(`/api/listeners/${listenerId}/start`, { method: "POST" })
  }

  async stopListener(listenerId: string): Promise<any> {
    return this.apiRequest(`/api/listeners/${listenerId}/stop`, { method: "POST" })
  }

  async deleteListener(listenerId: string): Promise<any> {
    return this.apiRequest(`/api/listeners/${listenerId}`, { method: "DELETE" })
  }

  // Module Management
  async getModules(): Promise<any[]> {
    return this.apiRequest("/api/modules/")
  }

  async executeModule(module: string, command: string, args: any = {}): Promise<any> {
    return this.apiRequest("/api/modules/execute", {
      method: "POST",
      body: JSON.stringify({ module, command, args }),
    })
  }

  // Operation Management
  async getOperations(): Promise<any[]> {
    return this.apiRequest("/api/operations/")
  }

  async createOperation(name: string, description = ""): Promise<any> {
    return this.apiRequest("/api/operations/", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    })
  }

  async deleteOperation(operationId: string): Promise<any> {
    return this.apiRequest(`/api/operations/${operationId}`, { method: "DELETE" })
  }

  async getCurrentUser(): Promise<any> {
    return this.apiRequest("/api/auth/me")
  }

  async logout(): Promise<void> {
    try {
      await this.apiRequest("/api/auth/logout", { method: "POST" })
    } catch (error) {
      console.error("Logout failed:", error)
    } finally {
      this.disconnect()
    }
  }

  disconnect(): void {
    if (this.websocket) {
      this.websocket.close()
      this.websocket = null
    }
    this.accessToken = null
  }
}

export const ghostAPI = new GhostProtocolAPI()
export default ghostAPI
