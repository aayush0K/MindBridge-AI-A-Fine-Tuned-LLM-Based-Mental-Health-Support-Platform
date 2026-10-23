"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import {
  Menu,
  ArrowLeft,
  LayoutDashboard,
  MessageCircle,
  Heart,
  BookOpen,
  LifeBuoy,
} from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { getAccessToken } from "@/lib/api";

const mobileBottomNav = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard },
  { href: "/dashboard/chat", label: "Chat", icon: MessageCircle },
  { href: "/dashboard/mood", label: "Mood", icon: Heart },
  { href: "/dashboard/journal", label: "Journal", icon: BookOpen },
  { href: "/dashboard/resources", label: "Crisis", icon: LifeBuoy },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthed, setIsAuthed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  useEffect(() => {
    if (!getAccessToken()) {
      router.replace("/login");
    } else {
      setIsAuthed(true);
    }
  }, [router]);

  if (!isAuthed) {
    return (
      <div className="flex h-screen items-center justify-center bg-parchment">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sage border-t-transparent" />
      </div>
    );
  }

  const getPageTitle = () => {
    if (pathname === "/dashboard") return "Dashboard";
    if (pathname.includes("/chat")) return "AI Chat";
    if (pathname.includes("/mood")) return "Mood Tracker";
    if (pathname.includes("/journal")) return "Journal";
    if (pathname.includes("/resources")) return "Crisis Resources";
    if (pathname.includes("/settings")) return "Settings";
    return "MindBridge";
  };

  return (
    <div className="flex h-screen bg-parchment overflow-hidden">
      {/* Desktop and Drawer Sidebar */}
      <Sidebar
        mobileOpen={mobileSidebarOpen}
        onMobileClose={() => setMobileSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* Mobile Top Bar */}
        <header className="md:hidden flex items-center justify-between px-4 py-2.5 bg-ink border-b border-white/10 text-parchment flex-shrink-0 z-30">
          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={() => setMobileSidebarOpen(true)}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-parchment/80 hover:text-parchment transition-colors"
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            {pathname !== "/dashboard" && (
              <Link
                href="/dashboard"
                className="flex items-center gap-1 text-xs text-parchment/70 hover:text-parchment bg-white/5 hover:bg-white/10 px-2 py-1 rounded"
              >
                <ArrowLeft className="h-3 w-3" />
                <span>Back</span>
              </Link>
            )}
            <span className="font-display text-sm tracking-wide text-parchment font-medium truncate">
              {getPageTitle()}
            </span>
          </div>

          <Link
            href="/"
            className="text-xs text-parchment/60 hover:text-parchment bg-white/5 px-2.5 py-1 rounded-full transition-colors"
          >
            Home
          </Link>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-hidden pb-14 md:pb-0">{children}</main>

        {/* Mobile Bottom Navigation Bar (Guarantees Journal, Mood, Chat, Crisis are 1-tap accessible) */}
        <nav className="md:hidden fixed bottom-0 inset-x-0 bg-ink border-t border-white/10 flex items-center justify-around py-1.5 z-30">
          {mobileBottomNav.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex flex-col items-center justify-center py-1 px-2 rounded-lg transition-colors ${
                  active ? "text-gold font-medium" : "text-parchment/50 hover:text-parchment"
                }`}
              >
                <Icon className={`h-4 w-4 ${active ? "text-gold" : "text-parchment/50"}`} />
                <span className="text-[10px] mt-0.5">{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
