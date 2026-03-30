import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useMetrics } from "./hooks/useMetrics";
import StatusBar from "./components/StatusBar";
import Dock from "./components/Dock";
import Dashboard from "./components/Dashboard";
import TerminalView from "./components/TerminalView";
import GlassWindow from "./components/GlassWindow";

/**
 * Root application shell -- macOS-style layout with status bar,
 * content area, and bottom dock.
 */
export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const { metrics, connected } = useMetrics();

  return (
    <div className="min-h-screen bg-vajra-bg overflow-hidden">
      {/* Ambient glow background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-vajra-accent/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/5 rounded-full blur-[100px]" />
      </div>

      {/* Status bar */}
      <StatusBar connected={connected} />

      {/* Main content area */}
      <main className="pt-10 relative z-10 h-screen overflow-y-auto">
        <AnimatePresence mode="wait">
          {activeView === "dashboard" && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
            >
              <Dashboard metrics={metrics} />
            </motion.div>
          )}

          {activeView === "terminal" && (
            <motion.div
              key="terminal"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="h-[calc(100vh-2.5rem)]"
            >
              <TerminalView />
            </motion.div>
          )}

          {activeView === "status" && (
            <motion.div
              key="status"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="p-6 pb-24"
            >
              <GlassWindow title="Raw System Status">
                <pre className="text-xs font-mono text-vajra-muted overflow-auto max-h-[70vh] whitespace-pre-wrap">
                  {metrics
                    ? JSON.stringify(metrics, null, 2)
                    : "Waiting for data..."}
                </pre>
              </GlassWindow>
            </motion.div>
          )}

          {activeView === "settings" && (
            <motion.div
              key="settings"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="p-6 pb-24"
            >
              <GlassWindow title="Settings">
                <div className="space-y-4 text-sm text-vajra-muted">
                  <p>Vajra Exocortex v0.1.0</p>
                  <p>
                    Engine: Level 1 -- Foundation Base
                  </p>
                  <div className="border-t border-vajra-border pt-4 space-y-2">
                    <h3 className="text-white font-medium">Roadmap</h3>
                    <ul className="list-disc list-inside space-y-1">
                      <li className="text-vajra-success">
                        Level 1: Glassmorphism Base (Current)
                      </li>
                      <li>Level 2: Mega Pattern Leecher + WebSocket Crawler</li>
                      <li>Level 3: Neural Sleep Cycle + God Mode Upgrades</li>
                      <li>Level 4: Multi-Tenant SaaS + API Monetization</li>
                      <li>Level 5: Megatron Distributed Cluster + CAD/CFD</li>
                    </ul>
                  </div>
                </div>
              </GlassWindow>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Dock */}
      <Dock activeView={activeView} onSelect={setActiveView} />
    </div>
  );
}
