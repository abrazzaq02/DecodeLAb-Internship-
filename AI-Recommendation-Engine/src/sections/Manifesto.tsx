import { useRef, useEffect, useState } from 'react';
import { manifestoConfig } from '../config';

function typeText(setter: (value: string) => void, text: string, speed: number): Promise<void> {
  return new Promise((resolve) => {
    setter('');
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setter(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(timer);
        resolve();
      }
    }, speed);
  });
}

export default function Manifesto() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const hasRunRef = useRef(false);
  const [headingText, setHeadingText] = useState('');
  const [bodyText, setBodyText] = useState('');
  const hasManifestoContent =
    manifestoConfig.headingText || manifestoConfig.bodyText || manifestoConfig.videoPath;

  useEffect(() => {
    if (!hasManifestoContent) return;

    const section = sectionRef.current;
    if (!section) return;

    async function runManifesto() {
      if (hasRunRef.current) return;
      hasRunRef.current = true;
      if (manifestoConfig.headingText) {
        await typeText(setHeadingText, manifestoConfig.headingText, 60);
      }
      if (manifestoConfig.bodyText) {
        await new Promise(r => setTimeout(r, 400));
        await typeText(setBodyText, manifestoConfig.bodyText, 30);
      }
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            runManifesto();
          }
        });
      },
      { threshold: 0.05 }
    );

    observer.observe(section);

    return () => {
      observer.disconnect();
    };
  }, [hasManifestoContent]);

  if (!hasManifestoContent) {
    return null;
  }

  return (
    <section
      ref={sectionRef}
      style={{
        background: 'var(--bg-primary)',
        padding: '6rem 4vw 10rem',
        position: 'relative',
        zIndex: 2,
      }}
    >
      <div
        style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: manifestoConfig.videoPath
            ? 'minmax(0, 1fr) minmax(320px, 44vw)'
            : 'minmax(0, 1fr)',
          gap: '4rem',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            maxWidth: '65ch',
          }}
        >
          {manifestoConfig.headingText && (
            <h2
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'clamp(2rem, 4vw, 3.5rem)',
                fontWeight: 600,
                lineHeight: 1.15,
                letterSpacing: '-0.01em',
                color: 'var(--text-primary)',
                minHeight: '1.2em',
                display: 'block',
              }}
            >
              {headingText}
            </h2>
          )}
          {manifestoConfig.bodyText && (
            <p
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'clamp(0.8rem, 1.1vw, 0.95rem)',
                fontWeight: 400,
                lineHeight: 1.7,
                color: 'var(--text-secondary)',
                marginTop: '2.5rem',
                minHeight: '3em',
                display: 'block',
              }}
            >
              {bodyText}
            </p>
          )}
        </div>

        {manifestoConfig.videoPath && (
          <div
            style={{
              width: '100%',
              maxWidth: '720px',
              justifySelf: 'end',
            }}
          >
            <div
              style={{
                position: 'relative',
                width: '100%',
                aspectRatio: '16 / 9',
                overflow: 'hidden',
                background: '#000',
              }}
            >
              <video
                autoPlay
                muted
                loop
                playsInline
                preload="metadata"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  display: 'block',
                }}
              >
                <source src={manifestoConfig.videoPath} type="video/mp4" />
              </video>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
