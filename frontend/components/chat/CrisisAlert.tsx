"use client";

import { AlertTriangle, Phone, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  onAcknowledge: () => void;
}

const INDIAN_CRISIS_HOTLINES = [
  { name: "India Emergency (Police / Medical)", number: "112", tel: "112", badge: "Immediate Emergency" },
  { name: "Tele-MANAS (Govt of India)", number: "14416", tel: "14416", badge: "24×7 Mental Health" },
  { name: "Tele-MANAS (Toll-Free)", number: "1800-89-14416", tel: "18008914416", badge: "24×7 Toll-Free" },
  { name: "NIMHANS Helpline", number: "080-46110007", tel: "08046110007", badge: "Apex Institute" },
  { name: "Vandrevala Foundation", number: "9999 666 555", tel: "9999666555", badge: "24×7 Counseling" },
  { name: "iCall (TISS)", number: "9152987821", tel: "9152987821", badge: "Mon–Sat 8AM–10PM" },
];

export function CrisisAlert({ onAcknowledge }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm p-4">
      <div className="max-w-lg w-full rounded-2xl border-2 border-red-500 bg-white p-6 shadow-2xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center text-red-600 shrink-0">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <div>
            <h2 className="font-bold text-lg text-slate-900">You Deserve Immediate Support</h2>
            <p className="text-xs text-slate-500">Government of India & Verified National Crisis Resources</p>
          </div>
        </div>

        <div className="rounded-xl bg-red-50 border border-red-200 p-3.5 text-xs text-red-900 space-y-1">
          <p className="font-semibold">
            If you or someone else is in immediate danger, call <strong>112</strong> or go to the nearest emergency department.
          </p>
          <p>
            Tele-MANAS provides 24×7 mental-health support across India. Call <strong>14416</strong> or <strong>1800-89-14416</strong>.
          </p>
        </div>

        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {INDIAN_CRISIS_HOTLINES.map((h) => (
            <div
              key={h.number}
              className="flex items-center justify-between p-2.5 rounded-xl border border-slate-100 bg-slate-50 hover:bg-slate-100 transition"
            >
              <div>
                <div className="text-xs font-bold text-slate-800">{h.name}</div>
                <div className="text-xs font-semibold text-emerald-700">{h.number}</div>
              </div>
              <a
                href={`tel:${h.tel}`}
                className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-emerald-700 transition shadow-sm shrink-0"
              >
                <Phone className="h-3 w-3" />
                Call
              </a>
            </div>
          ))}
        </div>

        <Button
          className="w-full py-2.5 bg-slate-800 text-white hover:bg-slate-900 rounded-xl font-medium transition text-xs"
          onClick={onAcknowledge}
        >
          I understand — return to conversation
        </Button>
      </div>
    </div>
  );
}
