import { type NextRequest, NextResponse } from "next/server"

const TEAM_SERVER_URL = process.env.TEAM_SERVER_URL || "http://localhost:8080"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const response = await fetch(`${TEAM_SERVER_URL}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      return NextResponse.json({ error: "Authentication failed" }, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Login proxy error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
