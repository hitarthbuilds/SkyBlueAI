import React from "react";

interface InsightCardProps {
  title: string;
  description: string;
  severity: "low" | "medium" | "high";
}

const colors: Record<string, string> = {
  low: "bg-skyblue-400/20 text-skyblue-200",
  medium: "bg-amber-400/20 text-amber-200",
  high: "bg-rose-400/20 text-rose-200"
};

export default function InsightCard({ title, description, severity }: InsightCardProps) {
  return (
    <div className="glass rounded-2xl p-4 border border-white/10">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${colors[severity]}`}>
          {severity}
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-200/80 leading-relaxed">{description}</p>
    </div>
  );
}
