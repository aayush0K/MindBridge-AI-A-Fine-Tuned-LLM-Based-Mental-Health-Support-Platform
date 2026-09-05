"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, MessageCircle, Heart, FileText, Download } from "lucide-react";
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
    <div className="h-full overflow-y-auto p-6 bg-parchment">
      <h1 className="font-display text-2xl text-ink mb-6">Dashboard</h1>

      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="font-mono-mb text-xs uppercase tracking-wide text-warm">Wellness score (7d avg)</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-display text-4xl text-ink">
              {stats ? stats.avg_score.toFixed(1) : "—"}
              <span className="text-base font-normal text-warm">/10</span>
            </p>
            {stats && (
              <p className="text-xs text-slate-500 mt-1 capitalize">Trend: {stats.trend}</p>
            )}
          </CardContent>
        </Card>
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="font-mono-mb text-xs uppercase tracking-wide text-warm">Mood history (30 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <MoodChart data={history} />
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        <Link href="/dashboard/chat">
          <Button className="bg-sage text-parchment hover:bg-ink rounded-full transition-colors duration-300 ease-mb-ease">
            <MessageCircle className="h-4 w-4 mr-2" />
            Start chat
          </Button>
        </Link>
        <Link href="/dashboard/mood">
          <Button variant="outline" className="border border-ink/20 text-ink hover:bg-ink/5 rounded-full transition-colors duration-300 ease-mb-ease">
            <Heart className="h-4 w-4 mr-2" />
            Log mood
          </Button>
        </Link>
        <Button
          variant="outline"
          onClick={handleGenerateReport}
          disabled={generating}
          className="border border-ink/20 text-ink hover:bg-ink/5 rounded-full transition-colors duration-300 ease-mb-ease"
        >
          <FileText className="h-4 w-4 mr-2" />
          {generating ? "Generating..." : "Generate 30-Day Report"}
        </Button>
      </div>

      {/* ── Wellness Reports ──────────────────────────────────────────────── */}
      {reports.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Consultation Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {reports.map((r) => (
                <li key={r.id} className="flex items-center justify-between rounded-xl border border-ink/8 px-4 py-3">
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

      <Card>
        <CardHeader>
          <CardTitle>Recent conversations</CardTitle>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <p className="text-sm text-slate-500">No chats yet. Start your first conversation.</p>
          ) : (
            <ul className="space-y-2">
              {sessions.map((s) => (
                <li key={s.id} className="flex items-center justify-between rounded-xl border border-ink/8 px-4 py-3 hover:bg-white transition-colors duration-300 ease-mb-ease">
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
