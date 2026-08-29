"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface TrendPoint {
  date: string;
  avg_score: number;
  dominant_mood: string | null;
}

interface MoodTrendData {
  daily_trend: TrendPoint[];
  weekly_avg: number;
  monthly_avg: number;
  most_frequent_emotions: { label: string; count: number }[];
  total_auto_detected: number;
  trend_direction: string;
}

const MOOD_COLORS: Record<string, string> = {
  Happy: "#4CAF50",
  Sad: "#5C6BC0",
  Anxious: "#FF9800",
  Angry: "#F44336",
  Lonely: "#7E57C2",
  Stressed: "#FF5722",
  Confused: "#FFC107",
  Neutral: "#78909C",
};

const TREND_EMOJI: Record<string, string> = {
  improving: "📈",
  declining: "📉",
  stable: "➡️",
};

export function AutoMoodTrends({ data }: { data: MoodTrendData | null }) {
  if (!data || !data.daily_trend.length) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-ink/40">
        Chat with MindBridge to see your automated mood trends
      </div>
    );
  }

  const chartData = data.daily_trend.map((d) => ({
    date: new Date(d.date).toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
    }),
    score: d.avg_score,
    mood: d.dominant_mood || "Neutral",
  }));

  return (
    <div className="space-y-4">
      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border border-ink/10 p-3 text-center">
          <div className="text-xs text-ink/50">Weekly Avg</div>
          <div className="font-display text-xl text-ink">
            {data.weekly_avg.toFixed(1)}
          </div>
        </div>
        <div className="rounded-xl border border-ink/10 p-3 text-center">
          <div className="text-xs text-ink/50">Monthly Avg</div>
          <div className="font-display text-xl text-ink">
            {data.monthly_avg.toFixed(1)}
          </div>
        </div>
        <div className="rounded-xl border border-ink/10 p-3 text-center">
          <div className="text-xs text-ink/50">Trend</div>
          <div className="font-display text-xl text-ink">
            {TREND_EMOJI[data.trend_direction] || "➡️"}{" "}
            <span className="text-sm capitalize">{data.trend_direction}</span>
          </div>
        </div>
      </div>

      {/* Daily Score Chart */}
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E0D2" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis domain={[1, 10]} tick={{ fontSize: 11 }} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload;
                return (
                  <div className="rounded-lg bg-white border border-ink/10 p-2 text-sm shadow-md">
                    <p className="font-medium text-ink">{d.date}</p>
                    <p className="text-ink/60">
                      Score: <strong>{d.score}/10</strong>
                    </p>
                    <p className="text-ink/60">
                      Mood: <strong>{d.mood}</strong>
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="score" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={MOOD_COLORS[entry.mood] || "#78909C"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Frequent Emotions */}
      {data.most_frequent_emotions.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-ink/70 mb-2">
            Most Frequent Emotions
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.most_frequent_emotions.map((e) => (
              <span
                key={e.label}
                className="rounded-full px-3 py-1 text-xs border border-ink/15"
                style={{
                  backgroundColor: (MOOD_COLORS[e.label] || "#78909C") + "20",
                  color: MOOD_COLORS[e.label] || "#78909C",
                }}
              >
                {e.label} ({e.count})
              </span>
            ))}
          </div>
        </div>
      )}

      <p className="text-xs text-ink/40 text-right">
        Based on {data.total_auto_detected} auto-detected entries
      </p>
    </div>
  );
}
