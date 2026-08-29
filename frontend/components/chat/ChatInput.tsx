"use client";

import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
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
    <div className="border-t border-slate-200 bg-white p-4">
      <div className="flex gap-2 items-end max-w-4xl mx-auto">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={disabled}
          placeholder="Share what's on your mind..."
          rows={1}
          className="flex-1 resize-none rounded-xl border border-ink/15 px-4 py-3 text-sm text-ink placeholder:text-warm focus:outline-none focus:ring-1 focus:ring-sage focus:border-sage min-h-[44px] max-h-32 transition-colors duration-300 ease-mb-ease"
        />
        <Button onClick={submit} disabled={disabled || !text.trim()} size="default" className="shrink-0">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
