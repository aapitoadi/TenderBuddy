import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS, toFrames } from '../data';
import { Background, FadeIn } from '../components';

// ============================================================
// Scene 7: Penutup (405-410s = 5s, silent — no audio)
// Quick title + tagline + badges + terima kasih
// ============================================================
export const ClosingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = spring({
    frame: frame - toFrames(0.5),
    fps,
    config: { damping: 200 },
  });

  return (
    <Background>
      {/* Title */}
      <div style={{
        position: 'absolute',
        top: '25%',
        left: '10%',
        right: '10%',
        textAlign: 'center',
        transform: `scale(${titleScale})`,
      }}>
        <h1 style={{
          color: COLORS.text,
          fontSize: 72,
          fontWeight: 700,
          fontFamily: 'sans-serif',
          margin: 0,
        }}>
          TenderBuddy
        </h1>
      </div>

      {/* Tagline */}
      <FadeIn delay={1.5} style={{ position: 'absolute', top: '42%', left: '10%', right: '10%' }}>
        <p style={{
          color: COLORS.textDim,
          fontSize: 24,
          fontFamily: 'sans-serif',
          textAlign: 'center',
          lineHeight: 1.6,
          margin: 0,
        }}>
          Dari paket tender LPSE ke berkas penawaran siap tanda tangan
          <br />
          <span style={{ color: COLORS.accent }}>dengan sumber yang bisa diperiksa</span>
          <br />
          <span style={{ color: COLORS.danger }}>dan gerbang yang tidak bisa dilewati</span>
        </p>
      </FadeIn>

      {/* Badges */}
      <FadeIn delay={2.5} style={{ position: 'absolute', top: '68%', left: '10%', right: '10%', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', gap: 24 }}>
          <div style={{
            padding: '8px 24px',
            borderRadius: 8,
            background: `${COLORS.purple}22`,
            border: `1px solid ${COLORS.purple}`,
            color: COLORS.purple,
            fontSize: 20,
            fontWeight: 600,
            fontFamily: 'sans-serif',
          }}>
            Track B — Agen Kantor
          </div>
          <div style={{
            padding: '8px 24px',
            borderRadius: 8,
            background: `${COLORS.primary}22`,
            border: `1px solid ${COLORS.primary}`,
            color: COLORS.primary,
            fontSize: 20,
            fontWeight: 600,
            fontFamily: 'sans-serif',
          }}>
            WorkBuddy AI
          </div>
        </div>
      </FadeIn>

      {/* Terima kasih */}
      <FadeIn delay={3.5} style={{ position: 'absolute', bottom: 60, left: '10%', right: '10%' }}>
        <p style={{
          color: COLORS.textMuted,
          fontSize: 24,
          fontFamily: 'sans-serif',
          textAlign: 'center',
        }}>
          Terima kasih.
        </p>
      </FadeIn>
    </Background>
  );
};
