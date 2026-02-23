import React from "react";

interface MetricTileProps {
  label: string;
  value: string;
  trend?: string;
}

export default function MetricTile({ label, value, trend }: MetricTileProps) {
  return (
    <div className="glass rounded-2xl p-4 border border-skyblue-500/20">
      <p className="text-xs uppercase tracking-widest text-skyblue-200/70">{label}</p>
      <div className="mt-3 flex items-end justify-between">
        <p className="text-2xl font-semibold text-white">{value}</p>
        {trend && (
          <span className="text-xs text-skyblue-300 font-mono">{trend}</span>
        )}
      </div>
    </div>
  );
}
