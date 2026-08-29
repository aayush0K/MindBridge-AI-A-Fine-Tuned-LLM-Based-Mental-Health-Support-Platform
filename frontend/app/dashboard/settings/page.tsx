"use client";

import { useEffect, useState } from "react";
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
    <div className="h-full overflow-y-auto p-6 max-w-lg bg-parchment mx-auto">
      <h1 className="font-display text-2xl text-ink mb-6">Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Email</Label>
            <Input value={email} disabled className="mt-1 bg-slate-50" />
          </div>
          <div>
            <Label htmlFor="name">Full name</Label>
            <Input id="name" value={fullName} onChange={(e) => setFullName(e.target.value)} className="mt-1" />
          </div>
          <div>
            <Label htmlFor="emergency">Emergency contact email</Label>
            <Input
              id="emergency"
              type="email"
              value={emergencyEmail}
              onChange={(e) => setEmergencyEmail(e.target.value)}
              className="mt-1"
              placeholder="Optional crisis contact"
            />
          </div>
          <Button onClick={save} className="bg-sage text-parchment hover:bg-ink rounded-full transition-colors duration-300 ease-mb-ease">{saved ? "Saved!" : "Save changes"}</Button>
        </CardContent>
      </Card>
    </div>
  );
}
