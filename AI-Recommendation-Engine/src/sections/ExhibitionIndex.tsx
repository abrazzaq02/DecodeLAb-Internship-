import { useRef, useEffect, useCallback } from 'react';
import gsap from 'gsap';
import { exhibitionsConfig } from '../config';
import { exhibitions, type Exhibition } from '../lib/exhibitions';

function splitTextToChars(container: HTMLElement): HTMLSpanElement[] {
  const text = container.textContent || '';
  container.innerHTML = '';
  const chars: HTMLSpanElement[] = [];
  const words = text.split(' ');
  
  words.forEach((word, wi) => {
    const wordSpan = document.createElement('span');
    wordSpan.className = 'word-wrap';
    wordSpan.style.display = 'inline-block';
    wordSpan.style.overflow = 'hidden';
    wordSpan.style.perspective = '1200px';
    wordSpan.style.perspectiveOrigin = '-100% 50%';
    wordSpan.style.position = 'relative';

    for (let i = 0; i < word.length; i++) {
      const charSpan = document.createElement('span');
      charSpan.className = 'char';
      charSpan.textContent = word[i];
      charSpan.style.display = 'inline-block';
      charSpan.style.willChange = 'transform';
      charSpan.style.transformOrigin = '0% 0%';
      wordSpan.appendChild(charSpan);
      chars.push(charSpan);
    }

    container.appendChild(wordSpan);
    if (wi < words.length - 1) {
      const space = document.createElement('span');
      space.innerHTML = '&nbsp;';
      space.style.display = 'inline-block';
      container.appendChild(space);
    }
  });

  return chars;
}

