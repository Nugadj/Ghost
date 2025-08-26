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
    const data = await proxyToTeamServer("/api/beacons/", {
      method: "GET",
      headers: authHeader ? { Authorization: authHeader } : {},
    })

    return NextResponse.json({
      success: true,
      beacons: data,
    })
  } catch (error) {
    console.error("[v0] Error fetching beacons:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Failed to fetch beacons from Team Server",
      },
      { status: 500 },
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const authHeader = request.headers.get("authorization")

    if (body.action === "create_task" && body.beacon_id) {
      // Create task for specific beacon
      const data = await proxyToTeamServer(`/api/beacons/${body.beacon_id}/tasks`, {
        method: "POST",
        headers: authHeader ? { Authorization: authHeader } : {},
        body: JSON.stringify({
          command: body.command,
          arguments: body.arguments || {},
        }),
      })

      return NextResponse.json({
        success: true,
        task: data,
      })
    } else if (body.beacon_id && body.system_info) {
      // Handle beacon check-in from actual beacon (not web interface)
      console.log(`[v0] Beacon check-in received from ${body.beacon_id}`)

      // This would be handled by the Python Team Server directly
      // Web interface doesn't need to handle beacon check-ins
      return NextResponse.json({
        success: true,
        message: "Beacon check-in should be handled by Team Server directly",
      })
    }

    return NextResponse.json({
      success: false,
      error: "Invalid request format",
    })
  } catch (error) {
    console.error("[v0] Error handling beacon request:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Internal server error",
      },
      { status: 500 },
    )
  }
}
