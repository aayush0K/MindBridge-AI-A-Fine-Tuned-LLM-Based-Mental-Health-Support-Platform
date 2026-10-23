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
      desc: "When feeling overwhelmed or anxious, notice 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. This grounds your nervous system in the physical present.",
      icon: Activity,
    },
    {
      title: "4-7-8 Breathing Exercise",
      desc: "Inhale quietly through your nose for 4 seconds, hold your breath gently for 7 seconds, then exhale completely through your mouth for 8 seconds. Repeat 4 times to reduce acute stress.",
      icon: Wind,
    },
    {
      title: "Academic Pressure Compartmentalization",
      desc: "Break overwhelming study material into focused 25-minute Pomodoro intervals with 5-minute movement pauses. Tackle one micro-step at a time rather than the entire syllabus at once.",
      icon: Heart,
    },
  ];

  return (
    <div className="h-full flex flex-col bg-slate-50 overflow-y-auto">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-6 md:px-8 py-4 md:py-5 sticky top-0 z-20">
        <div className="flex items-center gap-2.5 mb-1.5">
          <Link
            href="/dashboard"
            className="flex items-center gap-1 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded-full transition-colors"
          >
            <ArrowLeft className="h-3 w-3" />
            Dashboard
          </Link>
        </div>
        <h1 className="text-xl md:text-2xl font-bold text-slate-900 flex items-center gap-2">
          <LifeBuoy className="h-5 w-5 md:h-6 md:w-6 text-emerald-600" />
          India Crisis & Mental Health Resources
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Verified official Government of India helplines, emergency services, and mental wellness support.
        </p>
      </header>

      <div className="p-8 max-w-5xl mx-auto w-full space-y-8 flex-1">
        {/* Urgent Emergency Alert Banner */}
        <div className="rounded-2xl border-2 border-red-200 bg-red-50/90 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <ShieldAlert className="h-7 w-7 text-red-600 shrink-0 mt-0.5" />
            <div>
              <h2 className="font-bold text-red-900 text-base">Immediate Emergency Support (India)</h2>
              <p className="text-xs text-red-800 mt-1 leading-relaxed max-w-2xl">
                If you or someone else is in immediate danger, call <strong>112</strong> or go to the nearest emergency department.
                <br />
                Tele-MANAS provides 24×7 mental-health support across India. Call <strong>14416</strong> or <strong>1800-89-14416</strong>.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0 w-full md:w-auto">
            <a
              href="tel:112"
              className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-red-700 transition"
            >
              <Phone className="h-4 w-4" />
              Call 112
            </a>
            <a
              href="tel:14416"
              className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-emerald-700 transition"
            >
              <Phone className="h-4 w-4" />
              Call 14416
            </a>
          </div>
        </div>

        {/* Verified Indian Helplines Grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <PhoneCall className="h-5 w-5 text-emerald-600" />
              Verified Helplines & Emergency Contacts (India)
            </h2>
            <span className="text-xs text-slate-500 font-medium hidden sm:inline">
              Official Government & Accredited Sources
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {indianCrisisResources.map((resource, i) => (
              <div
                key={i}
                className={`rounded-2xl border bg-white p-5 shadow-sm flex flex-col justify-between transition hover:shadow-md ${
                  resource.isPrimaryEmergency
                    ? "border-red-200 ring-1 ring-red-100"
                    : resource.isPrimaryMentalHealth
                    ? "border-emerald-200 ring-1 ring-emerald-100"
                    : "border-slate-200"
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      India
                    </span>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium border ${resource.badgeColor}`}
                    >
                      {resource.badge}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900">{resource.name}</h3>

                  <div className="text-xl font-extrabold text-slate-800 tracking-tight">
                    {resource.number}
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed pt-1">
                    {resource.desc}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between gap-3">
                  <a
                    href={resource.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800 transition truncate max-w-[180px]"
                    title={`Source: ${resource.officialSource}`}
                  >
                    <span className="truncate">{resource.officialSource}</span>
                    <ExternalLink className="h-3 w-3 shrink-0" />
                  </a>

                  <a
                    href={`tel:${resource.tel}`}
                    className={`inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-bold shadow-sm transition shrink-0 ${resource.btnColor}`}
                  >
                    <Phone className="h-3.5 w-3.5" />
                    Call {resource.number.split(" ")[0].split("/")[0]}
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Evidence-Informed Coping Strategies */}
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
            <Heart className="h-5 w-5 text-emerald-600" />
            Evidence-Informed Coping & Grounding Techniques
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            {copingTechniques.map((c, i) => {
              const Icon = c.icon;
              return (
                <div key={i} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-3">
                  <div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{c.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{c.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Clinical & Academic Disclaimer */}
        <div className="rounded-2xl border border-slate-200 bg-slate-100/80 p-5 space-y-2 text-xs text-slate-600">
          <div className="flex items-center gap-2 font-bold text-slate-800">
            <Info className="h-4 w-4 text-emerald-600" />
            MindBridge AI Clinical & Academic Disclaimer
          </div>
          <p className="leading-relaxed">
            MindBridge AI is an AI-powered conversational platform developed for student emotional wellness support and academic research evaluation.
            MindBridge is <strong>NOT</strong> an emergency service, diagnostic tool, medical device, or replacement for clinical psychiatric healthcare.
            In situations involving severe emotional distress, self-harm ideation, or clinical medical emergencies, please connect immediately with a qualified healthcare professional or the verified Government of India emergency lines (<strong>112</strong> / <strong>14416</strong>) listed above.
          </p>
        </div>
      </div>
    </div>
  );
}
