interface LogoProps {
  size?: number;
}

export function Logo({ size = 28 }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 300 300"
      xmlns="http://www.w3.org/2000/svg"
      style={{ filter: "drop-shadow(0 0 9px rgba(201,168,76,.45))" }}
    >
      <defs>
        <linearGradient id="logo-gold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#7A5E22" />
          <stop offset=".4" stopColor="#C9A84C" />
          <stop offset=".7" stopColor="#F0D680" />
          <stop offset="1" stopColor="#A9882F" />
        </linearGradient>
        <mask id="logo-mask">
          <circle cx="130" cy="150" r="110" fill="white" />
          <circle cx="185" cy="140" r="95" fill="black" />
        </mask>
      </defs>
      <circle cx="130" cy="150" r="110" fill="url(#logo-gold)" mask="url(#logo-mask)" />
      <circle cx="185" cy="140" r="95" fill="none" stroke="url(#logo-gold)" strokeWidth="3.5" opacity=".7" />
    </svg>
  );
}
