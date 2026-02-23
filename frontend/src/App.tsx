import React, { useEffect, useMemo, useState } from "react";
import netlifyIdentity from "netlify-identity-widget";
import Heatmap from "./components/Heatmap";
import InsightCard from "./components/InsightCard";
import MetricTile from "./components/MetricTile";
import SetPieceViz from "./components/SetPieceViz";

const insights = [
  {
    title: "Left Half-Space Leak",
    description: "Opponent loses compactness on left when RB steps high. Target with diagonal switches.",
    severity: "high" as const
  },
  {
    title: "Pressing Trigger",
    description: "Press aggressively on the first touch of opponent pivot. 61% turnovers in that zone.",
    severity: "medium" as const
  },
  {
    title: "Set-Piece Advantage",
    description: "Near-post crowding leaves far-post runner free on second phase.",
    severity: "low" as const
  }
];

type LiveSnapshot = {
  updated_at?: string;
  counts?: {
    shots: number;
    passes: number;
    transitions: number;
  };
  pressing_index?: number;
  heatmap?: number[][];
  xthreat?: number[][];
  last_event?: {
    type?: string;
    team?: string;
    player_id?: string;
    timestamp?: number;
  } | null;
};

type IdentityUser = {
  email?: string;
  user_metadata?: {
    full_name?: string;
  };
};

const features = [
  {
    title: "Opponent Intelligence",
    detail: "Automated scanning of defensive gaps, press triggers, and transition leaks."
  },
  {
    title: "Live Match Overlay",
    detail: "Rolling heatmaps, xThreat, and pressing index streamed in real time."
  },
  {
    title: "Risk & Load Alerts",
    detail: "Fatigue, workload spike, and injury risk flags delivered in-session."
  }
];

const workflow = [
  "Ingest event/video data from trusted feeds",
  "Generate opponent and player insights in minutes",
  "Deliver live match intelligence to bench staff",
  "Export reports for post-match review"
];