function ExhibitionItem({
  exhibition,
  index,
  onSelect,
}: {
  exhibition: Exhibition;
  index: number;
  onSelect: (slug: string) => void;
}) {
  const itemRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const cloneRef = useRef<HTMLDivElement>(null);
  const revealRef = useRef<HTMLDivElement>(null);
  const originalCharsRef = useRef<HTMLSpanElement[]>([]);
  const cloneCharsRef = useRef<HTMLSpanElement[]>([]);
  const rafRef = useRef<number>(0);
  const mouseRef = useRef({ x: 0, y: 0 });
  const currentRef = useRef({ x: 0, y: 0, rotation: 0 });
  const boundsRef = useRef<DOMRect | null>(null);
  const velocityRef = useRef({ x: 0 });
  const prevMouseRef = useRef({ x: 0 });
  const textTlRef = useRef<gsap.core.Timeline | null>(null);
  const imageTlRef = useRef<gsap.core.Timeline | null>(null);
  const isInitRef = useRef(false);

  useEffect(() => {
    if (isInitRef.current) return;
    isInitRef.current = true;

    const textEl = textRef.current;
    const cloneEl = cloneRef.current;
    if (!textEl || !cloneEl) return;

    textEl.textContent = exhibition.title;
    cloneEl.textContent = exhibition.title;

    originalCharsRef.current = splitTextToChars(textEl);
    cloneCharsRef.current = splitTextToChars(cloneEl);

    cloneCharsRef.current.forEach((char) => {
      gsap.set(char, { y: '-100%', rotationX: 90, opacity: 0 });
    });
  }, [exhibition.title]);

  const onMouseEnter = useCallback(() => {
    const item = itemRef.current;
    if (!item) return;
    boundsRef.current = item.getBoundingClientRect();

    // Text animation
    if (textTlRef.current) {
      textTlRef.current.kill();
    }
    const textTl = gsap.timeline();

    textTl.to(originalCharsRef.current, {
      y: '100%',
      rotationX: -90,
      opacity: 0,
      stagger: 0.02,
      duration: 0.5,
      ease: 'power2.out',
    }, 0);

    cloneCharsRef.current.forEach((char) => {
      gsap.set(char, { y: '-100%', rotationX: 90, opacity: 0 });
    });

    textTl.to(cloneCharsRef.current, {
      y: '0%',
      rotationX: 0,
      opacity: 1,
      stagger: 0.02,
      duration: 0.5,
      ease: 'power2.out',
    }, 0.05);

    textTlRef.current = textTl;

    // Image reveal animation
    const reveal = revealRef.current;
    if (!reveal) return;
    const inner = reveal.querySelector('.hover-reveal__inner') as HTMLElement;
    const img = reveal.querySelector('.hover-reveal__img') as HTMLElement;
    if (!inner || !img) return;

    if (imageTlRef.current) {
      imageTlRef.current.kill();
    }

    gsap.set(reveal, { opacity: 1 });
    const imgTl = gsap.timeline();
    imgTl.fromTo(inner, { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 1.2, ease: 'expo.out' }, 0);
    imgTl.fromTo(img, { scaleX: 2 }, { scaleX: 1, duration: 1.2, ease: 'expo.out' }, 0);
    imageTlRef.current = imgTl;

    // Start rAF loop
    function animate() {
      const dx = mouseRef.current.x - prevMouseRef.current.x;
      velocityRef.current.x = dx;
      prevMouseRef.current.x = mouseRef.current.x;

      const bounds = boundsRef.current;
      if (bounds) {
        const targetX = mouseRef.current.x - bounds.left;
        const targetY = mouseRef.current.y - bounds.top;
        const targetRotation = Math.max(-15, Math.min(15, velocityRef.current.x * 0.5));

        currentRef.current.x += (targetX - currentRef.current.x) * 0.15;
        currentRef.current.y += (targetY - currentRef.current.y) * 0.15;
        currentRef.current.rotation += (targetRotation - currentRef.current.rotation) * 0.15;

        if (reveal) {
          gsap.set(reveal, {
            x: currentRef.current.x - 160,
            y: currentRef.current.y - 200,
            rotation: currentRef.current.rotation,
          });
        }
      }
      rafRef.current = requestAnimationFrame(animate);
    }
    rafRef.current = requestAnimationFrame(animate);
  }, []);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    mouseRef.current.x = e.clientX;
    mouseRef.current.y = e.clientY;
  }, []);

  const onMouseLeave = useCallback(() => {
    cancelAnimationFrame(rafRef.current);

    // Reverse text
    if (textTlRef.current) {
      textTlRef.current.kill();
    }
    const reverseTl = gsap.timeline();
    reverseTl.to(cloneCharsRef.current, {
      y: '-100%',
      rotationX: 90,
      opacity: 0,
      stagger: 0.02,
      duration: 0.5,
      ease: 'power2.out',
    }, 0);
    reverseTl.to(originalCharsRef.current, {
      y: '0%',
      rotationX: 0,
      opacity: 1,
      stagger: 0.02,
      duration: 0.5,
      ease: 'power2.out',
    }, 0.05);
    textTlRef.current = reverseTl;

    // Hide image
    const reveal = revealRef.current;
    if (!reveal) return;
    const inner = reveal.querySelector('.hover-reveal__inner') as HTMLElement;
    const img = reveal.querySelector('.hover-reveal__img') as HTMLElement;
    if (!inner || !img) return;

    const direction = velocityRef.current.x > 0 ? 1 : -1;

    if (imageTlRef.current) {
      imageTlRef.current.kill();
    }

    const hideTl = gsap.timeline({
      onComplete: () => {
        gsap.set(reveal, { opacity: 0 });
      },
    });
    hideTl.to(inner, { opacity: 0, duration: 0.4 }, 0);
    hideTl.to(img, { scaleX: 1.5, duration: 0.6, ease: 'power2.in' }, 0);
    hideTl.to(reveal, { y: '+=150', rotation: direction * 5, duration: 0.6, ease: 'power2.in' }, 0);
    imageTlRef.current = hideTl;
  }, []);

  return (
    <div
      ref={itemRef}
      className="exhibition-item"
      onMouseEnter={onMouseEnter}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      onClick={() => onSelect(exhibition.slug)}
      role="link"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(exhibition.slug);
        }
      }}
      style={{
        borderBottom: '1px solid #e5e5e5',
        padding: '2rem 0',
        cursor: 'none',
        position: 'relative',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <button
          onClick={() => onSelect(exhibition.slug)}
          style={{
            position: 'relative',
            overflow: 'hidden',
            background: 'none',
            border: 'none',
            padding: 0,
            margin: 0,
            textAlign: 'left',
            cursor: 'none',
            color: 'inherit',
          }}
          aria-label={`Open ${exhibition.title}`}
        >
          <div
            ref={textRef}
            className="exhibition-item-text"
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(3rem, 6vw, 6rem)',
              textTransform: 'uppercase',
              pointerEvents: 'none',
              lineHeight: 1.1,
              fontWeight: 400,
            }}
          />
          <div
            ref={cloneRef}
            className="exhibition-item-text"
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(3rem, 6vw, 6rem)',
              textTransform: 'uppercase',
              pointerEvents: 'none',
              lineHeight: 1.1,
              fontWeight: 400,
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
            }}
          />
        </button>
        <span
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '0.75rem',
            color: 'var(--text-secondary)',
            letterSpacing: '0.1em',
            flexShrink: 0,
            marginLeft: '2rem',
          }}
        >
          {exhibition.year} — No. {String(index + 1).padStart(2, '0')}
        </span>
      </div>

      <div
        ref={revealRef}
        className="hover-reveal"
        style={{
          position: 'absolute',
          width: '320px',
          height: '400px',
          top: 0,
          left: 0,
          pointerEvents: 'none',
          opacity: 0,
          zIndex: 10,
          willChange: 'transform',
        }}
      >
        <div
          className="hover-reveal__inner"
          style={{
            width: '100%',
            height: '100%',
            overflow: 'hidden',
            position: 'relative',
            willChange: 'transform, opacity',
          }}
        >
          <div
            className="hover-reveal__img"
            style={{
              width: '100%',
              height: '100%',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundImage: `url(${exhibition.image})`,
              willChange: 'transform',
            }}
          />
        </div>
      </div>
    </div>
  );
}

