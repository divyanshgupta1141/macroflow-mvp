import React from 'react';

export const SwiggyLogo = ({ className = "h-8" }: { className?: string }) => (
  <div className={`flex items-center gap-2.5 ${className}`}>
    <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 flex-shrink-0">
      <rect width="120" height="120" rx="28" fill="#FC8019" />
      <path 
        d="M60 22C42.879 22 29 35.879 29 53c0 14.195 9.774 26.155 23.011 29.544l-2.456 12.043c-.347 1.702 1.096 3.213 2.836 2.957.942-.139 1.728-.756 2.108-1.624L65.86 70.36C79.743 67.587 90 53c0-17.121-13.879-31-30-31zm0 43c-6.627 0-12-5.373-12-12s5.373-12 12-12 12 5.373 12 12-5.373 12-12 12z" 
        fill="#FFFFFF" 
      />
    </svg>
    <div className="flex flex-col">
      <span className="font-black text-xl tracking-[0.2em] text-white leading-none">SWIGGY</span>
      <span className="text-[9px] font-bold tracking-widest text-[#FC8019] uppercase mt-0.5">Meal Combiner</span>
    </div>
  </div>
);
