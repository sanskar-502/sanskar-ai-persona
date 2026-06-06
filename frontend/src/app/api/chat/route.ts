import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    
    // Use environment variable if set, otherwise default to deployed Railway backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "https://sanskar-ai-persona-production.up.railway.app";
    
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
