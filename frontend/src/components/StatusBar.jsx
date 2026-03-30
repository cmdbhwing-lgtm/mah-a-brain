import { motion } from "framer-motion";

/**
 * macOS-style top menu/status bar.
 */
export default function StatusBar({ connected }) {
  const now = new Date();
  const timeStr = now.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-8 flex items-center justify-between px-5 bg-black/40 backdrop-blur-[20px] border-b border-vajra-border text-xs select-none">
      {/* Left */}
      <div className="flex items-center gap-4">
        <span className="font-semibold text-white">Vajra</span>
        <span className="text-vajra-muted">File</span>
        <span className="text-vajra-muted">View</span>
        <span className="text-vajra-muted">Tools</span>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        <motion.div
          animate={{ opacity: [1, 0.4, 1] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="flex items-center gap-1.5"
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              connected ? "bg-vajra-success" : "bg-vajra-danger"
            }`}
          />
          <span className="text-vajra-muted">
            {connected ? "Connected" : "Disconnected"}
          </span>
        </motion.div>
        <span className="text-vajra-muted font-mono">{timeStr}</span>
      </div>
    </div>
  );
}
