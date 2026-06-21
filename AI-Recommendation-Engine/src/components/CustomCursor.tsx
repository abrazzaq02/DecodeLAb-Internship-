import { useRef, useEffect } from 'react';

export default function CustomCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const posRef = useRef({ x: 0, y: 0 });
  const targetRef = useRef({ x: 0, y: 0 });
  const isHoveringRef = useRef(false);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const cursor = cursorRef.current;
    if (!cursor) return;

    const handleMove = (e: MouseEvent) => {
      targetRef.current.x = e.clientX;
      targetRef.current.y = e.clientY;
    };

    const handleOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'A' ||
        target.tagName === 'BUTTON' ||
        target.closest('a') ||
        target.closest('button') ||
        target.closest('[data-cursor-hover]') ||
        target.closest('.exhibition-item') ||
        target.tagName === 'VIDEO'
      ) {
        isHoveringRef.current = true;
      } else {
        isHoveringRef.current = false;
      }
    };

    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseover', handleOver);

    function animate() {
      posRef.current.x += (targetRef.current.x - posRef.current.x) * 0.15;
      posRef.current.y += (targetRef.current.y - posRef.current.y) * 0.15;

      const size = isHoveringRef.current ? 48 : 12;
      const opacity = isHoveringRef.current ? 0.6 : 1;

      if (cursor) {
        cursor.style.transform = `translate(${posRef.current.x - size / 2}px, ${posRef.current.y - size / 2}px)`;
        cursor.style.width = `${size}px`;
        cursor.style.height = `${size}px`;
        cursor.style.opacity = String(opacity);
      }
      rafRef.current = requestAnimationFrame(animate);
    }

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(rafRef.current);
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseover', handleOver);
    };
  }, []);

  return (
    <div
      ref={cursorRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        background: '#ffffff',
        mixBlendMode: 'difference',
        pointerEvents: 'none',
        zIndex: 9999,
        transition: 'width 0.3s ease, height 0.3s ease, opacity 0.3s ease',
        willChange: 'transform',
      }}
    />
  );
}
