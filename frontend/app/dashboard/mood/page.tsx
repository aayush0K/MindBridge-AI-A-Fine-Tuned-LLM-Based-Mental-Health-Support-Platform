"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles, TrendingUp, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { MoodChart } from "@/components/dashboard/MoodChart";
import { AutoMoodTrends } from "@/components/dashboard/AutoMoodTrends";
import { moodApi } from "@/lib/api";
import { formatIndianDateTime } from "@/lib/utils";

const LABELS = [
  { value: "anxious", label: "Anxious 😟" },
  { value: "sad", label: "Sad 😢" },
  { value: "neutral", label: "Neutral 😐" },
  { value: "calm", label: "Calm 🌿" },
  { value: "happy", label: "Happy ✨" },
];

const SCORE_LABELS: Record<number, string> = {
  1: "1 · Very Low 😢",
  2: "2 · Struggling 😔",
  3: "3 · Down 😕",
  4: "4 · Low Energy 🥱",
  5: "5 · Neutral 😐",
  6: "6 · Okay 🙂",
  7: "7 · Good 😊",
  8: "8 · Upbeat 😄",
  9: "9 · Thriving 🌟",
  10: "10 · Peak Joy ✨",
};

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
  const [submitted, setSubmitted] = useState(false);

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
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 2500);
      load();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-8 max-w-4xl mx-auto bg-parchment space-y-6">
      {/* ── Desktop Breadcrumb Header ──────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="hidden md:inline-flex items-center gap-1.5 text-xs font-medium text-ink/70 hover:text-ink bg-white border border-ink/10 hover:border-ink/20 shadow-xs px-3.5 py-1.5 rounded-full transition-all"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Dashboard</span>
          </Link>
          <div>
            <h1 className="font-display text-2xl md:text-3xl text-ink font-semibold tracking-tight">
              Mood Tracker
            </h1>
            <p className="text-xs text-ink/60 mt-0.5">
              Log how you feel each day, observe emotional trends, and view AI insights.
            </p>
          </div>
        </div>
      </div>

      {/* ── AI-Detected Mood Trends (Phase 8) ────────────────────────────── */}
      <Card className="shadow-xs border border-ink/8">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base font-semibold text-ink">
            <span className="p-1.5 rounded-lg bg-sage/15 text-sage">🧠</span>
            <span>AI-Detected Emotional Rhythm</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AutoMoodTrends data={trends} />
        </CardContent>
      </Card>

      {/* ── Manual Mood Logging Form ────────────────────────────────────── */}
      <Card className="shadow-xs border border-ink/8">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold text-ink">
            How are you feeling right now?
          </CardTitle>
          <p className="text-xs text-ink/50">
            Select your current score on a scale from 1 (very low) to 10 (peak joy).
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Score Selector (Interactive pills + slider) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs font-semibold uppercase tracking-wider text-ink/60">
                Score: <strong className="text-ink text-sm">{SCORE_LABELS[score] || `${score} / 10`}</strong>
              </Label>
            </div>

            {/* Quick 1-10 Pill Buttons for Fast Mobile Tap */}
            <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setScore(s)}
                  className={`h-9 rounded-xl text-xs font-semibold transition-all ${
                    score === s
                      ? "bg-sage text-parchment shadow-sm scale-105"
                      : "bg-white border border-ink/10 text-ink/70 hover:border-ink/30 hover:bg-ink/5"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>

            <input
              type="range"
              min={1}
              max={10}
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
              className="w-full mt-2 accent-sage cursor-pointer"
            />
          </div>

          {/* Primary Emotion Selector */}
          <div>
            <Label className="text-xs font-semibold uppercase tracking-wider text-ink/60 block mb-2">
              Primary emotion
            </Label>
            <div className="flex flex-wrap gap-2">
              {LABELS.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => setLabel(item.value)}
                  className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all ${
                    label === item.value
                      ? "bg-ink text-parchment font-semibold shadow-xs"
                      : "bg-white border border-ink/15 text-ink/75 hover:border-ink/30"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Optional Notes */}
          <div>
            <Label htmlFor="notes" className="text-xs font-semibold uppercase tracking-wider text-ink/60 block mb-1">
              Personal Reflection / Notes (optional)
            </Label>
            <textarea
              id="notes"
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full rounded-xl border border-ink/15 bg-white p-3 text-sm text-ink placeholder:text-warm focus:outline-none focus:ring-2 focus:ring-sage focus:border-sage transition-all"
              placeholder="What events, thoughts, or interactions shaped how you feel?"
            />
          </div>

          <div className="flex items-center gap-3 pt-1">
            <Button
              onClick={submit}
              disabled={saving}
              className="bg-sage text-parchment hover:bg-ink rounded-full px-6 py-2.5 text-xs font-semibold shadow-sm transition-all active:scale-95"
            >
              {saving ? "Saving..." : "Log Daily Mood"}
            </Button>
            {submitted && (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-600 animate-in fade-in">
                <CheckCircle2 className="h-4 w-4" />
                Mood logged successfully!
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* ── 30-Day Score Trend Chart ────────────────────────────────────── */}
      <Card className="shadow-xs border border-ink/8">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-base font-semibold text-ink">30-Day Score Trend</CardTitle>
            <p className="text-xs text-ink/50 mt-0.5">Continuous visual tracking over the past month.</p>
          </div>
          {stats && (
            <div className="text-right">
              <span className="text-[10px] uppercase font-mono-mb tracking-wider text-warm block">30d Avg</span>
              <strong className="text-sm font-semibold text-ink">{stats.avg_score.toFixed(1)} / 10</strong>
            </div>
          )}
        </CardHeader>
        <CardContent>
          <MoodChart data={history} />
        </CardContent>
      </Card>

      {/* ── Recent Entries List ─────────────────────────────────────────── */}
      <Card className="shadow-xs border border-ink/8">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold text-ink">Recent Entries</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <p className="text-xs text-ink/50 py-4 text-center">
              No mood entries logged yet. Choose a score above to record your first entry.
            </p>
          ) : (
            <div className="divide-y divide-ink/8">
              {history.map((h) => (
                <div key={h.id} className="py-3.5 first:pt-0 last:pb-0 flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-ink capitalize">{h.mood_label || "Score"}</span>
                      {h.auto_detected && (
                        <span className="text-[10px] bg-sage/15 text-sage px-2 py-0.5 rounded-full font-medium">
                          AI detected
                        </span>
                      )}
                      <span className="text-xs text-ink/40">· {formatIndianDateTime(h.logged_at)}</span>
                    </div>
                    {h.notes && <p className="text-xs text-ink/70 mt-1 leading-relaxed">{h.notes}</p>}
                  </div>
                  <span className="text-sm font-bold text-sage shrink-0 bg-sage/10 px-2.5 py-1 rounded-xl">
                    {h.mood_score}/10
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
