"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  MessageCircle,
  Heart,
  FileText,
  Download,
  BookOpen,
  LifeBuoy,
  Plus,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MoodChart } from "@/components/dashboard/MoodChart";
import { moodApi, chatApi, reportApi } from "@/lib/api";
import { formatIndianDate } from "@/lib/utils";
import type { ChatSession } from "@/types/chat.types";

interface Report {
  id: string;
  period_start: string;
  period_end: string;
  summary: string;
  created_at: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<{ avg_score: number; trend: string; total_logs: number } | null>(null);
  const [history, setHistory] = useState<{ logged_at: string; mood_score: number }[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    moodApi.stats().then((r) => setStats(r.data)).catch(() => {});
    moodApi.history(30).then((r) => setHistory(r.data)).catch(() => {});
    chatApi.getSessions().then((r) => setSessions(r.data.slice(0, 5))).catch(() => {});
    reportApi.list().then((r) => setReports(r.data.slice(0, 3))).catch(() => {});
  }, []);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      await reportApi.generate(30);
      const r = await reportApi.list();
      setReports(r.data.slice(0, 3));
    } catch {
      // handle error silently
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (reportId: string) => {
    try {
      const response = await reportApi.download(reportId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `MindBridge_Report_${reportId.slice(0, 8)}.txt`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      // handle error silently
    }
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 bg-parchment max-w-5xl mx-auto space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl md:text-3xl text-ink font-semibold">Dashboard</h1>
          <p className="text-xs md:text-sm text-ink/60 mt-0.5">Your personal emotional health & AI companion space.</p>
        </div>
      </div>

      {/* ── Feature Cards (Quick Launch Grid for Mobile & Desktop) ────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Link
          href="/dashboard/chat"
          className="p-4 rounded-2xl bg-white border border-ink/8 hover:border-ink/20 shadow-sm transition-all hover:shadow hover:-translate-y-0.5 flex flex-col justify-between"
        >
          <div className="p-2 w-fit rounded-xl bg-sage/15 text-sage mb-2">
            <MessageCircle className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-ink">AI Chat</h3>
            <p className="text-[11px] text-ink/50 mt-0.5">Empathetic companion</p>
          </div>
        </Link>

        <Link
          href="/dashboard/mood"
          className="p-4 rounded-2xl bg-white border border-ink/8 hover:border-ink/20 shadow-sm transition-all hover:shadow hover:-translate-y-0.5 flex flex-col justify-between"
        >
          <div className="p-2 w-fit rounded-xl bg-rose-500/15 text-rose-600 mb-2">
            <Heart className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-ink">Mood Tracker</h3>
            <p className="text-[11px] text-ink/50 mt-0.5">Log & view emotional trends</p>
          </div>
        </Link>

        <Link
          href="/dashboard/journal"
          className="p-4 rounded-2xl bg-white border border-ink/8 hover:border-ink/20 shadow-sm transition-all hover:shadow hover:-translate-y-0.5 flex flex-col justify-between"
        >
          <div className="p-2 w-fit rounded-xl bg-indigo-500/15 text-indigo-600 mb-2">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-ink">Private Journal</h3>
            <p className="text-[11px] text-ink/50 mt-0.5">Reflections with AI prompts</p>
          </div>
        </Link>

        <Link
          href="/dashboard/resources"
          className="p-4 rounded-2xl bg-white border border-ink/8 hover:border-ink/20 shadow-sm transition-all hover:shadow hover:-translate-y-0.5 flex flex-col justify-between"
        >
          <div className="p-2 w-fit rounded-xl bg-emerald-500/15 text-emerald-600 mb-2">
            <LifeBuoy className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-ink">Crisis Helplines</h3>
            <p className="text-[11px] text-ink/50 mt-0.5">24x7 India verified support</p>
          </div>
        </Link>
      </div>

      {/* ── Key Metrics & Chart ───────────────────────────────────────────── */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="font-mono-mb text-xs uppercase tracking-wide text-warm">
              Wellness score (7d avg)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-display text-4xl text-ink font-semibold">
              {stats ? stats.avg_score.toFixed(1) : "—"}
              <span className="text-base font-normal text-warm">/10</span>
            </p>
            {stats && (
              <p className="text-xs text-slate-500 mt-1 capitalize">Trend: {stats.trend}</p>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="font-mono-mb text-xs uppercase tracking-wide text-warm">
              Mood history (30 days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <MoodChart data={history} />
          </CardContent>
        </Card>
      </div>

      {/* ── Action Buttons ────────────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-2.5">
        <Button
          variant="outline"
          onClick={handleGenerateReport}
          disabled={generating}
          className="border border-ink/20 text-ink hover:bg-ink/5 rounded-full text-xs transition-colors"
        >
          <FileText className="h-3.5 w-3.5 mr-2" />
          {generating ? "Generating..." : "Generate 30-Day Consultation Report"}
        </Button>
      </div>

      {/* ── Consultation Reports ──────────────────────────────────────────── */}
      {reports.length > 0 && (
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Consultation Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {reports.map((r) => (
                <li key={r.id} className="flex items-center justify-between rounded-xl border border-ink/8 px-4 py-3 bg-white">
                  <div>
                    <p className="font-medium text-sm text-ink">
                      {formatIndianDate(r.period_start)} — {formatIndianDate(r.period_end)}
                    </p>
                    <p className="text-xs text-ink/50 line-clamp-1">{r.summary.slice(0, 100)}...</p>
                  </div>
                  <button
                    onClick={() => handleDownload(r.id)}
                    className="p-2 rounded-full hover:bg-ink/5 transition-colors"
                    title="Download report"
                  >
                    <Download className="h-4 w-4 text-sage" />
                  </button>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* ── Recent Conversations ──────────────────────────────────────────── */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Recent conversations</CardTitle>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <p className="text-sm text-slate-500">No chats yet. Start your first conversation.</p>
          ) : (
            <ul className="space-y-2">
              {sessions.map((s) => (
                <li key={s.id} className="flex items-center justify-between rounded-xl border border-ink/8 px-4 py-3 bg-white hover:border-ink/20 transition-colors">
                  <div>
                    <p className="font-medium text-sm text-ink truncate max-w-xs">{s.title}</p>
                    <p className="text-xs text-ink/50">
                      {s.message_count} messages · {formatIndianDate(s.started_at)}
                    </p>
                  </div>
                  <Link href="/dashboard/chat">
                    <ArrowRight className="h-4 w-4 text-slate-400" />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
