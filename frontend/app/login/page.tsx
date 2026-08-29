"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { authApi, setTokens } from "@/lib/api";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    try {
      const res = await authApi.login(data);
      setTokens(res.data.access_token, res.data.refresh_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      router.push("/dashboard");
    } catch {
      setError("root", { message: "Invalid email or password" });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink p-4">
      <Card className="w-full max-w-md bg-parchment border-none rounded-2xl shadow-none p-8">
        <CardHeader className="text-center p-0 mb-6">
          <div className="font-display text-2xl text-parchment mb-2 mx-auto">MindBridge</div>
          <CardTitle className="font-display text-2xl text-ink">Welcome back</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} className="mt-1" />
              {errors.email && <p className="text-xs text-crisis mt-1">{errors.email.message}</p>}
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" {...register("password")} className="mt-1" />
              {errors.password && <p className="text-xs text-crisis mt-1">{errors.password.message}</p>}
            </div>
            {errors.root && <p className="text-sm text-crisis">{errors.root.message}</p>}
            <Button type="submit" className="w-full py-2.5 bg-sage text-parchment hover:bg-ink rounded-full transition-colors duration-300 ease-mb-ease" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-ink/60">
            No account?{" "}
            <Link href="/register" className="text-sage font-medium hover:text-ink hover:underline">
              Register
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
