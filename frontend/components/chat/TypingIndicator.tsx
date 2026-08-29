"use client";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3 bg-white border border-sage/20 rounded-2xl w-fit">
      <span className="h-2 w-2 animate-bounce rounded-full bg-sage [animation-delay:-0.3s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-sage [animation-delay:-0.15s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-sage" />
    </div>
  );
}
