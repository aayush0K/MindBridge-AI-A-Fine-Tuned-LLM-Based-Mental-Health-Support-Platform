"use client";

import { useEffect, useState } from "react";
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
      <h1 className="font-display text-2xl text-ink mb-6">Mood tracker</h1>

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

      {/* ── Manual Mood Entry ─────────────────────────────────────────────── */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Log how you feel</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Mood score: {score}/10</Label>
            <input
              type="range"
              min={1}
              max={10}
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
              className="w-full mt-2 accent-sage"
            />
          </div>
          <div>
            <Label>Label</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {LABELS.map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => setLabel(l)}
                  className={`rounded-full px-3 py-1 text-sm capitalize border transition-colors duration-300 ease-mb-ease ${
                    label === l ? "bg-sage text-parchment border-sage" : "border-ink/20 text-ink/70 hover:bg-ink/5"
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
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="mt-1 w-full rounded-xl border border-ink/15 p-3 text-sm min-h-[80px] focus:border-sage focus:ring-1 focus:ring-sage outline-none bg-white text-ink placeholder:text-warm transition-colors duration-300 ease-mb-ease"
              placeholder="What influenced your mood today?"
            />
          </div>
          <Button onClick={submit} disabled={saving} className="bg-sage text-parchment hover:bg-ink rounded-full transition-colors duration-300 ease-mb-ease">
            {saving ? "Saving..." : "Save mood"}
          </Button>
        </CardContent>
      </Card>

      {stats && (
        <p className="text-sm text-ink/60 mb-4">
          Weekly average: <strong className="font-display text-lg text-ink">{stats.avg_score.toFixed(1)}</strong>/10
        </p>
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Manual Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <MoodChart data={history.filter((h) => !h.auto_detected)} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>History</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {history.map((log) => (
              <li key={log.id} className="flex justify-between text-sm border-b border-ink/10 py-2">
                <span className="text-ink">
                  {log.auto_detected && <span className="text-xs bg-sage/10 text-sage px-1.5 py-0.5 rounded mr-2">AI</span>}
                  {log.mood_label} · {log.mood_score}/10
                </span>
                <span className="text-ink/50 text-xs">{formatIndianDateTime(log.logged_at)}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
