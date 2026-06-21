import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { heroConfig, navigationConfig } from '../config';

export default function Hero() {
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subRef = useRef<HTMLParagraphElement>(null);
  const navRef = useRef<HTMLElement>(null);
  const hasHeroContent =
    navigationConfig.brandName ||
    navigationConfig.links.length > 0 ||
    heroConfig.titleLines.length > 0 ||
    heroConfig.subtitle;

  useEffect(() => {
    if (!hasHeroContent) return;

    const tl = gsap.timeline({ delay: 0.5 });
    if (navRef.current) {
      tl.fromTo(
        navRef.current,
        { opacity: 0, y: -20 },
        { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }
      );
    }
    if (titleRef.current) {
      tl.fromTo(
        titleRef.current,
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 1.2, ease: 'power3.out' },
        '-=0.3'
      );
    }
    if (subRef.current) {
      tl.fromTo(
        subRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' },
        '-=0.5'
      );
    }

    return () => { tl.kill(); };
  }, [hasHeroContent]);

  if (!hasHeroContent) {
    return null;
  }

  return (
    <section
      style={{
        position: 'relative',
        width: '100%',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        zIndex: 1,
      }}
    >
      <nav
        ref={navRef}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '2rem 4vw',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.75rem',
          fontWeight: 500,
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          color: 'var(--text-inverse)',
          opacity: 0,
        }}
      >
        {navigationConfig.brandName ? <span>{navigationConfig.brandName}</span> : <span />}
        <div style={{ display: 'flex', gap: '2.5rem' }}>
          {navigationConfig.links.map((item) => (
            <a key={`${item.label}-${item.href}`} href={item.href} style={{ color: 'inherit', textDecoration: 'none' }}>
              {item.label}
            </a>
          ))}
        </div>
      </nav>

      <div
        style={{
          padding: '0 4vw 13vh',
          textAlign: 'center',
        }}
      >
        {heroConfig.titleLines.length > 0 && (
          <h1
            ref={titleRef}
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(3rem, 10vw, 9rem)',
              fontWeight: 400,
              lineHeight: 1.05,
              letterSpacing: '-0.02em',
              color: 'var(--text-inverse)',
              margin: 0,
              opacity: 0,
              textWrap: 'balance',
            }}
          >
            {heroConfig.titleLines.map((line, index) => (
              <span key={`${line}-${index}`}>
                {line}
                {index < heroConfig.titleLines.length - 1 && <br />}
              </span>
            ))}
          </h1>
        )}
        {heroConfig.subtitle && (
          <p
            ref={subRef}
            style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 'clamp(0.7rem, 1.2vw, 0.85rem)',
              fontWeight: 400,
              letterSpacing: '0.35em',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.5)',
              marginTop: '1.5rem',
              opacity: 0,
            }}
          >
            {heroConfig.subtitle}
          </p>
        )}
      </div>
    </section>
  );
}
