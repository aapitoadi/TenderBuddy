import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS, toFrames } from '../data';
import { Background, SlideUp, FadeIn } from '../components';

// ============================================================
// Scene 6: Nilai WorkBuddy dan refleksi (audio-driven: ~13s)
// Audio: 11_25 (11.7s)
// Single phase — compressed reveal of both cards + core value
// ============================================================
export const ReflectionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  return (
    <Background>
      <SlideUp delay={0.3} style={{ position: 'absolute', top: 40, left: 80, right: 80 }}>
        <h1 style={{ color: COLORS.text, fontSize: 42, fontWeight: 700, fontFamily: 'sans-serif', margin: 0 }}>
          Nilai WorkBuddy
        </h1>
      </SlideUp>

      <div style={{ position: 'absolute', top: 140, left: 80, right: 80, display: 'flex', gap: 40 }}>
        {/* Card 1: Folder kerja */}
        <FadeIn delay={1} style={{ flex: 1 }}>
          <div style={{
            background: COLORS.surface,
            border: `1px solid ${COLORS.primary}`,
            borderRadius: 16,
            padding: 28,
          }}>
            <div style={{ color: COLORS.primary, fontSize: 48, fontWeight: 700, fontFamily: 'sans-serif' }}>1</div>
            <h3 style={{ color: COLORS.text, fontSize: 22, fontFamily: 'sans-serif', margin: '8px 0' }}>
              Folder kerja sebagai unit
            </h3>
            <p style={{ color: COLORS.textDim, fontSize: 16, fontFamily: 'sans-serif', lineHeight: 1.5, margin: 0 }}>
              Agen, aturan, input, output, dan tes di satu tempat.
            </p>
          </div>
        </FadeIn>

        {/* Card 2: AGENTS.md */}
        <FadeIn delay={2} style={{ flex: 1 }}>
          <div style={{
            background: COLORS.surface,
            border: `1px solid ${COLORS.accent}`,
            borderRadius: 16,
            padding: 28,
          }}>
            <div style={{ color: COLORS.accent, fontSize: 48, fontWeight: 700, fontFamily: 'sans-serif' }}>2</div>
            <h3 style={{ color: COLORS.text, fontSize: 22, fontFamily: 'sans-serif', margin: '8px 0' }}>
              AGENTS.md sebagai kebijakan
            </h3>
            <p style={{ color: COLORS.textDim, fontSize: 16, fontFamily: 'sans-serif', lineHeight: 1.5, margin: 0 }}>
              Tujuh prinsip yang mengikat seluruh sesi.
            </p>
          </div>
        </FadeIn>
      </div>

      {/* Core value — the punchline */}
      <FadeIn delay={5} style={{ position: 'absolute', top: 440, left: '10%', right: '10%' }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: COLORS.textDim, fontSize: 22, fontFamily: 'sans-serif', marginBottom: 20 }}>
            Nilai TenderBuddy bukan kecepatan menulis.
          </p>
          <div style={{
            display: 'inline-block',
            background: `${COLORS.accent}11`,
            border: `3px solid ${COLORS.accent}`,
            borderRadius: 20,
            padding: '24px 60px',
          }}>
            <h1 style={{
              color: COLORS.accent,
              fontSize: 48,
              fontWeight: 700,
              fontFamily: 'sans-serif',
              margin: 0,
            }}>
              Nilainya adalah keberanian berhenti.
            </h1>
          </div>
        </div>
      </FadeIn>
    </Background>
  );
};
