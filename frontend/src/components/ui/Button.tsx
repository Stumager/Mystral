import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "gold" | "ghost";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantClasses: Record<Variant, string> = {
  primary: "bg-violet-600 hover:bg-violet-400 text-white",
  gold:    "bg-gold-600 hover:bg-gold-300 text-bg-deep",
  ghost:   "bg-transparent border border-border-subtle text-text-muted hover:text-text-primary",
};

const sizeClasses: Record<Size, string> = {
  sm: "py-2 px-4 text-sm",
  md: "py-3 px-6",
};

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`rounded-xl transition-all duration-200 ease-in-out font-sans ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
