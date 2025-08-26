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

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const authHeader = request.headers.get("authorization")
    const data = await proxyToTeamServer(`/api/beacons/${params.id}`, {
      method: "GET",
      headers: authHeader ? { Authorization: authHeader } : {},
    })

    return NextResponse.json({
      success: true,
      beacon: data,
    })
  } catch (error) {
    console.error("[v0] Error fetching beacon:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Failed to fetch beacon details",
      },
      { status: 500 },
    )
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const authHeader = request.headers.get("authorization")
    await proxyToTeamServer(`/api/beacons/${params.id}`, {
      method: "DELETE",
      headers: authHeader ? { Authorization: authHeader } : {},
    })

    return NextResponse.json({
      success: true,
      message: "Beacon terminated successfully",
    })
  } catch (error) {
    console.error("[v0] Error terminating beacon:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Failed to terminate beacon",
      },
      { status: 500 },
    )
  }
}
