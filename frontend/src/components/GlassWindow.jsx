import { motion } from "framer-motion";

/**
 * A macOS-style glass-morphism window panel with a traffic-light title bar.
 */
export default function GlassWindow({ title, children, className = "" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className={`glass overflow-hidden ${className}`}
    >
      {/* Title bar */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-vajra-border">
        {/* Traffic lights */}
        <div className="flex gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#ff5f57]" />
          <span className="w-3 h-3 rounded-full bg-[#febc2e]" />
          <span className="w-3 h-3 rounded-full bg-[#28c840]" />
        </div>
        <span className="ml-2 text-sm font-medium text-vajra-muted select-none">
          {title}
        </span>
      </div>
      {/* Content */}
      <div className="p-5">{children}</div>
    </motion.div>
  );
}
