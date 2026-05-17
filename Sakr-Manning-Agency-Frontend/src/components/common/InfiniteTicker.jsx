import React from "react";
import Card from "./Card";

/**
 * InfiniteTicker
 * 
 * Uses pure hardware-accelerated CSS keyframe translation (translate3d) 
 * to provide a 100% smooth, continuous, and reliable infinite marquee 
 * that never freezes, stutters, or jumps.
 *
 * Props:
 *  - items      : array of data objects
 *  - speed      : base animation duration modifier (default 8 seconds per card)
 *  - renderItem : optional JSX mapping function for custom card styling
 */
export default function InfiniteTicker({ items, speed = 8, renderItem }) {
  if (!items || items.length === 0) return null;

  // Triple the list to ensure the marquee seamless-loop covers the screen width completely
  const duplicatedList = [...items, ...items, ...items];

  // Dynamic animation name key to force keyframes to re-evaluate on array changes
  const animationName = `marquee-scroll-${items.length}`;
  const cardSpeed = speed < 2 ? 8 : speed;
  const duration = Math.max(items.length * cardSpeed, 18);

  return (
    <div className="relative w-full overflow-hidden select-none py-2">
      {/* Hardware-accelerated CSS Marquee Animation Styles */}
      <style>{`
        @keyframes ${animationName} {
          0% {
            transform: translate3d(0, 0, 0);
          }
          100% {
            transform: translate3d(-33.3333%, 0, 0);
          }
        }
        .animate-marquee-track {
          display: flex;
          gap: 1.25rem; /* gap-5 (20px) */
          width: max-content;
          animation: ${animationName} ${duration}s linear infinite;
          will-change: transform;
        }
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>

      {/* Left edge premium ambient fade overlay */}
      <div
        className="pointer-events-none absolute left-0 top-0 bottom-0 w-16 z-10"
        style={{ background: "linear-gradient(to right, #f8faff, transparent)" }}
      />

      {/* Right edge premium ambient fade overlay */}
      <div
        className="pointer-events-none absolute right-0 top-0 bottom-0 w-16 z-10"
        style={{ background: "linear-gradient(to left, #ffffff, transparent)" }}
      />

      {/* Scrolling track */}
      <div className="animate-marquee-track">
        {duplicatedList.map((item, idx) =>
          renderItem ? (
            renderItem(item, idx)
          ) : (
            <Card
              key={idx}
              title={item.title}
              subtitle={item.text}
              variant="outlined"
              className="!flex !flex-row flex-shrink-0 rounded-2xl shadow-md p-10 my-4 w-[510px] h-[226px] text-center items-center justify-center"
            />
          )
        )}
      </div>
    </div>
  );
}
