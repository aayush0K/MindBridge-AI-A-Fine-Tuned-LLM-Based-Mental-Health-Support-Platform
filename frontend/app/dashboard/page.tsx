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
  Sparkles,
  TrendingUp,
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
    <div className="h-full overflow-y-auto p-4 md:p-8 bg-parchment max-w-5xl mx-auto space-y-6">
      {/* ── Welcome Hero Banner ────────────────────────────────────────── */}
      <div className="rounded-3xl border border-ink/8 bg-white/90 backdrop-blur-xs p-5 md:p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wider text-sage bg-sage/10 px-2.5 py-0.5 rounded-full">
              <Sparkles className="h-3 w-3" />
              Emotional Wellness Space
            </span>
          </div>
          <h1 className="font-display text-2xl md:text-3xl text-ink font-semibold tracking-tight">
            Welcome to MindBridge
          </h1>
          <p className="text-xs md:text-sm text-ink/60 max-w-lg">
            A compassionate space to speak freely, track emotional rhythms, and maintain your peace of mind.
          </p>
        </div>

        <Link
          href="/dashboard/chat"
          className="inline-flex items-center gap-2 rounded-full bg-ink hover:bg-ink-light text-parchment px-4 py-2.5 text-xs font-semibold shadow-sm hover:shadow transition-all shrink-0 active:scale-95"
        >
          <MessageCircle className="h-4 w-4 text-gold" />
          <span>Talk to AI Companion</span>
        </Link>
      </div>

      {/* ── 4 Quick-Launch Feature Cards ─────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        {/* Card 1: AI Chat */}
        <Link
          href="/dashboard/chat"
          className="group p-4 md:p-5 rounded-2xl bg-white border border-ink/8 hover:border-sage/40 shadow-xs hover:shadow-md hover:-translate-y-0.5 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="p-2.5 w-fit rounded-xl bg-sage/15 text-sage mb-3 group-hover:scale-110 transition-transform">
              <MessageCircle className="h-5 w-5" />
            </div>
            <h3 className="font-semibold text-sm md:text-base text-ink group-hover:text-sage transition-colors">
              AI Chat
            </h3>
            <p className="text-[11px] md:text-xs text-ink/50 mt-1 line-clamp-2 leading-relaxed">
              Empathetic, confidential companion ready to listen 24×7.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[11px] font-medium text-sage mt-3 pt-2 border-t border-ink/5">
            <span>Start chat</span>
            <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </Link>

        {/* Card 2: Mood Tracker */}
        <Link
          href="/dashboard/mood"
          className="group p-4 md:p-5 rounded-2xl bg-white border border-ink/8 hover:border-rose-300 shadow-xs hover:shadow-md hover:-translate-y-0.5 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="p-2.5 w-fit rounded-xl bg-rose-500/15 text-rose-600 mb-3 group-hover:scale-110 transition-transform">
              <Heart className="h-5 w-5" />
            </div>
            <h3 className="font-semibold text-sm md:text-base text-ink group-hover:text-rose-600 transition-colors">
              Mood Tracker
            </h3>
            <p className="text-[11px] md:text-xs text-ink/50 mt-1 line-clamp-2 leading-relaxed">
              Log daily feelings and explore AI emotional trends.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[11px] font-medium text-rose-600 mt-3 pt-2 border-t border-ink/5">
            <span>Log mood</span>
            <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </Link>

        {/* Card 3: Private Journal */}
        <Link
          href="/dashboard/journal"
          className="group p-4 md:p-5 rounded-2xl bg-white border border-ink/8 hover:border-indigo-300 shadow-xs hover:shadow-md hover:-translate-y-0.5 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="p-2.5 w-fit rounded-xl bg-indigo-500/15 text-indigo-600 mb-3 group-hover:scale-110 transition-transform">
              <BookOpen className="h-5 w-5" />
            </div>
            <h3 className="font-semibold text-sm md:text-base text-ink group-hover:text-indigo-600 transition-colors">
              Private Journal
            </h3>
            <p className="text-[11px] md:text-xs text-ink/50 mt-1 line-clamp-2 leading-relaxed">
              Reflections, emotional release, and thought prompts.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[11px] font-medium text-indigo-600 mt-3 pt-2 border-t border-ink/5">
            <span>Write entry</span>
            <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </Link>

        {/* Card 4: Crisis Helplines */}
        <Link
          href="/dashboard/resources"
          className="group p-4 md:p-5 rounded-2xl bg-white border border-ink/8 hover:border-emerald-300 shadow-xs hover:shadow-md hover:-translate-y-0.5 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="p-2.5 w-fit rounded-xl bg-emerald-500/15 text-emerald-600 mb-3 group-hover:scale-110 transition-transform">
              <LifeBuoy className="h-5 w-5" />
            </div>
            <h3 className="font-semibold text-sm md:text-base text-ink group-hover:text-emerald-600 transition-colors">
              Crisis Helplines
            </h3>
            <p className="text-[11px] md:text-xs text-ink/50 mt-1 line-clamp-2 leading-relaxed">
              Verified 24×7 India emergency lines (112, 14416).
            </p>
          </div>
          <div className="flex items-center gap-1 text-[11px] font-medium text-emerald-600 mt-3 pt-2 border-t border-ink/5">
            <span>Emergency lines</span>
            <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </Link>
      </div>

      {/* ── Key Metrics & Chart ───────────────────────────────────────────── */}
      <div className="grid gap-4 md:grid-cols-3">
        {/* Wellness Score Card */}
        <Card className="shadow-xs border border-ink/8 flex flex-col justify-between">
          <CardHeader className="pb-2">
            <CardTitle className="font-mono-mb text-xs uppercase tracking-wider text-warm font-medium flex items-center justify-between">
              <span>Wellness Score (7d avg)</span>
              <TrendingUp className="h-3.5 w-3.5 text-sage" />
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="flex items-baseline gap-1">
              <span className="font-display text-4xl text-ink font-semibold">
                {stats ? stats.avg_score.toFixed(1) : "—"}
              </span>
              <span className="text-sm font-normal text-warm">/ 10</span>
            </div>
            {stats && (
              <div className="mt-2.5 flex items-center gap-2">
                <span className="inline-flex items-center text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-sage/10 text-sage capitalize">
                  Trend: {stats.trend}
                </span>
                <span className="text-xs text-ink/40">
                  {stats.total_logs} {stats.total_logs === 1 ? "log" : "logs"}
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Mood History Chart */}
        <Card className="md:col-span-2 shadow-xs border border-ink/8">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="font-mono-mb text-xs uppercase tracking-wider text-warm font-medium">
              Mood Rhythm (30 Days)
            </CardTitle>
            <Link
              href="/dashboard/mood"
              className="text-xs text-sage hover:text-ink font-medium flex items-center gap-1"
            >
              <span>Detailed analysis</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </CardHeader>
          <CardContent className="pt-2">
            <MoodChart data={history} />
          </CardContent>
        </Card>
      </div>

      {/* ── Consultation Reports ──────────────────────────────────────────── */}
      <Card className="shadow-xs border border-ink/8">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3">
          <div>
            <CardTitle className="text-base font-semibold text-ink">Clinical Consultation Reports</CardTitle>
            <p className="text-xs text-ink/50 mt-0.5">
              Generate structured 30-day summaries of your mood and themes to share with your counselor or doctor.
            </p>
          </div>
          <Button
            variant="outline"
            onClick={handleGenerateReport}
            disabled={generating}
            className="border border-ink/20 text-ink hover:bg-ink/5 rounded-full text-xs transition-colors shrink-0"
          >
            <FileText className="h-3.5 w-3.5 mr-2" />
            {generating ? "Generating Report..." : "Generate 30-Day Report"}
          </Button>
        </CardHeader>
        {reports.length > 0 && (
          <CardContent>
            <ul className="space-y-2">
              {reports.map((r) => (
                <li
                  key={r.id}
                  className="flex items-center justify-between rounded-xl border border-ink/8 px-4 py-3 bg-white hover:border-ink/20 transition-colors"
                >
                  <div className="pr-4">
                    <p className="font-medium text-sm text-ink">
                      {formatIndianDate(r.period_start)} — {formatIndianDate(r.period_end)}
                    </p>
                    <p className="text-xs text-ink/50 line-clamp-1 mt-0.5">{r.summary.slice(0, 100)}...</p>
                  </div>
                  <button
                    onClick={() => handleDownload(r.id)}
                    className="p-2 rounded-full hover:bg-ink/5 text-sage hover:text-ink transition-colors"
                    title="Download report"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </li>
              ))}
            </ul>
          </CardContent>
        )}
      </Card>

      {/* ── Recent Conversations ──────────────────────────────────────────── */}
      <Card className="shadow-xs border border-ink/8">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-base font-semibold text-ink">Recent Conversations</CardTitle>
            <p className="text-xs text-ink/50 mt-0.5">Pick up where you left off with your AI companion.</p>
          </div>
          <Link
            href="/dashboard/chat"
            className="text-xs text-sage hover:text-ink font-medium flex items-center gap-1"
          >
            <span>Open Chat</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <div className="py-8 text-center text-xs text-ink/50">
              No chat sessions yet. Click "Talk to AI Companion" above to begin your first conversation.
            </div>
          ) : (
            <ul className="space-y-2">
              {sessions.map((s) => (
                <li
                  key={s.id}
                  className="flex items-center justify-between rounded-xl border border-ink/8 px-4 py-3 bg-white hover:border-ink/20 transition-colors"
                >
                  <div>
                    <p className="font-medium text-sm text-ink truncate max-w-xs md:max-w-md">{s.title || "Conversation"}</p>
                    <p className="text-xs text-ink/50 mt-0.5">
                      {s.message_count} messages · {formatIndianDate(s.started_at)}
                    </p>
                  </div>
                  <Link
                    href="/dashboard/chat"
                    className="p-2 rounded-full hover:bg-ink/5 text-ink/40 hover:text-ink transition-colors"
                  >
                    <ArrowRight className="h-4 w-4" />
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
