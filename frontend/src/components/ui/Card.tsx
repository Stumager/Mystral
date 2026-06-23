import { HTMLAttributes } from "react";

type CardVariant = "default" | "gold" | "purple";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: CardVariant;
}

const variantStyles: Record<CardVariant, React.CSSProperties> = {
  default: {
    background: "var(--bg-card)",
    border: "1px solid var(--border-default)",
  },
  gold: {
    background: "var(--gradient-card)",
    border: "1px solid var(--border-gold-md)",
    backdropFilter: "blur(12px)",
  },
  purple: {
    background: "var(--bg-purple)",
    border: "1px solid rgba(138,127,192,.28)",
  },
};

export function Card({ children, variant = "default", className = "", style, ...props }: CardProps) {
  return (
    <div
      className={`p-4 ${className}`}
      style={{
        borderRadius: "var(--radius-lg)",
        ...variantStyles[variant],
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
}
