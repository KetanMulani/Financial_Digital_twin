export function BrandMark({ size = 26 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 26 26" fill="none">
      <path d="M13 2 L23 20 H3 Z" stroke="#2dd4c8" strokeWidth="1.6" strokeLinejoin="round" />
      <circle cx="13" cy="13" r="2.2" fill="#2dd4c8" />
    </svg>
  );
}
