import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "gold" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  shimmer?: boolean;
}

const baseStyle = "rounded-[var(--radius-md)] transition-all duration-200 ease-in-out font-sans font-semibold relative overflow-hidden";

const variantStyles: Record<Variant, string> = {
  primary: "",
  secondary: "",
  gold: "",
  ghost: "bg-transparent text-text-secondary",
  danger: "",
};

const sizeClasses: Record<Size, string> = {
  sm: "py-2 px-4 text-sm",
  md: "py-3 px-6",
};

function getInlineStyle(variant: Variant): React.CSSProperties {
  switch (variant) {
    case "primary":
    case "gold":
      return {
        background: "linear-gradient(100deg, #A9882F, #C9A84C 50%, #E8CD7E)",
        color: "#1A1206",
        boxShadow: "0 8px 24px -6px rgba(201,168,76,.5)",
        height: "auto",
      };
    case "secondary":
      return {
        border: "1px solid rgba(201,168,76,.4)",
        background: "rgba(201,168,76,.06)",
        color: "#E8CD7E",
      };
    case "ghost":
      return {
        border: "1px solid rgba(255,255,255,.1)",
        background: "transparent",
      };
    case "danger":
      return {
        border: "1px solid rgba(196,84,84,.4)",
        background: "rgba(196,84,84,.08)",
        color: "#D98A8A",
      };
  }
}

export function Button({
  variant = "primary",
  size = "md",
  shimmer = false,
  className = "",
  children,
  style,
  ...props
}: ButtonProps) {
  const isPrimary = variant === "primary" || variant === "gold";
  return (
    <button
      className={`${baseStyle} ${variantStyles[variant]} ${sizeClasses[size]} ${className}`}
      style={{ ...getInlineStyle(variant), ...style }}
      {...props}
    >
      {children}
      {shimmer && isPrimary && (
        <span
          style={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(100deg, transparent 30%, rgba(255,255,255,.25) 50%, transparent 70%)",
            backgroundSize: "200% 100%",
            animation: "mystral-shimmer 2.6s linear infinite",
          }}
        />
      )}
    </button>
  );
}
