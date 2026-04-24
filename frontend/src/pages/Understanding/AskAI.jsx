import React, { useEffect, useRef, useState } from "react";
import { supabase } from "../../services/supabaseClient";
import MarkdownContent from "../../components/MarkdownContent";

// Module-scoped state so in-flight requests survive unmounts (tab/chapter/phase switches).
const chatCache = new Map();   // cacheKey -> messages[]
const pending = new Set();     // cacheKeys with an in-flight request
const listeners = new Map();   // cacheKey -> Set<callback>

function subscribe(cacheKey, cb) {
  if (!listeners.has(cacheKey)) listeners.set(cacheKey, new Set());
  listeners.get(cacheKey).add(cb);
  return () => listeners.get(cacheKey)?.delete(cb);
}

function notify(cacheKey) {
  listeners.get(cacheKey)?.forEach((cb) => cb());
}

async function sendChatMessage({ cacheKey, bookId, chapterId, userText }) {
  const existing = chatCache.get(cacheKey) ?? [];
  const withUser = [
    ...existing,
    { id: Date.now(), role: "user", text: userText },
  ];
  chatCache.set(cacheKey, withUser);
  pending.add(cacheKey);
  notify(cacheKey);

  try {
    const { data: sessionData } = await supabase.auth.getSession();
    const token = sessionData.session?.access_token;
    if (!token) throw new Error("Not authenticated");

    const res = await fetch("http://localhost:8000/api/askAI", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        textbook_id: bookId,
        chapter_number: parseInt(chapterId, 10),
        messages: withUser.map(({ role, text }) => ({ role, text })),
      }),
    });
    if (!res.ok) throw new Error("Request failed");

    const data = await res.json();
    chatCache.set(cacheKey, [
      ...withUser,
      {
        id: Date.now() + 1,
        role: "assistant",
        text: data.response ?? "",
      },
    ]);
  } catch (err) {
    console.error("AskAI request failed:", err);
    chatCache.set(cacheKey, [
      ...withUser,
      {
        id: Date.now() + 1,
        role: "assistant",
        text: "Something went wrong. Please try again.",
        isError: true,
      },
    ]);
  } finally {
    pending.delete(cacheKey);
    notify(cacheKey);
  }
}

function retryMessage({ cacheKey, bookId, chapterId, userMessageId }) {
  if (pending.has(cacheKey)) return;
  const existing = chatCache.get(cacheKey) ?? [];
  const idx = existing.findIndex((m) => m.id === userMessageId);
  if (idx === -1 || existing[idx].role !== "user") return;

  const userText = existing[idx].text;
  chatCache.set(cacheKey, existing.slice(0, idx));
  notify(cacheKey);

  sendChatMessage({ cacheKey, bookId, chapterId, userText });
}

function useChatState(cacheKey) {
  const [state, setState] = useState(() => ({
    messages: cacheKey ? chatCache.get(cacheKey) ?? [] : [],
    isSending: cacheKey ? pending.has(cacheKey) : false,
  }));

  useEffect(() => {
    if (!cacheKey) {
      setState({ messages: [], isSending: false });
      return undefined;
    }
    const sync = () => {
      setState({
        messages: chatCache.get(cacheKey) ?? [],
        isSending: pending.has(cacheKey),
      });
    };
    sync();
    return subscribe(cacheKey, sync);
  }, [cacheKey]);

  return state;
}

export default function AskAI({ bookId, chapterId }) {
  const cacheKey = bookId && chapterId ? `${bookId}:${chapterId}` : null;
  const { messages, isSending } = useChatState(cacheKey);
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isSending]);

  const handleSubmit = (e) => {
    e?.preventDefault?.();
    const trimmed = input.trim();
    if (!trimmed || isSending || !cacheKey) return;
    setInput("");
    sendChatMessage({ cacheKey, bookId, chapterId, userText: trimmed });
  };

  return (
    <div className="flex h-full flex-col text-slate-100">
      <div ref={scrollRef} className="flex-1 overflow-auto pr-2">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-slate-300">
              Ask AI to start a conversation!
            </p>
          </div>
        ) : (
          <div className="space-y-3 py-2">
            {messages.map((msg, idx) => {
              const nextMsg = messages[idx + 1];
              const canRetry =
                msg.role === "user" && nextMsg?.isError && !isSending;
              return (
                <div
                  key={msg.id}
                  className={`flex items-center gap-2 ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {canRetry && (
                    <button
                      type="button"
                      onClick={() =>
                        retryMessage({
                          cacheKey,
                          bookId,
                          chapterId,
                          userMessageId: msg.id,
                        })
                      }
                      title="Retry"
                      aria-label="Retry sending this message"
                      style={{
                        width: 28,
                        height: 28,
                        minWidth: 28,
                        flexShrink: 0,
                      }}
                      className="flex items-center justify-center rounded-full bg-neutral-800 text-slate-200 leading-none hover:bg-neutral-700 transition"
                    >
                      <span style={{ fontSize: 16, lineHeight: 1 }}>↻</span>
                    </button>
                  )}
                  <div
                    className={`min-w-0 max-w-[85%] break-words rounded-2xl px-4 py-2.5 text-sm ${
                      msg.role === "user"
                        ? "bg-white text-black"
                        : msg.isError
                          ? "bg-red-900/40 text-red-200"
                          : "bg-neutral-800 text-slate-100"
                    }`}
                  >
                    {msg.role === "assistant" && !msg.isError ? (
                      <MarkdownContent>{msg.text}</MarkdownContent>
                    ) : (
                      <div className="whitespace-pre-wrap">{msg.text}</div>
                    )}
                  </div>
                </div>
              );
            })}

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

      <div className="mt-3 pt-3 border-t border-neutral-800/50">
        <form
          onSubmit={handleSubmit}
          className="flex items-center rounded-full bg-neutral-900 border border-neutral-700 px-4 py-3 cursor-text"
          onClick={() => document.getElementById("askAiInput")?.focus()}
        >
          <input
            id="askAiInput"
            type="text"
            autoComplete="off"
            autoCorrect="off"
            spellCheck={false}
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none"
            placeholder="Ask anything related to the textbook"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isSending}
          />
          <button
            type="submit"
            disabled={isSending || !input.trim()}
            className="ml-3 flex h-8 w-8 items-center justify-center rounded-full bg-neutral-700 text-slate-300 hover:bg-neutral-600 disabled:cursor-not-allowed disabled:opacity-40 transition"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
