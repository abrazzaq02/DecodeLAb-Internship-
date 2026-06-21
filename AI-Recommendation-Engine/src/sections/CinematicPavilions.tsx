import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { pavilionsConfig } from '../config';

gsap.registerPlugin(ScrollTrigger);

function VideoPlayer({ src, caption }: { src: string; caption: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const video = videoRef.current;
    if (!container || !video) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            video.play().catch(() => {});
          } else {
            video.pause();
          }
        });
      },
      { threshold: 0.3 }
    );

    observer.observe(container);

    gsap.fromTo(
      container,
      { opacity: 0, y: 20 },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: container,
          start: 'top 80%',
          once: true,
        },
      }
    );

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <div ref={containerRef} style={{ opacity: 0 }}>
      <div
        style={{
          position: 'relative',
          aspectRatio: '16 / 9',
          overflow: 'hidden',
          background: '#000',
        }}
      >
        <video
          ref={videoRef}
          src={src}
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
        />
      </div>
      <p
        style={{
          fontFamily: 'var(--font-sans)',
          fontSize: '0.75rem',
          fontWeight: 400,
          color: 'var(--text-secondary)',
          marginTop: '1rem',
          letterSpacing: '0.03em',
        }}
      >
        {caption}
      </p>
    </div>
  );
}

export default function CinematicPavilions() {
  if (!pavilionsConfig.sectionLabel && pavilionsConfig.videos.length === 0) {
    return null;
  }

  return (
    <section
      id="pavilions"
      style={{
        background: 'var(--bg-tertiary)',
        padding: '12rem 4vw',
        position: 'relative',
        zIndex: 2,
      }}
    >
      <div
        style={{
          marginBottom: '4rem',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.7rem',
          fontWeight: 500,
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
          color: 'var(--text-secondary)',
        }}
      >
        {pavilionsConfig.sectionLabel}
      </div>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: pavilionsConfig.videos.length > 1 ? 'repeat(2, 1fr)' : '1fr',
          gap: '3rem',
        }}
      >
        {pavilionsConfig.videos.map((video) => (
          <VideoPlayer key={`${video.src}-${video.caption}`} src={video.src} caption={video.caption} />
        ))}
      </div>
    </section>
  );
}
