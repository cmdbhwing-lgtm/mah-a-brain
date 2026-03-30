import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const COLORS = ["#6366f1", "#a855f7", "#ec4899", "#f43f5e", "#f59e0b", "#22c55e"];

/**
 * Per-core CPU utilization bar chart.
 */
export default function CpuChart({ cores = [] }) {
  const data = cores.map((pct, i) => ({
    name: `C${i}`,
    usage: pct,
  }));

  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} barSize={14}>
        <XAxis
          dataKey="name"
          tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={30}
        />
        <Tooltip
          contentStyle={{
            background: "rgba(15,15,25,0.9)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 8,
            color: "#fff",
            fontSize: 12,
          }}
          formatter={(v) => [`${v}%`, "Usage"]}
        />
        <Bar dataKey="usage" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.8} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
