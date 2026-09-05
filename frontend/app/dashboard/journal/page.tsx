"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Edit3, BookOpen, Search, Sparkles, Check, X } from "lucide-react";
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
    <div className="h-full flex flex-col bg-slate-50 overflow-y-auto">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-8 py-5 flex items-center justify-between sticky top-0 z-20">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-indigo-600" />
            Private Journal
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Your secure, private space for self-reflection and emotional expression.
          </p>
        </div>

        {!isCreating && (
          <button
            onClick={() => setIsCreating(true)}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 transition"
          >
            <Plus className="h-4 w-4" />
            New Entry
          </button>
        )}
      </header>

      <div className="p-8 max-w-5xl mx-auto w-full space-y-6 flex-1">
        {/* Entry Creator / Editor Modal Card */}
        {isCreating && (
          <form
            onSubmit={handleCreate}
            className="rounded-2xl border border-indigo-100 bg-white p-6 shadow-md space-y-4 animate-in fade-in duration-200"
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-500" />
                {editingId ? "Edit Journal Entry" : "Write a New Reflection"}
              </h2>
              <button
                type="button"
                onClick={resetForm}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Thoughts on today's lecture..."
                  className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
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
                          ? "bg-indigo-600 text-white"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Reflection Content
                </label>
                <textarea
                  rows={6}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="How are you feeling right now? What happened today that stood out to you? Write freely..."
                  required
                  className="w-full rounded-xl border border-slate-200 p-4 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={resetForm}
                className="rounded-xl px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition shadow-sm"
              >
                <Check className="h-4 w-4" />
                {saving ? "Saving..." : editingId ? "Update Entry" : "Save Entry"}
              </button>
            </div>
          </form>
        )}

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-3.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search journal entries by keyword or mood..."
            className="w-full rounded-xl border border-slate-200 bg-white pl-11 pr-4 py-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 shadow-sm"
          />
        </div>

        {/* Entries List */}
        {loading ? (
          <div className="py-16 text-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mx-auto" />
            <p className="text-sm text-slate-500 mt-3">Loading your reflections...</p>
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-12 text-center space-y-3">
            <div className="h-12 w-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
              <BookOpen className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-800">No Journal Entries Found</h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto">
              {searchQuery
                ? "No entries match your search query. Try different keywords."
                : "Journaling is a proven way to process emotions and decompress. Write your first reflection today!"}
            </p>
            {!isCreating && (
              <button
                onClick={() => setIsCreating(true)}
                className="mt-2 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition"
              >
                <Plus className="h-4 w-4" />
                Write Your First Entry
              </button>
            )}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {filteredEntries.map((entry) => (
              <div
                key={entry.id}
                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-slate-900 text-base">{entry.title}</h3>
                    {entry.mood_tag && (
                      <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 shrink-0">
                        {entry.mood_tag}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {formatIndianDateTime(entry.created_at)}
                  </p>
                  <p className="text-sm text-slate-600 mt-3 whitespace-pre-line line-clamp-4">
                    {entry.content}
                  </p>
                </div>

                <div className="flex items-center justify-end gap-2 border-t border-slate-100 pt-3 mt-4">
                  <button
                    onClick={() => startEdit(entry)}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
                    title="Edit Entry"
                  >
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 transition"
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
