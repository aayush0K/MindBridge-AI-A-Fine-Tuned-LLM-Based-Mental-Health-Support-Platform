"use client";

interface Props {
  suggestions: string[];
  onSelect: (text: string) => void;
}

export function QuickReplies({ suggestions, onSelect }: Props) {
  if (!suggestions.length) return null;
  return (
    <div className="flex flex-wrap gap-2 px-4 pb-2">
      {suggestions.map((s) => (
        <button
          key={s}
          type="button"
          onClick={() => onSelect(s)}
          className="rounded-full border border-sage/30 text-sage px-3 py-1 text-xs hover:bg-sage/10 transition-colors duration-300 ease-mb-ease"
        >
          {s}
        </button>
      ))}
    </div>
  );
}
