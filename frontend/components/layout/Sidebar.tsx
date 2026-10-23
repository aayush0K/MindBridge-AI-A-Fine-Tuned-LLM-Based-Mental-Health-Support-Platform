"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  MessageCircle,
  Heart,
  BookOpen,
  LifeBuoy,
  Settings,
  LogOut,
  Plus,
  ArrowLeft,
  X,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { clearTokens } from "@/lib/api";
import { useChatStore } from "@/store/chatStore";
import { chatApi } from "@/lib/api";
import { useEffect } from "react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/chat", label: "AI Chat", icon: MessageCircle },
  { href: "/dashboard/mood", label: "Mood Tracker", icon: Heart },
  { href: "/dashboard/journal", label: "Private Journal", icon: BookOpen },
  { href: "/dashboard/resources", label: "Crisis Resources", icon: LifeBuoy },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ mobileOpen = false, onMobileClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { sessions, activeSessionId, setSessions, setActiveSession, setMessages, reset } = useChatStore();

  useEffect(() => {
    chatApi.getSessions().then((r) => setSessions(r.data)).catch(() => {});
  }, [setSessions]);

  const handleNavClick = () => {
    if (onMobileClose) onMobileClose();
  };

  const newChat = () => {
    reset();
    router.push("/dashboard/chat");
    if (onMobileClose) onMobileClose();
  };

  const openSession = async (id: string) => {
    setActiveSession(id);
    const { data } = await chatApi.getMessages(id);
    setMessages(data);
    router.push("/dashboard/chat");
    if (onMobileClose) onMobileClose();
  };

  const logout = () => {
    clearTokens();
    reset();
    router.push("/login");
    if (onMobileClose) onMobileClose();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={onMobileClose}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          "w-64 flex-col border-r border-white/5 bg-ink h-full transition-transform duration-300 z-50",
          "fixed inset-y-0 left-0 md:static md:flex",
          mobileOpen ? "flex translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-white/5 flex items-center justify-between">
          <Link
            href="/dashboard"
            onClick={handleNavClick}
            className="flex items-center gap-2.5 group"
          >
            <div className="h-8 w-8 rounded-xl bg-sage/20 border border-sage/30 flex items-center justify-center text-sage group-hover:text-gold transition-colors">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <span className="font-display text-lg text-parchment font-semibold tracking-wide block leading-none">
                MindBridge
              </span>
              <span className="text-[10px] text-parchment/40 uppercase tracking-widest mt-1 block">
                Mental Health AI
              </span>
            </div>
          </Link>

          <div className="flex items-center gap-2">
            {/* Back to landing page */}
            <Link
              href="/"
              title="Back to Landing Page"
              className="flex items-center gap-1 text-[11px] text-parchment/60 hover:text-parchment bg-white/5 hover:bg-white/10 px-2 py-1 rounded-md transition-colors"
            >
              <ArrowLeft className="h-3 w-3" />
              <span>Home</span>
            </Link>

            {/* Mobile close button */}
            <button
              type="button"
              onClick={onMobileClose}
              className="p-1 rounded text-parchment/60 hover:text-parchment hover:bg-white/10 md:hidden"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {nav.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={handleNavClick}
                className={cn(
                  "flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm transition-all duration-200",
                  active
                    ? "bg-white/10 text-gold font-medium shadow-xs border border-white/5"
                    : "text-parchment/60 hover:bg-white/5 hover:text-parchment"
                )}
              >
                <Icon className={cn("h-4 w-4", active ? "text-gold" : "text-parchment/50")} />
                <span>{label}</span>
              </Link>
            );
          })}

          {/* New Chat Button & Recent Chats */}
          <div className="pt-4 mt-2 border-t border-white/5">
            <button
              type="button"
              onClick={newChat}
              className="flex w-full items-center justify-center gap-2 rounded-full bg-gold px-3 py-2.5 text-sm font-semibold text-gold-dark hover:bg-gold/90 shadow-sm hover:shadow-md transition-all active:scale-98"
            >
              <Plus className="h-4 w-4 stroke-[2.5]" />
              <span>New Chat</span>
            </button>

            {sessions.length > 0 && (
              <p className="text-[10px] text-parchment/40 uppercase tracking-wider font-semibold mt-5 mb-2 px-2.5">
                Recent Conversations
              </p>
            )}
            <div className="max-h-48 overflow-y-auto space-y-0.5 pr-1">
              {sessions.slice(0, 10).map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => openSession(s.id)}
                  className={cn(
                    "w-full truncate rounded-lg px-2.5 py-1.5 text-left text-xs transition-colors duration-150 flex items-center gap-2",
                    activeSessionId === s.id
                      ? "bg-sage/20 text-gold font-medium"
                      : "text-parchment/45 hover:bg-white/5 hover:text-parchment/80"
                  )}
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-sage/60 shrink-0" />
                  <span className="truncate">{s.title || "Conversation"}</span>
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Footer logout */}
        <div className="p-3 border-t border-white/5">
          <button
            type="button"
            onClick={logout}
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-sm text-parchment/50 hover:bg-white/5 hover:text-parchment transition-colors"
          >
            <LogOut className="h-4 w-4" />
            <span>Log out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
