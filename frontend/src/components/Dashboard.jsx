import GlassWindow from "./GlassWindow";
import MetricRing from "./MetricRing";
import CpuChart from "./CpuChart";

/**
 * Main dashboard view showing system metrics in a grid of glass panels.
 */
export default function Dashboard({ metrics }) {
  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-full text-vajra-muted">
        Connecting to Vajra Engine...
      </div>
    );
  }

  const { cpu, memory, disk, gpu, network } = metrics;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 p-6 pb-24">
      {/* CPU Overview */}
      <GlassWindow title="CPU" className="col-span-1">
        <div className="flex items-center justify-around">
          <MetricRing
            label="Usage"
            value={cpu.usage_pct}
            color="#6366f1"
          />
          <div className="text-sm space-y-2 text-vajra-muted">
            <p>
              Cores:{" "}
              <span className="text-white">
                {cpu.cores_physical}P / {cpu.cores_logical}L
              </span>
            </p>
            {cpu.freq_mhz && (
              <p>
                Freq:{" "}
                <span className="text-white">
                  {Math.round(cpu.freq_mhz)} MHz
                </span>
              </p>
            )}
          </div>
        </div>
      </GlassWindow>

      {/* Memory */}
      <GlassWindow title="Memory" className="col-span-1">
        <div className="flex items-center justify-around">
          <MetricRing
            label="RAM"
            value={memory.usage_pct}
            color="#a855f7"
          />
          <div className="text-sm space-y-2 text-vajra-muted">
            <p>
              Used:{" "}
              <span className="text-white">{memory.used_gb} GB</span>
            </p>
            <p>
              Total:{" "}
              <span className="text-white">{memory.total_gb} GB</span>
            </p>
            <p>
              Free:{" "}
              <span className="text-white">{memory.available_gb} GB</span>
            </p>
          </div>
        </div>
      </GlassWindow>

      {/* Disk */}
      <GlassWindow title="Disk" className="col-span-1">
        <div className="flex items-center justify-around">
          <MetricRing
            label="Storage"
            value={disk.usage_pct}
            color="#22c55e"
          />
          <div className="text-sm space-y-2 text-vajra-muted">
            <p>
              Used:{" "}
              <span className="text-white">{disk.used_gb} GB</span>
            </p>
            <p>
              Total:{" "}
              <span className="text-white">{disk.total_gb} GB</span>
            </p>
            <p>
              Free:{" "}
              <span className="text-white">{disk.free_gb} GB</span>
            </p>
          </div>
        </div>
      </GlassWindow>

      {/* GPU (conditional) */}
      {gpu && (
        <GlassWindow title={`GPU - ${gpu.name}`} className="col-span-1">
          <div className="flex items-center justify-around">
            <MetricRing
              label="GPU Load"
              value={gpu.utilization_pct}
              color="#f59e0b"
            />
            <div className="text-sm space-y-2 text-vajra-muted">
              <p>
                VRAM:{" "}
                <span className="text-white">
                  {Math.round(gpu.memory_used_mb)} / {Math.round(gpu.memory_total_mb)} MB
                </span>
              </p>
              <p>
                Temp:{" "}
                <span className="text-white">{gpu.temperature_c} C</span>
              </p>
            </div>
          </div>
        </GlassWindow>
      )}

      {/* Network */}
      <GlassWindow title="Network I/O" className="col-span-1">
        <div className="text-sm space-y-3 text-vajra-muted">
          <p>
            Sent:{" "}
            <span className="text-white font-mono">
              {formatBytes(network.bytes_sent)}
            </span>
          </p>
          <p>
            Received:{" "}
            <span className="text-white font-mono">
              {formatBytes(network.bytes_recv)}
            </span>
          </p>
        </div>
      </GlassWindow>

      {/* Per-core CPU chart */}
      <GlassWindow title="Per-Core Usage" className="md:col-span-2 xl:col-span-2">
        <CpuChart cores={cpu.per_core_pct} />
      </GlassWindow>
    </div>
  );
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
}
