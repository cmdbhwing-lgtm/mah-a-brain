import { useState, useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import GlassWindow from "./GlassWindow";

let _lineId = 0;
function nextId() {
  return ++_lineId;
}

/**
 * A terminal view that sends commands to /api/execute
 * and displays the echoed responses.
 */
export default function TerminalView() {
  const [history, setHistory] = useState(() => [
    { id: nextId(), type: "system", text: "Vajra Engine v0.1.0 -- Type a command below." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const addLines = useCallback((...lines) => {
    setHistory((h) => [...h, ...lines.map((l) => ({ ...l, id: nextId() }))]);
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const cmd = input.trim();
    addLines({ type: "input", text: cmd });
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd }),
      });
      const data = await res.json();
      addLines(
        { type: "output", text: data.echo },
        { type: "meta", text: `Status: ${data.status} | ${data.timestamp}` },
      );
    } catch (err) {
      addLines({ type: "error", text: `Error: ${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  const lineColor = {
    system: "text-vajra-accent",
    input: "text-green-400",
    output: "text-white",
    meta: "text-vajra-muted",
    error: "text-vajra-danger",
  };

  return (
    <div className="p-6 pb-24 h-full">
      <GlassWindow
        title="Terminal"
        className="h-[calc(100vh-10rem)]"
        fillHeight
      >
        {/* Scrollable output */}
        <div className="flex-1 overflow-y-auto font-mono text-sm space-y-1 mb-3 min-h-0">
          {history.map((line) => (
            <motion.div
              key={line.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              className={lineColor[line.type] || "text-white"}
            >
              {line.type === "input" && (
                <span className="text-vajra-muted mr-1">{">"}</span>
              )}
              {line.text}
            </motion.div>
          ))}
          <div ref={endRef} />
        </div>

        {/* Input */}
        <form onSubmit={submit} className="flex gap-2 shrink-0">
          <span className="text-vajra-accent font-mono pt-2">$</span>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 bg-transparent border border-vajra-border rounded-lg px-3 py-2 text-sm font-mono text-white outline-none focus:border-vajra-accent/50 transition-colors placeholder:text-vajra-muted"
            placeholder="Enter command..."
            autoFocus
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-vajra-accent/20 text-vajra-accent text-sm font-medium hover:bg-vajra-accent/30 transition-colors disabled:opacity-40"
          >
            {loading ? "..." : "Run"}
          </button>
        </form>
      </GlassWindow>
    </div>
  );
}
