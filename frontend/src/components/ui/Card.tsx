import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function Card({ children, className = "", ...props }: CardProps) {
  return (
    <div
      className={`rounded-2xl p-4 ${className}`}
      style={{
        background: "rgba(13,11,31,0.72)",
        border: "0.5px solid rgba(140,110,255,0.15)",
      }}
      {...props}
    >
      {children}
    </div>
  );
}
