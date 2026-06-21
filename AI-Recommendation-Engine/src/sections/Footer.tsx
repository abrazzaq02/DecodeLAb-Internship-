import { footerConfig } from '../config';

export default function Footer() {
  const hasFooterContent =
    footerConfig.visitLabel ||
    footerConfig.visitLines.length > 0 ||
    footerConfig.connectLabel ||
    footerConfig.connectLinks.length > 0 ||
    footerConfig.brandName ||
    footerConfig.rightsText ||
    footerConfig.coordinatesText;

  if (!hasFooterContent) {
    return null;
  }

  return (
    <footer
      id="contact"
      style={{
        background: 'var(--bg-primary)',
        padding: '8rem 4vw 4rem',
        position: 'relative',
        zIndex: 2,
        borderTop: '1px solid #e5e5e5',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '8rem',
        }}
      >
        {(footerConfig.visitLabel || footerConfig.visitLines.length > 0) && (
          <div>
            <p
              style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '0.7rem',
                fontWeight: 500,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'var(--text-secondary)',
                marginBottom: '1.5rem',
              }}
            >
              {footerConfig.visitLabel}
            </p>
            <p
              style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '0.85rem',
                lineHeight: 1.8,
                color: 'var(--text-primary)',
              }}
            >
              {footerConfig.visitLines.map((line, index) => (
                <span key={`${line}-${index}`}>
                  {line}
                  {index < footerConfig.visitLines.length - 1 && <br />}
                </span>
              ))}
            </p>
          </div>
        )}

        {(footerConfig.connectLabel || footerConfig.connectLinks.length > 0) && (
          <div style={{ textAlign: 'right' }}>
            <p
              style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '0.7rem',
                fontWeight: 500,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'var(--text-secondary)',
                marginBottom: '1.5rem',
              }}
            >
              {footerConfig.connectLabel}
            </p>
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
                alignItems: 'flex-end',
              }}
            >
              {footerConfig.connectLinks.map((item) => (
                <a
                  key={`${item.label}-${item.href}`}
                  href={item.href}
                  style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)',
                    textDecoration: 'none',
                    position: 'relative',
                  }}
                  onMouseEnter={(e) => {
                    (e.target as HTMLElement).style.opacity = '0.5';
                  }}
                  onMouseLeave={(e) => {
                    (e.target as HTMLElement).style.opacity = '1';
                  }}
                >
                  {item.label}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>

      {footerConfig.brandName && (
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(4rem, 12vw, 12rem)',
            fontWeight: 400,
            lineHeight: 0.85,
            letterSpacing: '-0.03em',
            color: 'var(--text-primary)',
            textTransform: 'uppercase',
            textWrap: 'balance',
          }}
        >
          {footerConfig.brandName}
        </div>
      )}

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '3rem',
          paddingTop: '1.5rem',
          borderTop: '1px solid #e5e5e5',
        }}
      >
        <span
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '0.65rem',
            color: 'var(--text-secondary)',
            letterSpacing: '0.05em',
          }}
        >
          {footerConfig.rightsText}
        </span>
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.65rem',
            color: 'var(--text-secondary)',
          }}
        >
          {footerConfig.coordinatesText}
        </span>
      </div>
    </footer>
  );
}
