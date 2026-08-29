import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-xl border border-ink/15 bg-white px-3 py-2 text-sm text-ink ring-offset-white placeholder:text-warm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-sage focus-visible:border-sage transition-colors duration-300 ease-mb-ease",
        className
      )}
      ref={ref}
      {...props}
    />
  )
);
Input.displayName = "Input";

export { Input };
