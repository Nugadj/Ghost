import { type NextRequest, NextResponse } from "next/server"

const TEAM_SERVER_URL = process.env.TEAM_SERVER_URL || "http://localhost:8080"

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("authorization")

    if (!authHeader) {
      return NextResponse.json({ error: "Authorization header required" }, { status: 401 })
    }

    const response = await fetch(`${TEAM_SERVER_URL}/api/auth/me`, {
      method: "GET",
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      return NextResponse.json({ error: "Failed to get user info" }, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("User info proxy error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
