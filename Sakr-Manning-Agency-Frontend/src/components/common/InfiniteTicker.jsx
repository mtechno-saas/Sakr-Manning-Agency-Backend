import React, { useRef, useState, useEffect } from "react";
import Card from "./Card";

/**
 * InfiniteTicker / Vacancies Slider
 * 
 * Provides a responsive scroll container for vacancies without duplicating cards.
 * When items fit within the screen width, they are centered.
 * When they overflow, they auto-slide smoothly, wrap back to the beginning upon reaching the end,
 * pause on hover, and support left/right navigation buttons.
 */
export default function InfiniteTicker({ items, speed = 8, renderItem }) {
  const scrollRef = useRef(null);
  const [showLeftBtn, setShowLeftBtn] = useState(false);
  const [showRightBtn, setShowRightBtn] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  if (!items || items.length === 0) return null;

  const checkScrollButtons = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setShowLeftBtn(scrollLeft > 3);
      setShowRightBtn(scrollLeft + clientWidth < scrollWidth - 3);
    }
  };

  useEffect(() => {
    const el = scrollRef.current;
    if (el) {
      el.addEventListener("scroll", checkScrollButtons);
      checkScrollButtons();
      const timer = setTimeout(checkScrollButtons, 150);
      window.addEventListener("resize", checkScrollButtons);
      
      return () => {
        el.removeEventListener("scroll", checkScrollButtons);
        window.removeEventListener("resize", checkScrollButtons);
        clearTimeout(timer);
      };
    }
  }, [items]);

  // RequestAnimationFrame scroll loop for smooth automatic sliding
  useEffect(() => {
    const el = scrollRef.current;
    if (!el || isPaused) return;

    let animationFrameId;
    let lastTime = performance.now();
    const pixelsPerSecond = 35; // smooth sliding speed

    const step = (time) => {
      if (!scrollRef.current) return;
      const delta = (time - lastTime) / 1000;
      lastTime = time;

      const currentScroll = scrollRef.current.scrollLeft;
      const maxScroll = scrollRef.current.scrollWidth - scrollRef.current.clientWidth;

      if (maxScroll > 0) {
        if (currentScroll >= maxScroll - 1) {
          // Wrap back to beginning
          scrollRef.current.scrollLeft = 0;
        } else {
          scrollRef.current.scrollLeft += pixelsPerSecond * delta;
        }
      }

      animationFrameId = requestAnimationFrame(step);
    };

    animationFrameId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animationFrameId);
  }, [items, isPaused]);

  const handleScroll = (direction) => {
    if (scrollRef.current) {
      // scroll by one card width (approx 310px) plus gap (20px)
      const scrollAmount = 330; 
      scrollRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  return (
    <div 
      className="relative w-full select-none py-2 group"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Sliding Buttons - Left */}
      {showLeftBtn && (
        <button
          onClick={() => handleScroll("left")}
          className="absolute left-6 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-white/95 hover:bg-white shadow-[0_4px_12px_rgba(0,0,0,0.15)] border border-gray-100 flex items-center justify-center text-gray-700 hover:text-[#0065AF] transition-all duration-200 hover:scale-105 active:scale-95"
          aria-label="Scroll Left"
        >
          <svg
            width="10"
            height="16"
            viewBox="0 0 10 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-2.5 h-4 transform rotate-180"
          >
            <path
              d="M1.5 1.5L8 8L1.5 14.5"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      )}

      {/* Sliding Buttons - Right */}
      {showRightBtn && (
        <button
          onClick={() => handleScroll("right")}
          className="absolute right-6 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-white/95 hover:bg-white shadow-[0_4px_12px_rgba(0,0,0,0.15)] border border-gray-100 flex items-center justify-center text-gray-700 hover:text-[#0065AF] transition-all duration-200 hover:scale-105 active:scale-95"
          aria-label="Scroll Right"
        >
          <svg
            width="10"
            height="16"
            viewBox="0 0 10 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-2.5 h-4"
          >
            <path
              d="M1.5 1.5L8 8L1.5 14.5"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      )}

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

      {/* Scrolling track wrapper */}
      <div
        ref={scrollRef}
        className="flex items-center gap-5 overflow-x-auto scroll-smooth no-scrollbar px-16 py-4"
        style={{
          justifyContent: showLeftBtn || showRightBtn ? "flex-start" : "center",
        }}
      >
        {items.map((item, idx) => (
          <div key={idx} className="flex-shrink-0">
            {renderItem ? (
              renderItem(item, idx)
            ) : (
              <Card
                title={item.title}
                subtitle={item.text}
                variant="outlined"
                className="!flex !flex-row flex-shrink-0 rounded-2xl shadow-md p-10 my-4 w-[510px] h-[226px] text-center items-center justify-center"
              />
            )}
          </div>
        ))}
      </div>
      <style>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}
