"use client";

import { useEffect, useState } from "react";

type Doc = {
  id: string;
  title: string;
  source: string;
  chunks: number;
  created_at: string;
};

type Stats = {
  query_count: number;
  avg_latency_ms: number;
  total_input_tokens: number;
  total_output_tokens: number;
  estimated_cost_usd: number;
};

export default function Admin() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    const [d, s] = await Promise.all([
      fetch("/api/documents").then((r) => r.json()),
      fetch("/api/stats").then((r) => r.json()),
    ]);
    setDocs(d);
    setStats(s);
  }

  useEffect(() => {
    load();
  }, []);

  async function upload(file: File) {
    setBusy(true);
    const fd = new FormData();
    fd.append("file", file);
    await fetch("/api/ingest", { method: "POST", body: fd });
    await load();
    setBusy(false);
  }

  async function remove(id: string) {
    await fetch(`/api/documents/${id}`, { method: "DELETE" });
    await load();
  }

  return (
    <main className="mx-auto max-w-4xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Admin</h1>
        <a href="/" className="text-sm text-emerald-400 hover:underline">
          ← Back to chat
        </a>
      </div>

      {stats && (
        <section className="mb-10 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Queries" value={stats.query_count.toLocaleString()} />
          <Stat label="Avg latency" value={`${stats.avg_latency_ms} ms`} />
          <Stat
            label="Tokens"
            value={`${(stats.total_input_tokens + stats.total_output_tokens).toLocaleString()}`}
          />
          <Stat label="Est. cost" value={`$${stats.estimated_cost_usd.toFixed(4)}`} />
        </section>
      )}

      <section className="mb-8">
        <h2 className="mb-3 text-sm uppercase tracking-wider text-neutral-400">Upload PDF</h2>
        <input
          type="file"
          accept="application/pdf"
          disabled={busy}
          onChange={(e) => e.target.files && upload(e.target.files[0])}
          className="block w-full rounded border border-neutral-700 bg-neutral-900 p-2 text-sm file:mr-3 file:rounded file:border-0 file:bg-emerald-600 file:px-3 file:py-1.5 file:text-white"
        />
      </section>

      <section>
        <h2 className="mb-3 text-sm uppercase tracking-wider text-neutral-400">
          Documents ({docs.length})
        </h2>
        <ul className="divide-y divide-neutral-800 rounded border border-neutral-800">
          {docs.map((d) => (
            <li key={d.id} className="flex items-center justify-between p-3">
              <div>
                <div className="font-medium">{d.title}</div>
                <div className="text-xs text-neutral-500">
                  {d.chunks} chunks · {new Date(d.created_at).toLocaleString()}
                </div>
              </div>
              <button
                onClick={() => remove(d.id)}
                className="rounded border border-red-800 px-3 py-1 text-sm text-red-400 hover:bg-red-950"
              >
                Delete
              </button>
            </li>
          ))}
          {docs.length === 0 && (
            <li className="p-6 text-center text-sm text-neutral-500">
              No documents yet. Upload a PDF above.
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-neutral-800 bg-neutral-900 p-3">
      <div className="text-xs uppercase tracking-wider text-neutral-500">{label}</div>
      <div className="mt-1 text-lg font-semibold">{value}</div>
    </div>
  );
}
