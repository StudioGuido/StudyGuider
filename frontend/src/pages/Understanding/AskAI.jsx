import React from "react";
import { useState } from "react";

export default function AskAI() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      text: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsSending(true);

    // Mock AI response after a small delay
    setTimeout(() => {
      const aiMessage = {
        id: Date.now() + 1,
        role: "assistant",
        text: "This is a mock AI response to your question: " + trimmed,
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsSending(false);
    }, 1500);
  };

  return (
    <div className="flex h-full flex-col text-slate-100">
      {/* Chat area */}
      <div className="flex-1 overflow-auto pr-2">
        {messages.length === 0 ? (
          // Empty state (the conversation has no messages yet)
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-slate-300">
              Ask AI to start a conversation!
            </p>
          </div>
        ) : (
          // Messages
          <div className="space-y-3 py-2">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                    msg.role === "user"
                      ? "bg-white text-black"
                      : "bg-neutral-800 text-slate-100"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {isSending && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-neutral-800 px-4 py-2.5">
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]"></div>
                    <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]"></div>
                    <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400"></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input text area */}
      <div className="mt-3 pt-3 border-t border-neutral-800/50">
        <div
          className="flex items-center rounded-full bg-neutral-900 border border-neutral-700 px-4 py-3 cursor-text"
          onClick={() => document.getElementById("askAiInput")?.focus()}
        >
          <input
            id="askAiInput"
            type="text"
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none"
            placeholder="Ask anything related to the textbook"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                handleSubmit(e);
              }
            }}
            disabled={isSending}
          />
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSending || !input.trim()}
            className="ml-3 flex h-8 w-8 items-center justify-center rounded-full bg-neutral-700 text-slate-300 hover:bg-neutral-600 disabled:cursor-not-allowed disabled:opacity-40 transition"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
