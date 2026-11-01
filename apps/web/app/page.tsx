"use client";

import { useState } from "react";

type Msg = { role: "user" | "assistant"; content: string };

export default function Home() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function ask() {
    if (!input.trim() || busy) return;
    const q = input;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }, { role: "assistant", content: "" }]);
    setBusy(true);

    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    if (!res.body) {
      setBusy(false);
      return;
    }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const parts = buf.split("\n\n");
      buf = parts.pop() ?? "";
      for (const part of parts) {
        if (!part.startsWith("data: ")) continue;
        const payload = JSON.parse(part.slice(6));
        if (payload.delta) {
          setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = {
              role: "assistant",
              content: copy[copy.length - 1].content + payload.delta,
            };
            return copy;
          });
        }
      }
    }
    setBusy(false);
  }

  return (
    <main className="mx-auto flex h-screen max-w-3xl flex-col p-6">
      <h1 className="mb-6 text-2xl font-semibold">DocuChat</h1>
      <div className="flex-1 space-y-4 overflow-y-auto">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-neutral-300" : "text-emerald-300"}>
            <span className="mr-2 text-xs uppercase opacity-60">{m.role}</span>
            {m.content}
          </div>
        ))}
      </div>
      <div className="mt-6 flex gap-2">
        <input
          className="flex-1 rounded border border-neutral-700 bg-neutral-900 px-3 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
          placeholder="Ask a question..."
        />
        <button
          className="rounded bg-emerald-600 px-4 py-2 disabled:opacity-50"
          onClick={ask}
          disabled={busy}
        >
          Send
        </button>
      </div>
    </main>
  );
}
