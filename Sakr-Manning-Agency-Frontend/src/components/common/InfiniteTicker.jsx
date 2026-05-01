import { useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Card from "./Card";

export default function InfiniteTicker({ items, speed = 0.5 }) {
  const containerRef = useRef(null);
  const [list, setList] = useState(items);
  const [isPaused, setIsPaused] = useState(false);

  // --- Auto continuous scroll ---
  useEffect(() => {
    let animationFrame;
    const container = containerRef.current;

    const scrollStep = () => {
      if (container && !isPaused) {
        container.scrollLeft += speed;

        const firstItem = container.firstChild;
        const itemWidth = firstItem?.offsetWidth || 200;

        // When first item fully leaves → move it to end
        if (container.scrollLeft >= itemWidth) {
          container.scrollLeft -= itemWidth;
          setList((prev) => [...prev.slice(1), prev[0]]);
        }
      }
      animationFrame = requestAnimationFrame(scrollStep);
    };

    animationFrame = requestAnimationFrame(scrollStep);
    return () => cancelAnimationFrame(animationFrame);
  }, [isPaused, speed]);

  // --- Manual rotation via arrows ---
  const rotate = (direction = 1) => {
    const container = containerRef.current;
    const itemWidth = container.firstChild?.offsetWidth || 200;

    if (direction > 0) {
      // forward
      container.scrollTo({ left: itemWidth, behavior: "smooth" });
      setTimeout(() => {
        container.scrollLeft = 0;
        setList((prev) => [...prev.slice(1), prev[0]]);
      }, 300);
    } else {
      // backward
      container.scrollLeft = itemWidth;
      setList((prev) => [prev[prev.length - 1], ...prev.slice(0, -1)]);
      setTimeout(() => {
        container.scrollTo({ left: 0, behavior: "smooth" });
      }, 0);
    }
  };

  return (
    <div
      className="relative w-full overflow-hidden group"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Arrows (only visible on hover, also pause auto-scroll) */}
      <button
        onClick={() => rotate(-1)}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
        className="absolute left-2 top-1/2 -translate-y-1/2 z-10 
                   bg-white/80 hover:bg-white p-2 rounded-full shadow-lg 
                   opacity-0 group-hover:opacity-100 transition"
      >
        <ChevronLeft size={20} />
      </button>

      <button
        onClick={() => rotate(1)}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
        className="absolute right-2 top-1/2 -translate-y-1/2 z-10 
                   bg-white/80 hover:bg-white p-2 rounded-full shadow-lg 
                   opacity-0 group-hover:opacity-100 transition"
      >
        <ChevronRight size={20} />
      </button>

      {/* Scrolling container */}
      <div
        ref={containerRef}
        className="flex gap-4 overflow-x-hidden no-scrollbar"
      >
        {list.map((item, idx) => (
          <Card
            key={idx}
            title={item.title}
            subtitle={item.text}
            variant="outlined"
            // clickable
            className="!flex !flex-row flex-shrink-0 rounded-2xl shadow-md p-10 my-4 w-[510px] h-[226px] text-center items-center justify-center"
          />
        ))}
      </div>
    </div>
  );
}
