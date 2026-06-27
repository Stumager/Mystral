import { useState } from "react";

interface StarRatingProps {
  value: number;
  onChange?: (v: number) => void;
  size?: number;
  readonly?: boolean;
}

export function StarRating({ value, onChange, size = 24, readonly = false }: StarRatingProps) {
  const [hover, setHover] = useState(0);

  return (
    <div style={{ display: "flex", gap: 6 }}>
      {[1, 2, 3, 4, 5].map(i => {
        const active = i <= (hover || value);
        return (
          <span
            key={i}
            onClick={() => !readonly && onChange?.(i)}
            onMouseEnter={() => !readonly && setHover(i)}
            onMouseLeave={() => !readonly && setHover(0)}
            style={{
              fontSize: size, lineHeight: 1, cursor: readonly ? "default" : "pointer",
              color: active ? "#C9A84C" : "rgba(201,168,76,.3)",
              filter: active ? "drop-shadow(0 0 6px rgba(201,168,76,.5))" : "none",
              transition: ".15s",
            }}
          >
            {active ? "★" : "☆"}
          </span>
        );
      })}
    </div>
  );
}
