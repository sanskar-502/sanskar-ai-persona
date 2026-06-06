"use client";

import React, { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

// Simple markdown-ish renderer (bold, code, lists, links)
function renderMarkdown(text: string) {
  // Split by lines for list handling
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let listItems: string[] = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`} className="my-2 space-y-1">
          {listItems.map((item, i) => (
            <li key={i} className="flex gap-2 items-start">
              <span className="text-purple-400 mt-0.5 flex-shrink-0">•</span>
              <span dangerouslySetInnerHTML={{ __html: inlineFormat(item) }} />
            </li>
          ))}
        </ul>
      );
      listItems = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const bulletMatch = line.match(/^[\*\-]\s+(.+)/);

    if (bulletMatch) {
      listItems.push(bulletMatch[1]);
    } else {
      flushList();
      if (line.trim() === "") {
        continue;
      }
      elements.push(
        <p key={`p-${i}`} className="mb-2 last:mb-0" dangerouslySetInnerHTML={{ __html: inlineFormat(line) }} />
      );
    }
  }
  flushList();
  return elements;
}

function inlineFormat(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong class="text-purple-300 font-semibold">$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener" class="text-indigo-400 underline underline-offset-2 hover:text-indigo-300">$1</a>');
}

const QUICK_ACTIONS = [
  "Why hire Sanskar?",
  "Tell me about VartaSync",
  "Check calendar availability",
  "What's your tech stack?",
];

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm the AI persona of **Sanskar Dubey**. I can answer questions about my background, deep-dive into projects like **VartaSync** or **PolicyMind**, or check my calendar to schedule an interview. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!response.ok) throw new Error("Failed to get response");

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I'm experiencing a temporary connection issue. Please try again in a moment — my backend auto-retries on API spikes.",
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="flex flex-col h-full glass-panel rounded-2xl overflow-hidden">
      {/* ── Header ── */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-lg shadow-purple-500/20">
            SD
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white/90 leading-tight">Sanskar Dubey</h2>
            <span className="text-[11px] text-white/35">AI Persona · Online</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-white/20 bg-white/5 px-2.5 py-1 rounded-full">
            Gemini + RAG
          </span>
        </div>
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto chat-messages px-5 py-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex fade-in ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "assistant" && (
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500/30 to-purple-600/30 flex items-center justify-center text-[9px] text-purple-300 font-bold flex-shrink-0 mt-1 mr-2.5">
                AI
              </div>
            )}
            <div
              className={`max-w-[85%] px-4 py-3 text-[13.5px] leading-relaxed ${
                msg.role === "user" ? "msg-user" : "msg-assistant"
              }`}
            >
              {msg.role === "assistant" ? renderMarkdown(msg.content) : msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start fade-in">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500/30 to-purple-600/30 flex items-center justify-center text-[9px] text-purple-300 font-bold flex-shrink-0 mt-1 mr-2.5">
              AI
            </div>
            <div className="msg-assistant px-4 py-3.5 flex items-center gap-1.5">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* ── Quick actions ── */}
      {messages.length <= 1 && !isLoading && (
        <div className="px-5 pb-2 flex flex-wrap gap-2 fade-in">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action}
              onClick={() => sendMessage(action)}
              className="chip"
            >
              {action}
            </button>
          ))}
        </div>
      )}

      {/* ── Input ── */}
      <div className="px-4 py-3.5 border-t border-white/5">
        <form onSubmit={handleSubmit} className="flex gap-2.5">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about my projects, skills, or schedule an interview…"
            disabled={isLoading}
            className="chat-input flex-1 rounded-xl px-4 py-2.5 text-sm"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="send-btn rounded-xl px-5 py-2.5 text-sm font-medium flex items-center gap-2"
          >
            <span className="hidden sm:inline">Send</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
