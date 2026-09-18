import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md font-display font-semibold transition-all disabled:pointer-events-none disabled:opacity-40",
  {
    variants: {
      variant: {
        primary:
          "bg-accent text-[#06110f] shadow-[0_0_18px_1px_rgba(45,212,200,0.35)] hover:-translate-y-px hover:shadow-[0_0_24px_3px_rgba(45,212,200,0.35)]",
        ghost:
          "bg-transparent border border-line-strong text-text-dim hover:text-text hover:border-white/25",
        link: "bg-transparent text-accent font-semibold p-0 hover:underline",
      },
      size: {
        default: "px-[26px] py-[13px] text-sm rounded-xl",
        sm: "px-4 py-2 text-xs rounded-lg",
        icon: "h-[42px] w-[42px] rounded-full",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
