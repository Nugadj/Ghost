import { type NextRequest, NextResponse } from "next/server"

const TEAM_SERVER_URL = process.env.TEAM_SERVER_URL || "http://localhost:8080"

async function proxyToTeamServer(endpoint: string, options: RequestInit = {}) {
  try {
    const response = await fetch(`${TEAM_SERVER_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`Team Server request failed: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`[v0] Team Server proxy error:`, error)
    throw error
  }
}

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("authorization")
    const data = await proxyToTeamServer("/api/listeners/", {
      method: "GET",
      headers: authHeader ? { Authorization: authHeader } : {},
    })

    return NextResponse.json({
      success: true,
      listeners: data,
    })
  } catch (error) {
    console.error("[v0] Error fetching listeners:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Failed to fetch listeners from Team Server",
      },
      { status: 500 },
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const authHeader = request.headers.get("authorization")

    console.log(`[v0] Creating new listener:`, body)

    const data = await proxyToTeamServer("/api/listeners/", {
      method: "POST",
      headers: authHeader ? { Authorization: authHeader } : {},
      body: JSON.stringify({
        name: body.name,
        type: body.protocol?.toLowerCase() || body.type || "http",
        host: body.host || "0.0.0.0",
        port: body.port || 8080,
        config: body.config || {},
      }),
    })

    return NextResponse.json({
      success: true,
      listener: data,
    })
  } catch (error) {
    console.error("[v0] Error creating listener:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Failed to create listener",
      },
      { status: 500 },
    )
  }
}
