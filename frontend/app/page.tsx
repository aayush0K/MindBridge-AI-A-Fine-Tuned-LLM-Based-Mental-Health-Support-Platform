import Link from "next/link";
import { Brain, Shield, Clock, Sparkles, LineChart, HeartHandshake } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  { icon: Sparkles, title: "AI Chat", desc: "Empathetic conversations with few-shot prompting" },
  { icon: LineChart, title: "Mood Tracking", desc: "Log and visualize your emotional wellbeing" },
  { icon: HeartHandshake, title: "Crisis Support", desc: "India hotlines built into every session" },
  { icon: Shield, title: "Private & Secure", desc: "JWT auth, encrypted passwords, your data stays yours" },
  { icon: Clock, title: "24/7 Available", desc: "Support whenever you need someone to listen" },
  { icon: Brain, title: "Research-Backed", desc: "IEEE ICDSBS 2025 embedding + relevance pipeline" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-parchment">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6 relative z-20">
        <div className="flex items-center gap-2 font-display text-ink text-2xl">
          MindBridge
        </div>
        <div className="flex gap-3">
          <Link href="/login">
            <Button variant="ghost">Log in</Button>
          </Link>
          <Link href="/register">
            <Button className="bg-sage text-parchment hover:bg-ink rounded-full px-6 py-3 transition-colors duration-300 ease-mb-ease">Start free</Button>
          </Link>
        </div>
      </header>

      <div className="relative">
        <div className="mb-ambient-bg" />
        <main className="mx-auto max-w-6xl px-6 pb-20 relative z-10">
          <section className="py-16 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sage/15 text-gold-dark text-xs font-medium mb-4 border border-sage/30">
              <Sparkles className="h-3.5 w-3.5 text-sage" />
              Fine-Tuned on Meta Llama 3 with QLoRA
            </div>
            <h1 className="font-display text-5xl md:text-6xl font-medium text-ink tracking-tight">
              Your Mental Wellness Companion
            </h1>
            <p className="mt-4 font-sans text-lg text-ink/70 max-w-2xl mx-auto">
              MindBridge combines fine-tuned Meta Llama 3 conversational intelligence with sentence embeddings and multi-layer safety guards to deliver compassionate, real-time emotional support.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <Link href="/register">
                <Button size="lg" className="bg-sage text-parchment hover:bg-ink rounded-full px-6 py-3 transition-colors duration-300 ease-mb-ease">Start free</Button>
              </Link>
              <a href="#how-it-works">
                <Button size="lg" variant="outline" className="border border-ink/20 text-ink hover:bg-ink/5 rounded-full transition-colors duration-300 ease-mb-ease">
                  Learn how it works
                </Button>
              </a>
            </div>
          </section>

          <section className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 py-12">
            {features.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="rounded-2xl border border-ink/10 bg-parchment-dim p-6 shadow-none">
                <Icon className="h-8 w-8 text-sage mb-3" />
                <h3 className="font-semibold text-ink">{title}</h3>
                <p className="mt-1 text-sm text-ink/70">{desc}</p>
              </div>
            ))}
          </section>

          <section id="how-it-works" className="py-12">
            <h2 className="font-display text-2xl font-bold text-center mb-8 text-ink">How it works</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { step: "1", title: "Sign up", desc: "Create a private, secure account in seconds" },
                { step: "2", title: "Talk to MindBridge", desc: "Share what's on your mind — fine-tuned Llama 3 responds with empathy" },
                { step: "3", title: "Track wellbeing", desc: "Log mood, write journal reflections, and view trends" },
              ].map((s) => (
                <div key={s.step} className="text-center p-6 rounded-2xl bg-parchment-dim border border-ink/10">
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-sage text-parchment font-bold">
                    {s.step}
                  </span>
                  <h3 className="mt-4 font-semibold text-ink">{s.title}</h3>
                  <p className="text-sm text-ink/70 mt-1">{s.desc}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-2xl bg-ink text-parchment/70 p-8 text-center space-y-2">
            <p className="text-sm font-medium text-parchment">Built with Meta Llama 3 · IEEE Research Implementation · 100% Private & Secure</p>
            <p className="text-xs opacity-75">
              India Emergency & Helplines: Emergency 112 · Tele-MANAS 14416 / 1800-89-14416 · NIMHANS 080-46110007 · Vandrevala 9999-666-555
            </p>
          </section>
        </main>
      </div>
    </div>
  );
}
