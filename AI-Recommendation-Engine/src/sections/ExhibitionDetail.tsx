import type { Exhibition } from '../lib/exhibitions';
import { exhibitionsConfig } from '../config';

interface ExhibitionDetailProps {
  exhibition: Exhibition;
  onBack: () => void;
}

export default function ExhibitionDetail({ exhibition, onBack }: ExhibitionDetailProps) {
  return (
    <section
      style={{
        background: 'var(--bg-primary)',
        minHeight: '100vh',
        padding: '2rem 4vw 5rem',
        position: 'relative',
        zIndex: 2,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '3rem',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.72rem',
          fontWeight: 500,
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: 'var(--text-secondary)',
        }}
      >
        <button
          onClick={onBack}
          style={{
            background: 'none',
            border: 'none',
            padding: 0,
            font: 'inherit',
            color: 'inherit',
            cursor: 'none',
          }}
        >
          {exhibitionsConfig.detailBackText}
        </button>
        <span>{exhibition.year}</span>
      </div>

      <div
        style={{
          maxWidth: '1440px',
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'minmax(280px, 36vw) minmax(0, 1fr)',
          gap: '4rem',
          alignItems: 'start',
        }}
      >
        <div
          style={{
            position: 'sticky',
            top: '2rem',
            maxWidth: '560px',
          }}
        >
          <div
            style={{
              width: '100%',
              aspectRatio: '4 / 5',
              overflow: 'hidden',
              background: '#f2f2f2',
            }}
          >
            <img
              src={exhibition.image}
              alt={exhibition.title}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                display: 'block',
              }}
            />
          </div>
        </div>

        <div
          style={{
            maxWidth: '62ch',
            paddingTop: '1rem',
          }}
        >
          <p
            style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '0.72rem',
              fontWeight: 500,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              color: 'var(--text-secondary)',
              marginBottom: '1.25rem',
            }}
          >
            {exhibition.eyebrow}
          </p>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2.6rem, 5vw, 5rem)',
              lineHeight: 1.02,
              fontWeight: 400,
              textTransform: 'uppercase',
              margin: 0,
              color: 'var(--text-primary)',
            }}
          >
            {exhibition.title}
          </h1>
          <p
            style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '1rem',
              lineHeight: 1.8,
              color: 'var(--text-secondary)',
              marginTop: '2rem',
              marginBottom: '3rem',
            }}
          >
            {exhibition.intro}
          </p>

          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '2.75rem',
            }}
          >
            {exhibition.sections.map((section) => (
              <article key={section.heading}>
                <h2
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: 'clamp(1.5rem, 2vw, 2.1rem)',
                    lineHeight: 1.15,
                    fontWeight: 400,
                    margin: 0,
                    color: 'var(--text-primary)',
                  }}
                >
                  {section.heading}
                </h2>
                <p
                  style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize: '0.96rem',
                    lineHeight: 1.9,
                    color: 'var(--text-secondary)',
                    marginTop: '1rem',
                    marginBottom: 0,
                  }}
                >
                  {section.body}
                </p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
