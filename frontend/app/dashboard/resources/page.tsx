"use client";

import Link from "next/link";
import { LifeBuoy, PhoneCall, ShieldAlert, Heart, Wind, Activity, Info, ExternalLink, Phone, ArrowLeft } from "lucide-react";

export default function ResourcesPage() {
  const indianCrisisResources = [
    {
      name: "India Emergency Number",
      number: "112",
      tel: "112",
      badge: "Unified National Emergency",
      badgeColor: "bg-red-100 text-red-700 border-red-200",
      btnColor: "bg-red-600 hover:bg-red-700 text-white",
      desc: "For immediate danger or an emergency, call India's unified emergency number 112 (Police, Fire, Medical Ambulance).",
      officialSource: "Ministry of Home Affairs / Govt of India",
      sourceUrl: "https://112.gov.in",
      isPrimaryEmergency: true,
    },
    {
      name: "Tele-MANAS",
      number: "14416",
      tel: "14416",
      badge: "Govt of India · 24×7 Free",
      badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
      btnColor: "bg-emerald-600 hover:bg-emerald-700 text-white",
      desc: "Government of India's 24×7 Tele-MANAS mental-health support service. Comprehensive tele-mental health support across all Indian States and Union Territories in multiple regional languages.",
      officialSource: "Ministry of Health & Family Welfare (MoHFW) / DGHS",
      sourceUrl: "https://telemanas.mohfw.gov.in",
      isPrimaryMentalHealth: true,
    },
    {
      name: "Tele-MANAS (Toll-Free Alternative)",
      number: "1800-89-14416",
      tel: "18008914416",
      badge: "Toll-Free Helpline",
      badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
      btnColor: "bg-emerald-700 hover:bg-emerald-800 text-white",
      desc: "National toll-free alternative number for 24×7 mental-health support and psychological first aid across India.",
      officialSource: "Ministry of Health & Family Welfare",
      sourceUrl: "https://telemanas.mohfw.gov.in",
    },
    {
      name: "NIMHANS Helpline",
      number: "080-46110007",
      tel: "08046110007",
      badge: "24×7 National Apex Institute",
      badgeColor: "bg-indigo-100 text-indigo-800 border-indigo-200",
      btnColor: "bg-indigo-600 hover:bg-indigo-700 text-white",
      desc: "National Institute of Mental Health and Neurosciences (Govt of India) psycho-social support and mental health helpline.",
      officialSource: "NIMHANS, Autonomous Institute of National Importance",
      sourceUrl: "https://nimhans.ac.in",
    },
    {
      name: "Vandrevala Foundation Helpline",
      number: "9999 666 555 / 1860-2662-345",
      tel: "9999666555",
      badge: "24×7 Counseling Support",
      badgeColor: "bg-blue-100 text-blue-800 border-blue-200",
      btnColor: "bg-blue-600 hover:bg-blue-700 text-white",
      desc: "Free, confidential 24×7 psychological counseling and mental health support by trained professionals across India.",
      officialSource: "Vandrevala Foundation for Mental Health",
      sourceUrl: "https://www.vandrevalafoundation.com",
    },
    {
      name: "iCall Psychosocial Helpline",
      number: "9152987821",
      tel: "9152987821",
      badge: "Mon–Sat, 8 AM – 10 PM",
      badgeColor: "bg-purple-100 text-purple-800 border-purple-200",
      btnColor: "bg-purple-600 hover:bg-purple-700 text-white",
      desc: "Free, confidential psychosocial counseling by qualified mental health professionals at the Tata Institute of Social Sciences (TISS).",
      officialSource: "Tata Institute of Social Sciences (TISS), Mumbai",
      sourceUrl: "https://icallhelpline.org",
    },
  ];

  const copingTechniques = [
    {
      title: "5-4-3-2-1 Grounding Technique",
      desc: "Acknowledge 5 things you can see, 4 things you can physically touch, 3 sounds you can hear, 2 scents you can smell, and 1 positive affirmation about yourself.",
      icon: Wind,
    },
    {
      title: "Box Breathing (4-4-4-4)",
      desc: "Inhale slowly through your nose for 4 seconds, hold gently for 4 seconds, exhale smoothly through your mouth for 4 seconds, and pause for 4 seconds before your next breath.",
      icon: Activity,
    },
    {
      title: "Academic Pressure Compartmentalization",
      desc: "Break overwhelming study material into focused 25-minute Pomodoro intervals with 5-minute movement pauses. Tackle one micro-step at a time rather than the entire syllabus at once.",
      icon: Heart,
    },
  ];

  return (
    <div className="h-full flex flex-col bg-parchment overflow-y-auto">
      {/* Header */}
      <header className="border-b border-ink/8 bg-white/80 backdrop-blur-sm px-4 md:px-8 py-3.5 md:py-4 sticky top-0 z-20 shadow-xs">
        <div className="flex items-center gap-2 mb-1">
          <Link
            href="/dashboard"
            className="hidden md:inline-flex items-center gap-1.5 text-xs font-medium text-ink/70 hover:text-ink bg-parchment hover:bg-parchment-dim border border-ink/10 px-3 py-1 rounded-full transition-all"
          >
            <ArrowLeft className="h-3 w-3" />
            <span>Dashboard</span>
          </Link>
        </div>
        <h1 className="text-lg md:text-2xl font-bold text-ink flex items-center gap-2 font-display">
          <LifeBuoy className="h-5 w-5 text-emerald-600" />
          <span>India Crisis & Mental Health Resources</span>
        </h1>
        <p className="text-xs text-ink/50 mt-0.5 hidden sm:block">
          Official Government of India helplines, emergency services, and mental health first aid.
        </p>
      </header>

      <div className="p-4 md:p-8 max-w-4xl mx-auto w-full space-y-6 flex-1">
        {/* Urgent Emergency Alert Banner */}
        <div className="rounded-3xl border-2 border-red-200 bg-red-50/90 p-5 md:p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <ShieldAlert className="h-6 w-6 text-red-600 shrink-0 mt-0.5" />
            <div>
              <h2 className="font-bold text-red-900 text-sm md:text-base">Immediate Emergency Support (India)</h2>
              <p className="text-xs text-red-800 mt-1 leading-relaxed max-w-xl">
                If you or someone else is in immediate danger, call <strong>112</strong> or visit the nearest emergency facility.
                <br />
                Tele-MANAS provides 24×7 free national psychological support across India. Call <strong>14416</strong> or <strong>1800-89-14416</strong>.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0 w-full md:w-auto">
            <a
              href="tel:112"
              className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 rounded-full bg-red-600 px-5 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-red-700 active:scale-95 transition"
            >
              <Phone className="h-3.5 w-3.5" />
              <span>Call 112</span>
            </a>
            <a
              href="tel:14416"
              className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 rounded-full bg-emerald-600 px-5 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-emerald-700 active:scale-95 transition"
            >
              <Phone className="h-3.5 w-3.5" />
              <span>Call 14416</span>
            </a>
          </div>
        </div>

        {/* Verified Indian Helplines Grid */}
        <div>
          <div className="flex items-center justify-between mb-3.5">
            <h2 className="text-base md:text-lg font-bold text-ink flex items-center gap-2 font-display">
              <PhoneCall className="h-4 w-4 text-emerald-600" />
              <span>Verified Helplines & Emergency Contacts</span>
            </h2>
            <span className="text-xs text-ink/50 font-medium hidden sm:inline">
              Official Accredited Indian Sources
            </span>
          </div>

          <div className="grid gap-3.5 md:grid-cols-2">
            {indianCrisisResources.map((resource, i) => (
              <div
                key={i}
                className={`rounded-3xl border bg-white p-5 shadow-xs flex flex-col justify-between transition hover:shadow-md ${
                  resource.isPrimaryEmergency
                    ? "border-red-200 ring-1 ring-red-100"
                    : resource.isPrimaryMentalHealth
                    ? "border-emerald-200 ring-1 ring-emerald-100"
                    : "border-ink/8"
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-ink/50">
                      India Verified
                    </span>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium border ${resource.badgeColor}`}
                    >
                      {resource.badge}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-ink">{resource.name}</h3>

                  <div className="text-xl font-extrabold text-ink tracking-tight">
                    {resource.number}
                  </div>

                  <p className="text-xs text-ink/65 leading-relaxed pt-1">
                    {resource.desc}
                  </p>
                </div>

                <div className="pt-3.5 border-t border-ink/5 mt-3.5 flex items-center justify-between gap-3">
                  <a
                    href={resource.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] text-ink/50 hover:text-ink transition truncate max-w-[170px]"
                    title={`Source: ${resource.officialSource}`}
                  >
                    <span className="truncate">{resource.officialSource}</span>
                    <ExternalLink className="h-3 w-3 shrink-0" />
                  </a>

                  <a
                    href={`tel:${resource.tel}`}
                    className={`inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-xs font-semibold shadow-xs hover:shadow transition shrink-0 active:scale-95 ${resource.btnColor}`}
                  >
                    <Phone className="h-3 w-3" />
                    <span>Call {resource.number.split(" ")[0].split("/")[0]}</span>
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Evidence-Informed Coping Strategies */}
        <div>
          <h2 className="text-base md:text-lg font-bold text-ink flex items-center gap-2 mb-3.5 font-display">
            <Heart className="h-4 w-4 text-emerald-600" />
            <span>Evidence-Informed Grounding Techniques</span>
          </h2>
          <div className="grid gap-3.5 md:grid-cols-3">
            {copingTechniques.map((c, i) => {
              const Icon = c.icon;
              return (
                <div key={i} className="rounded-3xl border border-ink/8 bg-white p-5 shadow-xs space-y-2.5">
                  <div className="h-9 w-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <Icon className="h-4 w-4" />
                  </div>
                  <h3 className="text-sm font-bold text-ink">{c.title}</h3>
                  <p className="text-xs text-ink/65 leading-relaxed">{c.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Clinical & Academic Disclaimer */}
        <div className="rounded-3xl border border-ink/8 bg-white/70 p-5 space-y-1.5 text-xs text-ink/60">
          <div className="flex items-center gap-1.5 font-bold text-ink">
            <Info className="h-4 w-4 text-emerald-600" />
            <span>MindBridge AI Clinical & Academic Disclaimer</span>
          </div>
          <p className="leading-relaxed text-[11px]">
            MindBridge AI is an AI-powered conversational support platform developed for student emotional wellness support.
            MindBridge is <strong>NOT</strong> an emergency service, diagnostic tool, or replacement for clinical psychiatric healthcare.
            In situations involving severe emotional distress, self-harm ideation, or clinical emergencies, please connect immediately with a qualified healthcare professional or the verified Government of India emergency lines (<strong>112</strong> / <strong>14416</strong>).
          </p>
        </div>
      </div>
    </div>
  );
}
