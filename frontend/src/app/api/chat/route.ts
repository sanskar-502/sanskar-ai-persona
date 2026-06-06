import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    
    // In production, point this to your Railway/deployed backend URL
    // e.g., const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const backendUrl = "http://localhost:8000";
    
    const response = await fetch(`${backendUrl}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend responded with ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: "Failed to communicate with AI Persona Backend." },
      { status: 500 }
    );
  }
}
