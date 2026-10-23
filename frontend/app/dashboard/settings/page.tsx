"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { userApi } from "@/lib/api";

export default function SettingsPage() {
  const [fullName, setFullName] = useState("");
  const [emergencyEmail, setEmergencyEmail] = useState("");
  const [email, setEmail] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    userApi.me().then((r) => {
      setFullName(r.data.full_name || "");
      setEmergencyEmail(r.data.emergency_email || "");
      setEmail(r.data.email);
    }).catch(() => {});
  }, []);

  const save = async () => {
    await userApi.update({ full_name: fullName, emergency_email: emergencyEmail || undefined });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-8 max-w-lg bg-parchment mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link
          href="/dashboard"
          className="hidden md:inline-flex items-center gap-1.5 text-xs font-medium text-ink/70 hover:text-ink bg-white border border-ink/10 hover:border-ink/20 shadow-xs px-3.5 py-1.5 rounded-full transition-all"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Dashboard</span>
        </Link>
        <div>
          <h1 className="font-display text-2xl md:text-3xl text-ink font-semibold tracking-tight">Settings</h1>
          <p className="text-xs text-ink/50 mt-0.5">Manage your profile and emergency notification preferences.</p>
        </div>
      </div>

      <Card className="shadow-xs border border-ink/8">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold text-ink">Personal Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-xs font-semibold uppercase tracking-wider text-ink/60">Email Address</Label>
            <Input value={email} disabled className="mt-1 bg-parchment/70 border-ink/10 text-ink/70 rounded-xl" />
          </div>
          <div>
            <Label htmlFor="name" className="text-xs font-semibold uppercase tracking-wider text-ink/60">Full Name</Label>
            <Input
              id="name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your full name"
              className="mt-1 bg-white border-ink/15 rounded-xl text-ink focus:border-sage"
            />
          </div>
          <div>
            <Label htmlFor="emergency" className="text-xs font-semibold uppercase tracking-wider text-ink/60">Emergency Contact Email</Label>
            <Input
              id="emergency"
              type="email"
              value={emergencyEmail}
              onChange={(e) => setEmergencyEmail(e.target.value)}
              placeholder="e.g. parent@example.com"
              className="mt-1 bg-white border-ink/15 rounded-xl text-ink focus:border-sage"
            />
            <p className="text-[11px] text-ink/50 mt-1">
              Used strictly in severe acute crisis emergencies if emergency outreach is configured.
            </p>
          </div>
          <div className="flex items-center gap-3 pt-2">
            <Button onClick={save} className="bg-sage text-parchment hover:bg-ink rounded-full px-5 py-2 text-xs font-semibold shadow-xs transition-all active:scale-95">
              Save Changes
            </Button>
            {saved && (
              <span className="inline-flex items-center gap-1 text-xs text-emerald-600 font-medium">
                <CheckCircle2 className="h-4 w-4" />
                Changes saved
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
