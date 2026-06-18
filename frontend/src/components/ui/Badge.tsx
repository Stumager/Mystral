type BadgeVariant = "FREE" | "PRO";

interface BadgeProps {
  variant: BadgeVariant;
}

const styles: Record<BadgeVariant, { bg: string; color: string }> = {
  FREE: {
    bg:    "rgba(107,78,255,0.12)",
    color: "#9B8AFF",
  },
  PRO: {
    bg:    "rgba(201,168,76,0.15)",
    color: "#C9A84C",
  },
};

export function Badge({ variant }: BadgeProps) {
  const { bg, color } = styles[variant];
  return (
    <span
      className="text-xs uppercase tracking-wider px-2 py-0.5 rounded-md font-sans"
      style={{ background: bg, color }}
    >
      {variant}
    </span>
  );
}
