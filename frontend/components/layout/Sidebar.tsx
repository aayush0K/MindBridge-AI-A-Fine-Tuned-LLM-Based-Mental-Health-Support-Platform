"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, MessageCircle, Heart, BookOpen, LifeBuoy, Settings, LogOut, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { clearTokens } from "@/lib/api";
import { useChatStore } from "@/store/chatStore";
import { chatApi } from "@/lib/api";
import { useEffect } from "react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/chat", label: "Chat", icon: MessageCircle },
  { href: "/dashboard/mood", label: "Mood Tracker", icon: Heart },
  { href: "/dashboard/journal", label: "Journal", icon: BookOpen },
  { href: "/dashboard/resources", label: "Resources", icon: LifeBuoy },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { sessions, activeSessionId, setSessions, setActiveSession, setMessages, reset } = useChatStore();

  useEffect(() => {
    chatApi.getSessions().then((r) => setSessions(r.data)).catch(() => {});
  }, [setSessions]);

  const newChat = () => {
    reset();
    router.push("/dashboard/chat");
  };

  const openSession = async (id: string) => {
    setActiveSession(id);
    const { data } = await chatApi.getMessages(id);
    setMessages(data);
    router.push("/dashboard/chat");
  };

  const logout = () => {
    clearTokens();
    reset();
    router.push("/login");
  };

  return (
    <aside className="hidden md:flex w-60 flex-col border-r border-white/5 bg-ink h-full">
      <div className="p-4 border-b border-white/5">
        <Link href="/dashboard" className="flex items-center gap-2 font-display text-lg text-parchment">
          MindBridge
        </Link>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors duration-300 ease-mb-ease",
              pathname === href ? "bg-sage/15 text-gold font-medium" : "text-parchment/50 hover:bg-white/5 hover:text-parchment"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
      {pathname.includes("/chat") && (
        <div className="px-3 pb-2">
          <button
            type="button"
            onClick={newChat}
            className="flex w-full items-center gap-2 rounded-full bg-gold px-3 py-2 text-sm text-gold-dark hover:bg-gold/90 transition-colors duration-300 ease-mb-ease"
          >
            <Plus className="h-4 w-4" />
            New chat
          </button>
          {sessions.length > 0 && (
            <p className="text-[10px] text-parchment/30 uppercase tracking-wider mt-3 mb-1 px-2">Recent chats</p>
          )}
          <div className="max-h-48 overflow-y-auto space-y-1">
            {sessions.slice(0, 10).map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => openSession(s.id)}
                className={cn(
                  "w-full truncate rounded px-2 py-1.5 text-left text-xs transition-colors duration-300 ease-mb-ease",
                  activeSessionId === s.id
                    ? "bg-sage/15 text-gold font-medium"
                    : "text-parchment/40 hover:bg-white/5 hover:text-parchment/80"
                )}
              >
                {s.title}
              </button>
            ))}
          </div>
        </div>
      )}
      <div className="p-3 border-t border-white/5">
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-parchment/50 hover:bg-white/5 hover:text-parchment transition-colors duration-300 ease-mb-ease"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}