export default function App() {
  const [snapshot, setSnapshot] = useState<LiveSnapshot | null>(null);
  const [connection, setConnection] = useState<"connected" | "disconnected" | "connecting">(
    "connecting"
  );
  const [user, setUser] = useState<IdentityUser | null>(null);

  const apiBase = useMemo(() => {
    return (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";
  }, []);

  const matchId = "match-001";

  useEffect(() => {
    netlifyIdentity.init();
    setUser((netlifyIdentity.currentUser() as IdentityUser) || null);

    const onLogin = (identityUser: any) => {
      setUser(identityUser as IdentityUser);
      netlifyIdentity.close();
    };
    const onLogout = () => setUser(null);

    netlifyIdentity.on("login", onLogin);
    netlifyIdentity.on("logout", onLogout);

    return () => {
      netlifyIdentity.off("login", onLogin);
      netlifyIdentity.off("logout", onLogout);
    };
  }, []);

  useEffect(() => {
    if (!user) {
      return;
    }

    const resolvedApiBase = apiBase.startsWith("/")
      ? `${window.location.origin}${apiBase}`
      : apiBase;

    fetch(`${resolvedApiBase}/match/${matchId}/live`)
      .then((res) => res.json())
      .then((data) => setSnapshot(data.payload || null))
      .catch(() => null);

    const wsBase = resolvedApiBase.replace(/^http/, "ws");
    const wsRoot = wsBase.replace(/\/api$/, "");
    const wsUrl = `${wsRoot}/ws/match/${matchId}`;

    const ws = new WebSocket(wsUrl);
    setConnection("connecting");

    ws.onopen = () => setConnection("connected");
    ws.onclose = () => setConnection("disconnected");
    ws.onerror = () => setConnection("disconnected");
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.snapshot) {
          setSnapshot(payload.snapshot);
        }
      } catch {
        // ignore parse errors
      }
    };

    return () => ws.close();
  }, [apiBase, user]);

  if (!user) {
    return (
      <div className="min-h-screen text-white">
        <div className="absolute inset-0 grid-overlay opacity-30" />
        <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">
          <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-skyblue-200/60">SkyBlueAI</p>
              <h1 className="text-4xl md:text-5xl font-semibold mt-3 leading-tight">
                Real-time football intelligence for elite clubs.
              </h1>
              <p className="text-base text-slate-200/80 mt-4 max-w-xl">
                Merge video, event data, and AI insights into a single operational dashboard. Built for
                match day, scouting, and performance teams.
              </p>
            </div>
            <div className="glass rounded-3xl p-5 border border-white/10 w-full md:w-72">
              <p className="text-xs uppercase tracking-widest text-slate-300">Access Portal</p>
              <p className="text-sm text-slate-200/80 mt-2">
                Sign in to launch the live intelligence suite.
              </p>
              <button
                className="mt-4 w-full rounded-xl bg-skyblue-500/90 hover:bg-skyblue-400 text-slate-900 py-2 text-sm font-semibold"
                onClick={() => netlifyIdentity.open("login")}
              >
                Sign in with OAuth
              </button>
              <button
                className="mt-2 w-full rounded-xl border border-white/20 text-white py-2 text-xs"
                onClick={() => netlifyIdentity.open("signup")}
              >
                Request access
              </button>
            </div>
          </header>

          <section className="mt-14 grid gap-6 md:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.title} className="glass rounded-2xl p-5 border border-white/10">
                <h3 className="text-base font-semibold text-white">{feature.title}</h3>
                <p className="text-sm text-slate-200/70 mt-2">{feature.detail}</p>
              </div>
            ))}
          </section>

          <section className="mt-12 grid gap-6 lg:grid-cols-2">
            <div className="glass rounded-2xl p-6 border border-white/10">
              <h3 className="text-sm font-semibold text-white">Operational Workflow</h3>
              <ol className="mt-4 space-y-3 text-sm text-slate-200/80">
                {workflow.map((step) => (
                  <li key={step} className="flex gap-3">
                    <span className="text-skyblue-300 font-mono">●</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>
            <div className="glass rounded-2xl p-6 border border-white/10">
              <h3 className="text-sm font-semibold text-white">What You Get</h3>
              <p className="text-sm text-slate-200/80 mt-3">
                Opponent scouting, player performance prediction, injury risk alerts, set-piece
                generation, and tactical recommendations in one continuous feed.
              </p>
              <div className="mt-5 grid grid-cols-2 gap-3 text-xs text-slate-200/70">
                <div className="rounded-xl bg-slate-900/60 p-3">Live match overlays</div>
                <div className="rounded-xl bg-slate-900/60 p-3">Analyst-ready exports</div>
                <div className="rounded-xl bg-slate-900/60 p-3">On-prem deployment</div>
                <div className="rounded-xl bg-slate-900/60 p-3">Secure access</div>
              </div>
            </div>
          </section>
        </div>
      </div>
    );
  }

  const pressingIndex = snapshot?.pressing_index ?? 0.0;
  const counts = snapshot?.counts || { shots: 0, passes: 0, transitions: 0 };
  const lastEvent = snapshot?.last_event;

  return (
    <div className="min-h-screen text-white">
      <div className="absolute inset-0 grid-overlay opacity-20" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-skyblue-200/60">SkyBlueAI</p>
            <h1 className="text-3xl md:text-4xl font-semibold mt-2">Match Intelligence Suite</h1>
            <p className="text-sm text-slate-300/80 mt-2">Manchester City vs Arsenal - 23 Feb 2026</p>
          </div>
          <div className="glass rounded-2xl px-4 py-2 text-xs text-slate-200/80 flex items-center gap-4">
            <span>
              Live status <span className="text-skyblue-300 font-mono">{connection}</span>
            </span>
            <span className="text-slate-400">|</span>
            <span className="text-slate-200/80">
              {user?.user_metadata?.full_name || user?.email}
            </span>
            <button
              className="text-xs text-skyblue-200 hover:text-skyblue-100"
              onClick={() => netlifyIdentity.logout()}
            >
              Sign out
            </button>
          </div>
        </header>

        <section className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricTile label="Processing Time" value="4:32" trend="-18%" />
          <MetricTile label="Pressing Index" value={pressingIndex.toFixed(2)} trend="+0.08" />
          <MetricTile label="Shots / Passes" value={`${counts.shots} / ${counts.passes}`} />
          <MetricTile label="Transitions" value={`${counts.transitions}`} />
        </section>

        <section className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Heatmap data={snapshot?.heatmap} />
            <SetPieceViz />
          </div>
          <div className="space-y-4">
            <div className="glass rounded-2xl p-4 border border-white/10">
              <h3 className="text-sm font-semibold text-white">Tactical AI Coach</h3>
              <ul className="mt-3 text-sm text-slate-200/80 space-y-2">
                <li>Activate 3-2 build-up vs mid-block</li>
                <li>Overload left half-space, switch early</li>
                <li>Trigger press on back-pass to CB</li>
              </ul>
            </div>
            {insights.map((insight) => (
              <InsightCard
                key={insight.title}
                title={insight.title}
                description={insight.description}
                severity={insight.severity}
              />
            ))}
          </div>
        </section>

        <section className="mt-10">
          <div className="glass rounded-2xl p-6 border border-white/10">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Live Match Feed</h3>
              <span className="text-xs text-slate-300/70">
                Last event: {lastEvent?.timestamp ?? "--"}
              </span>
            </div>
            <div className="mt-4 grid md:grid-cols-3 gap-4 text-sm text-slate-200/80">
              <div className="p-4 rounded-xl bg-slate-900/60">
                <p className="text-xs uppercase tracking-widest text-slate-400">Transition</p>
                <p className="mt-2">Latest event: {lastEvent?.type ?? "No event yet"}.</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60">
                <p className="text-xs uppercase tracking-widest text-slate-400">Injury Alert</p>
                <p className="mt-2">High load spike detected for #16. Recommend 10 min cooldown.</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60">
                <p className="text-xs uppercase tracking-widest text-slate-400">Set Piece</p>
                <p className="mt-2">Corner delivery pattern exploited in last 3 matches.</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
