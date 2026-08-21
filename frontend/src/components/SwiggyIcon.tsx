import React from 'react';

export const SwiggyLogo = ({ className = "h-8" }: { className?: string }) => (
  <svg
    viewBox="0 0 160 40"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    {/* Swiggy Iconic Location Pin Monogram */}
    <g transform="translate(0, 2) scale(0.36)">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M50 0C22.386 0 0 22.386 0 50c0 24.32 17.306 44.6 40.234 49.09V68.32H27.97V50h12.264V36.84c0-12.1 7.21-18.79 18.24-18.79 5.28 0 10.8.94 10.8.94v11.88h-6.084c-5.996 0-7.866 3.72-7.866 7.54V50h13.39l-2.14 18.32H55.324v30.77C78.252 94.6 95.558 74.32 95.558 50 95.558 22.386 73.172 0 50 0z"
        fill="#FC8019"
      />
    </g>
    {/* Clean Typography */}
    <text
      x="42"
      y="26"
      fill="#FFFFFF"
      fontFamily="system-ui, -apple-system, sans-serif"
      fontWeight="900"
      fontSize="22"
      letterSpacing="2.5"
    >
      SWIGGY
    </text>
  </svg>
);

export const SwiggyPinIcon = ({ className = "w-6 h-6" }: { className?: string }) => (
  <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <rect width="32" height="32" rx="8" fill="#FC8019" />
    <path
      d="M16 6C11.58 6 8 9.58 8 14c0 6.2 7.15 11.45 7.45 11.67.33.24.77.24 1.1 0 .3-.22 7.45-5.47 7.45-11.67 0-4.42-3.58-8-8-8zm0 11.5c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z"
      fill="#FFFFFF"
    />
  </svg>
);