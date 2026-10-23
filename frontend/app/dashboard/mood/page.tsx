"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { MoodChart } from "@/components/dashboard/MoodChart";
import { AutoMoodTrends } from "@/components/dashboard/AutoMoodTrends";
import { moodApi } from "@/lib/api";
import { formatIndianDateTime } from "@/lib/utils";

const LABELS = ["anxious", "sad", "neutral", "calm", "happy"];

interface MoodLog {
  id: string;
  mood_score: number;
  mood_label: string | null;
  notes: string | null;
  logged_at: string;
  auto_detected?: boolean;
}

interface MoodTrendData {
  daily_trend: { date: string; avg_score: number; dominant_mood: string | null }[];
  weekly_avg: number;
  monthly_avg: number;
  most_frequent_emotions: { label: string; count: number }[];
  total_auto_detected: number;
  trend_direction: string;
}

export default function MoodPage() {
  const [score, setScore] = useState(5);
  const [label, setLabel] = useState("neutral");
  const [notes, setNotes] = useState("");
  const [history, setHistory] = useState<MoodLog[]>([]);
  const [stats, setStats] = useState<{ avg_score: number } | null>(null);
  const [trends, setTrends] = useState<MoodTrendData | null>(null);
  const [saving, setSaving] = useState(false);

  const load = () => {
    moodApi.history(30).then((r) => setHistory(r.data)).catch(() => {});
    moodApi.stats().then((r) => setStats(r.data)).catch(() => {});
    moodApi.trends(30).then((r) => setTrends(r.data)).catch(() => {});
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async () => {
    setSaving(true);
    try {
      await moodApi.log({ mood_score: score, mood_label: label, notes: notes || undefined });
      setNotes("");
      load();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6 max-w-3xl mx-auto bg-parchment">
      {/* Desktop & Mobile Breadcrumb Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-xs font-medium text-ink/70 hover:text-ink bg-ink/5 hover:bg-ink/10 px-3 py-1.5 rounded-full transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Dashboard
          </Link>
          <h1 className="font-display text-2xl text-ink">Mood Tracker</h1>
        </div>
      </div>

      {/* ── AI-Detected Mood Trends (Phase 8) ────────────────────────────── */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>🧠</span> AI-Detected Mood Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AutoMoodTrends data={trends} />
        </CardContent>
      </Card>

      {/* ── Manual Mood Logging Form ────────────────────────────────────── */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>How are you feeling today?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Score: {score} / 10</Label>
            <input
              type="range"
              min={1}
              max={10}
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
              className="w-full mt-2 accent-sage cursor-pointer"
            />
          </div>
          <div>
            <Label>Primary emotion</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {LABELS.map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => setLabel(l)}
                  className={`rounded-full px-3 py-1 text-xs capitalize transition-colors ${
                    label === l ? "bg-sage text-parchment font-semibold" : "border border-ink/20 text-ink/70 hover:border-ink/40"
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>
          <div>
            <Label htmlFor="notes">Notes (optional)</Label>
            <textarea
              id="notes"
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-200 bg-white p-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-sage"
              placeholder="What contributed to how you feel?"
            />
          </div>
          <Button onClick={submit} disabled={saving} className="bg-sage text-parchment hover:bg-ink">
            {saving ? "Saving..." : "Log mood"}
          </Button>
        </CardContent>
      </Card>

      {stats && (
        <p className="text-xs text-ink/50 mb-3">
          30-day average: <strong className="text-ink">{stats.avg_score.toFixed(1)} / 10</strong>
        </p>
      )}

      {/* ── Visual Trend Chart ─────────────────────────────────────────── */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>30-Day Score Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <MoodChart data={history} />
        </CardContent>
      </Card>

      {/* ── Recent Logs List ───────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle>Recent entries</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <p className="text-sm text-ink/50">No mood entries yet. Log your first one above!</p>
          ) : (
            <div className="space-y-3">
              {history.map((h) => (
                <div key={h.id} className="flex items-start justify-between border-b border-ink/10 pb-3 last:border-0 last:pb-0">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-ink capitalize">{h.mood_label || "Score"}</span>
                      {h.auto_detected && (
                        <span className="text-[10px] bg-sage/15 text-sage px-1.5 py-0.5 rounded-full font-medium">
                          AI detected
                        </span>
                      )}
                      <span className="text-xs text-ink/40">· {formatIndianDateTime(h.logged_at)}</span>
                    </div>
                    {h.notes && <p className="text-xs text-ink/70 mt-1">{h.notes}</p>}
                  </div>
                  <span className="text-sm font-bold text-sage">{h.mood_score}/10</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
