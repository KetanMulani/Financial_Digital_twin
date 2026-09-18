export function Loading() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center animate-fadeIn">
      <svg viewBox="0 0 220 110" className="w-[220px] h-[110px] mb-7">
        <path
          d="M5,90 C50,90 60,20 100,45 C140,70 150,15 215,20"
          fill="none"
          stroke="#2dd4c8"
          strokeWidth={2.5}
          strokeLinecap="round"
          className="animate-drawLine loading-path-anim"
          style={{
            filter: "drop-shadow(0 0 6px rgba(45,212,200,0.35))",
            strokeDasharray: 400,
          }}
        />
      </svg>
      <div className="font-display text-[17px] font-semibold">
        Building your possible future
        <span>
          <span className="animate-blink">.</span>
          <span className="animate-blink [animation-delay:0.2s]">.</span>
          <span className="animate-blink [animation-delay:0.4s]">.</span>
        </span>
      </div>
    </div>
  );
}
