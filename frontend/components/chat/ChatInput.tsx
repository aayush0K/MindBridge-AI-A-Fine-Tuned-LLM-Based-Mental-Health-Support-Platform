"use client";

import { Send } from "lucide-react";
import { useState, KeyboardEvent } from "react";

interface Props {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  const submit = () => {
    const msg = text.trim();
    if (!msg || disabled) return;
    onSend(msg);
    setText("");
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="border-t border-ink/8 bg-white/90 backdrop-blur-md px-3.5 md:px-6 py-3">
      <div className="flex gap-2 items-end max-w-3xl mx-auto bg-parchment/60 rounded-2xl border border-ink/10 p-1.5 focus-within:border-sage/60 focus-within:ring-2 focus-within:ring-sage/20 transition-all shadow-xs">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={disabled}
          placeholder="Share what's on your mind... (Press Enter to send)"
          rows={1}
          className="flex-1 resize-none bg-transparent px-3 py-2 text-sm text-ink placeholder:text-warm focus:outline-none min-h-[40px] max-h-32"
        />
        <button
          type="button"
          onClick={submit}
          disabled={disabled || !text.trim()}
          className="h-9 w-9 rounded-xl bg-sage hover:bg-ink text-parchment flex items-center justify-center shrink-0 disabled:opacity-40 disabled:hover:bg-sage transition-all shadow-sm active:scale-95"
          aria-label="Send message"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
      <p className="text-[10px] text-center text-ink/40 mt-1.5">
        MindBridge AI offers compassionate emotional support · In emergencies, call 112 or Tele-MANAS (14416).
      </p>
    </div>
  );
}
