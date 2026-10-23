"use client";

import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/types/chat.types";

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-2.5 md:gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-xs mt-0.5",
          isUser ? "bg-gold text-gold-dark ring-2 ring-gold/20" : "bg-sage/15 text-sage ring-2 ring-sage/20"
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div className={cn("max-w-[85%] md:max-w-[75%] space-y-1", isUser ? "items-end text-right" : "items-start text-left")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-xs text-left",
            isUser
              ? "bg-ink text-parchment rounded-tr-xs"
              : "bg-white border border-ink/8 text-ink rounded-tl-xs"
          )}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    </div>
  );
}
