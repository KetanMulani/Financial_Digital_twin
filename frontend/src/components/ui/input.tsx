import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  prefix?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, prefix, ...props }, ref) => {
    return (
      <div className="flex items-center bg-white/[0.02] border border-line-strong rounded-[10px] px-[14px] transition-all focus-within:border-accent/50 focus-within:shadow-[0_0_0_4px_rgba(45,212,200,0.14)]">
        {prefix && <span className="text-text-faint text-[15px] mr-1.5">{prefix}</span>}
        <input
          ref={ref}
          className={cn(
            "flex-1 bg-transparent border-none outline-none text-text text-base py-3 placeholder:text-text-faint tabular-nums",
            className
          )}
          {...props}
        />
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