interface ExhibitionIndexProps {
  onSelect: (slug: string) => void;
}

export default function ExhibitionIndex({ onSelect }: ExhibitionIndexProps) {
  const sectionRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  if (!exhibitionsConfig.sectionLabel && exhibitions.length === 0) {
    return null;
  }

  useEffect(() => {
    const header = headerRef.current;
    if (!header) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            gsap.fromTo(
              header,
              { opacity: 0, y: 20 },
              { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }
            );
            observer.disconnect();
          }
        });
      },
      { threshold: 0.2 }
    );

    observer.observe(header);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="exhibitions"
      ref={sectionRef}
      style={{
        background: 'var(--bg-primary)',
        padding: '6rem 4vw 8rem',
        position: 'relative',
        zIndex: 2,
      }}
    >
      <div
        ref={headerRef}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          marginBottom: '3rem',
          opacity: 0,
        }}
      >
        <span
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '0.7rem',
            fontWeight: 500,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            color: 'var(--text-secondary)',
          }}
        >
          {exhibitionsConfig.sectionLabel}
        </span>
        {exhibitionsConfig.countLabel && (
          <span
            style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '0.7rem',
              fontWeight: 400,
              color: 'var(--text-secondary)',
              letterSpacing: '0.05em',
            }}
          >
            {exhibitionsConfig.countLabel}
          </span>
        )}
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
          borderTop: '1px solid #e5e5e5',
        }}
      >
        {exhibitions.map((ex, i) => (
          <ExhibitionItem key={ex.slug} exhibition={ex} index={i} onSelect={onSelect} />
        ))}
      </div>
    </section>
  );
}
