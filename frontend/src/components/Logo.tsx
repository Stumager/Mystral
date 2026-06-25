interface LogoProps {
  size?: number;
}

export function Logo({ size = 28 }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      xmlns="http://www.w3.org/2000/svg"
      style={{ overflow: "visible" }}
    >
      <defs>
        <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#7A5E22" />
          <stop offset=".4" stopColor="#C9A84C" />
          <stop offset=".7" stopColor="#F0D680" />
          <stop offset="1" stopColor="#A9882F" />
        </linearGradient>
        <mask id="lm">
          <circle cx="88" cy="100" r="72" fill="white" />
          <circle cx="128" cy="92" r="62" fill="black" />
        </mask>
      </defs>
      <circle cx="88" cy="100" r="72" fill="url(#lg)" mask="url(#lm)"
        style={{ filter: "drop-shadow(0 0 12px rgba(201,168,76,.6))" }} />
      <circle cx="128" cy="92" r="62" fill="none" stroke="url(#lg)" strokeWidth="2.5" opacity=".5" />
    </svg>
  );
}
