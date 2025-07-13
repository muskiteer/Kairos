export const Logo = () => (
  <div className="flex items-center gap-2">
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Circle background */}
      <circle cx="16" cy="16" r="14" className="fill-primary/10" />

      {/* Premium stylized "K" */}
      {/* Vertical bar */}
      <rect x="10" y="8" width="2.5" height="16" rx="1" className="fill-primary" />

      {/* Upper diagonal */}
      <path
        d="M13 16 L21.5 9.5 C22 9 23 9.5 23.5 10 L24.5 11 C25 11.5 24 12.5 23.5 13 L16 17 Z"
        className="fill-primary"
      />

      {/* Lower diagonal */}
      <path
        d="M13 16 L21.5 22.5 C22 23 23 22.5 23.5 22 L24.5 21 C25 20.5 24 19.5 23.5 19 L16 15 Z"
        className="fill-primary"
      />
    </svg>
    <span className="font-bold text-lg tracking-tight text-primary">Kairos AI</span>
  </div>
);
