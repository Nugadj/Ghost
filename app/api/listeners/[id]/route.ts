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

export async function POST(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const body = await request.json()
    const authHeader = request.headers.get("authorization")
    const { action } = body

    if (action === "start") {
      // Start listener
      await proxyToTeamServer(`/api/listeners/${params.id}/start`, {
        method: "POST",
        headers: authHeader ? { Authorization: authHeader } : {},
      })

      return NextResponse.json({
        success: true,
        message: "Listener started successfully",
      })
    } else if (action === "stop") {
      // Stop listener
      await proxyToTeamServer(`/api/listeners/${params.id}/stop`, {
        method: "POST",
        headers: authHeader ? { Authorization: authHeader } : {},
      })

      return NextResponse.json({
        success: true,
        message: "Listener stopped successfully",
      })
    }

    return NextResponse.json({
      success: false,
      error: "Invalid action",
    })
  } catch (error) {
    console.error("[v0] Error managing listener:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Failed to manage listener",
      },
      { status: 500 },
    )
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const authHeader = request.headers.get("authorization")
    await proxyToTeamServer(`/api/listeners/${params.id}`, {
      method: "DELETE",
      headers: authHeader ? { Authorization: authHeader } : {},
    })

    return NextResponse.json({
      success: true,
      message: "Listener deleted successfully",
    })
  } catch (error) {
    console.error("[v0] Error deleting listener:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Failed to delete listener",
      },
      { status: 500 },
    )
  }
}
