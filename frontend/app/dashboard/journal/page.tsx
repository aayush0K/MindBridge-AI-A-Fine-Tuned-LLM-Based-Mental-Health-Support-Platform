"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, Trash2, Edit3, BookOpen, Search, Sparkles, Check, X, ArrowLeft } from "lucide-react";
import { journalApi } from "@/lib/api";
import { formatIndianDateTime } from "@/lib/utils";

interface JournalEntry {
  id: string;
  title: string;
  content: string;
  mood_tag?: string;
  created_at: string;
  updated_at: string;
}

const MOOD_TAGS = [
  "Calm 🌿",
  "Reflective 💭",
  "Hopeful ✨",
  "Grateful 🙏",
  "Anxious 😟",
  "Stressed ⚡",
  "Tired 🌙",
];

export default function JournalPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Form State
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [moodTag, setMoodTag] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const res = await journalApi.list();
      setEntries(res.data);
    } catch (err) {
      console.error("Failed to load journal entries", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setSaving(true);
    try {
      if (editingId) {
        await journalApi.update(editingId, {
          title: title.trim() || "Untitled Reflection",
          content: content.trim(),
          mood_tag: moodTag || undefined,
        });
      } else {
        await journalApi.create({
          title: title.trim() || "Untitled Reflection",
          content: content.trim(),
          mood_tag: moodTag || undefined,
        });
      }
      resetForm();
      await fetchEntries();
    } catch (err) {
      console.error("Failed to save entry", err);
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (entry: JournalEntry) => {
    setEditingId(entry.id);
    setTitle(entry.title);
    setContent(entry.content);
    setMoodTag(entry.mood_tag || "");
    setIsCreating(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this journal entry?")) return;
    try {
      await journalApi.delete(id);
      setEntries(entries.filter((e) => e.id !== id));
      if (editingId === id) resetForm();
    } catch (err) {
      console.error("Failed to delete entry", err);
    }
  };

  const resetForm = () => {
    setTitle("");
    setContent("");
    setMoodTag("");
    setEditingId(null);
    setIsCreating(false);
  };

  const filteredEntries = entries.filter(
    (e) =>
      e.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (e.mood_tag && e.mood_tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="h-full flex flex-col bg-parchment overflow-y-auto">
      {/* Header */}
      <header className="border-b border-ink/8 bg-white/80 backdrop-blur-sm px-4 md:px-8 py-3.5 md:py-4 flex items-center justify-between sticky top-0 z-20 shadow-xs">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Link
              href="/dashboard"
              className="hidden md:inline-flex items-center gap-1.5 text-xs font-medium text-ink/70 hover:text-ink bg-parchment hover:bg-parchment-dim border border-ink/10 px-3 py-1 rounded-full transition-all"
            >
              <ArrowLeft className="h-3 w-3" />
              <span>Dashboard</span>
            </Link>
          </div>
          <h1 className="text-lg md:text-2xl font-bold text-ink flex items-center gap-2 font-display">
            <BookOpen className="h-5 w-5 text-indigo-600" />
            <span>Private Journal</span>
          </h1>
          <p className="text-xs text-ink/50 mt-0.5 hidden sm:block">
            Your encrypted, safe space for emotional decompression and personal thoughts.
          </p>
        </div>

        {!isCreating && (
          <button
            onClick={() => setIsCreating(true)}
            className="inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-4 py-2 text-xs md:text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 active:scale-95 transition-all"
          >
            <Plus className="h-4 w-4 stroke-[2.5]" />
            <span>New Entry</span>
          </button>
        )}
      </header>

      <div className="p-4 md:p-8 max-w-4xl mx-auto w-full space-y-6 flex-1">
        {/* Entry Creator / Editor Modal Card */}
        {isCreating && (
          <form
            onSubmit={handleCreate}
            className="rounded-3xl border border-indigo-100 bg-white p-5 md:p-6 shadow-md space-y-4 animate-in fade-in duration-200"
          >
            <div className="flex items-center justify-between border-b border-ink/5 pb-3">
              <h2 className="text-base font-semibold text-ink flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-500" />
                {editingId ? "Edit Journal Entry" : "Write a New Reflection"}
              </h2>
              <button
                type="button"
                onClick={resetForm}
                className="rounded-full p-1.5 text-ink/40 hover:bg-ink/5 hover:text-ink transition"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink/60 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Thoughts on today's classes and feelings..."
                  className="w-full rounded-xl border border-ink/15 px-4 py-2.5 text-sm text-ink placeholder:text-warm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink/60 mb-1.5">
                  Mood Tag (Optional)
                </label>
                <div className="flex flex-wrap gap-2">
                  {MOOD_TAGS.map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => setMoodTag(moodTag === tag ? "" : tag)}
                      className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                        moodTag === tag
                          ? "bg-indigo-600 text-white shadow-xs"
                          : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink/60 mb-1">
                  Reflection Content
                </label>
                <textarea
                  rows={6}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="How are you feeling right now? What happened today that stood out to you? Write freely..."
                  required
                  className="w-full rounded-2xl border border-ink/15 p-4 text-sm text-ink placeholder:text-warm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all leading-relaxed"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={resetForm}
                className="rounded-full px-4 py-2 text-xs font-medium text-ink/60 hover:bg-ink/5 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-5 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition shadow-sm active:scale-95"
              >
                <Check className="h-4 w-4" />
                {saving ? "Saving..." : editingId ? "Update Entry" : "Save Entry"}
              </button>
            </div>
          </form>
        )}

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-3.5 h-4 w-4 text-ink/40" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search journal entries by keyword or mood tag..."
            className="w-full rounded-2xl border border-ink/10 bg-white pl-11 pr-4 py-3 text-sm text-ink placeholder:text-warm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 shadow-xs transition-all"
          />
        </div>

        {/* Entries List */}
        {loading ? (
          <div className="py-16 text-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mx-auto" />
            <p className="text-xs text-ink/50 mt-3">Loading your reflections...</p>
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-ink/15 bg-white/80 p-10 text-center space-y-3">
            <div className="h-12 w-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
              <BookOpen className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-ink">No Journal Entries Found</h3>
            <p className="text-xs text-ink/60 max-w-sm mx-auto leading-relaxed">
              {searchQuery
                ? "No entries match your search query. Try different keywords."
                : "Journaling is a proven way to process emotions and decompress. Write your first reflection today!"}
            </p>
            {!isCreating && (
              <button
                onClick={() => setIsCreating(true)}
                className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 transition shadow-sm active:scale-95"
              >
                <Plus className="h-4 w-4" />
                <span>Write Your First Entry</span>
              </button>
            )}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {filteredEntries.map((entry) => (
              <div
                key={entry.id}
                className="rounded-3xl border border-ink/8 bg-white p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-ink text-base line-clamp-1">{entry.title}</h3>
                    {entry.mood_tag && (
                      <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 shrink-0">
                        {entry.mood_tag}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-ink/40 mt-1">
                    {formatIndianDateTime(entry.created_at)}
                  </p>
                  <p className="text-xs text-ink/70 mt-3 whitespace-pre-line line-clamp-4 leading-relaxed">
                    {entry.content}
                  </p>
                </div>

                <div className="flex items-center justify-end gap-2 border-t border-ink/5 pt-3 mt-4">
                  <button
                    onClick={() => startEdit(entry)}
                    className="rounded-lg p-1.5 text-ink/40 hover:bg-ink/5 hover:text-ink transition"
                    title="Edit Entry"
                  >
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="rounded-lg p-1.5 text-ink/40 hover:bg-rose-50 hover:text-rose-600 transition"
                    title="Delete Entry"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
