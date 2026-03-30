import { motion } from "framer-motion";
import {
  VscTerminalBash,
  VscDashboard,
  VscSettingsGear,
  VscPulse,
} from "react-icons/vsc";

const DOCK_ITEMS = [
  { icon: VscDashboard, label: "Dashboard", id: "dashboard" },
  { icon: VscTerminalBash, label: "Terminal", id: "terminal" },
  { icon: VscPulse, label: "System Status", id: "status" },
  { icon: VscSettingsGear, label: "Settings", id: "settings" },
];

/**
 * macOS-style bottom dock with hover magnification effect.
 */
export default function Dock({ activeView, onSelect }) {
  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
      <motion.div
        initial={{ y: 80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="glass-dock flex items-end gap-2 px-4 py-2"
      >
        {DOCK_ITEMS.map(({ icon: Icon, label, id }) => {
          const isActive = activeView === id;
          return (
            <motion.button
              key={id}
              onClick={() => onSelect(id)}
              whileHover={{ scale: 1.25, y: -6 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
              className="relative flex flex-col items-center group"
              title={label}
            >
              <div
                className={`p-3 rounded-xl transition-colors ${
                  isActive
                    ? "bg-vajra-accent/20 text-vajra-accent"
                    : "text-vajra-muted hover:text-white"
                }`}
              >
                <Icon size={26} />
              </div>
              {/* Active indicator dot */}
              {isActive && (
                <motion.span
                  layoutId="dock-dot"
                  className="absolute -bottom-1 w-1 h-1 rounded-full bg-vajra-accent"
                />
              )}
              {/* Tooltip */}
              <span className="absolute -top-8 opacity-0 group-hover:opacity-100 transition-opacity text-xs bg-black/80 text-white px-2 py-0.5 rounded whitespace-nowrap pointer-events-none">
                {label}
              </span>
            </motion.button>
          );
        })}
      </motion.div>
    </div>
  );
}
