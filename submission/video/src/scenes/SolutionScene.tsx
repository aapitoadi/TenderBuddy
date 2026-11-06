import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS, toFrames } from '../data';
import { Background, SlideUp, FadeIn, Badge, ScaleIn } from '../components';

// ============================================================
// Scene 2: Solusi dan track (audio-driven: ~87s)
// Audio: 3_25 (61s) + 4_25 (25s)
// Phase 1: 0-61s (TenderBuddy intro — matches 3_25)
// Phase 2: 61-87s (Track B + decision — matches 4_25)
// ============================================================
export const SolutionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  return (
    <Background>
      {/* Phase 1: TenderBuddy intro (0-61s) */}
      {t < 61 && (
        <>
          <SlideUp delay={0.5} style={{ position: 'absolute', top: '22%', left: '10%', right: '10%' }}>
            <h1 style={{
              color: COLORS.text,
              fontSize: 64,
              fontWeight: 700,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              margin: 0,
            }}>
              TenderBuddy
            </h1>
          </SlideUp>

          <SlideUp delay={3} style={{ position: 'absolute', top: '36%', left: '10%', right: '10%' }}>
            <p style={{
              color: COLORS.textDim,
              fontSize: 26,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              lineHeight: 1.6,
            }}>
              Satu perintah: lempar paketnya.
              <br />
              Agen mengembalikan checklist, matriks kepatuhan, dan berkas siap tanda tangan.
            </p>
          </SlideUp>

          <div style={{ position: 'absolute', top: '55%', left: '15%', right: '15%', display: 'flex', justifyContent: 'center', gap: 30 }}>
            <ScaleIn delay={8}>
              <div style={{
                background: COLORS.surface,
                border: `1px solid ${COLORS.primary}`,
                borderRadius: 16,
                padding: '24px 36px',
                textAlign: 'center',
                width: 280,
              }}>
                <div style={{ color: COLORS.primary, fontSize: 48, fontWeight: 700, fontFamily: 'sans-serif' }}>
                  Checklist
                </div>
                <div style={{ color: COLORS.textDim, fontSize: 18, fontFamily: 'sans-serif', marginTop: 8 }}>
                  persyaratan bersumber
                </div>
              </div>
            </ScaleIn>

            <ScaleIn delay={10}>
              <div style={{
                background: COLORS.surface,
                border: `1px solid ${COLORS.accent}`,
                borderRadius: 16,
                padding: '24px 36px',
                textAlign: 'center',
                width: 280,
              }}>
                <div style={{ color: COLORS.accent, fontSize: 48, fontWeight: 700, fontFamily: 'sans-serif' }}>
                  Matriks
                </div>
                <div style={{ color: COLORS.textDim, fontSize: 18, fontFamily: 'sans-serif', marginTop: 8 }}>
                  kepatuhan profil
                </div>
              </div>
            </ScaleIn>

            <ScaleIn delay={12}>
              <div style={{
                background: COLORS.surface,
                border: `1px solid ${COLORS.success}`,
                borderRadius: 16,
                padding: '24px 36px',
                textAlign: 'center',
                width: 280,
              }}>
                <div style={{ color: COLORS.success, fontSize: 48, fontWeight: 700, fontFamily: 'sans-serif' }}>
                  Berkas
                </div>
                <div style={{ color: COLORS.textDim, fontSize: 18, fontFamily: 'sans-serif', marginTop: 8 }}>
                  siap ditandatangani
                </div>
              </div>
            </ScaleIn>
          </div>
        </>
      )}

      {/* Phase 2: Track B + decision (61-87s) */}
      {t >= 61 && (
        <>
          <FadeIn delay={0} style={{ position: 'absolute', top: '15%', left: '10%', right: '10%', textAlign: 'center' }}>
            <Badge text="Track B — Agen Kantor" color={COLORS.purple} delay={0} />
          </FadeIn>

          <FadeIn delay={2} style={{ position: 'absolute', top: '25%', left: '10%', right: '10%' }}>
            <p style={{
              color: COLORS.text,
              fontSize: 26,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              lineHeight: 1.6,
            }}>
              Satu permintaan tidak terstruktur diubah menjadi rencana tindakan yang jelas.
              <br />
              Tidak ada yang dieksekusi sebelum manusia setuju.
            </p>
          </FadeIn>

          <FadeIn delay={6} style={{ position: 'absolute', top: '42%', left: '25%', right: '25%' }}>
            <div style={{
              background: COLORS.surface,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 20,
              padding: '40px 60px',
              textAlign: 'center',
            }}>
              <div style={{ color: COLORS.textDim, fontSize: 18, fontFamily: 'sans-serif', marginBottom: 16 }}>
                Keputusan paket
              </div>
              <div style={{
                display: 'inline-block',
                background: `${COLORS.warning}22`,
                border: `2px solid ${COLORS.warning}`,
                borderRadius: 12,
                padding: '16px 48px',
                color: COLORS.warning,
                fontSize: 40,
                fontWeight: 700,
                fontFamily: 'sans-serif',
              }}>
                LOLOS BERSYARAT
              </div>
              <div style={{ color: COLORS.textDim, fontSize: 20, fontFamily: 'sans-serif', marginTop: 16 }}>
                Bukan "lolos" — karena 3 dokumen belum ada
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={16} style={{ position: 'absolute', top: '70%', left: '15%', right: '15%' }}>
            <p style={{
              color: COLORS.text,
              fontSize: 24,
              fontFamily: 'sans-serif',
              textAlign: 'center',
            }}>
              <span style={{ color: COLORS.accent, fontWeight: 700 }}>Bedanya dengan asisten dokumen biasa:</span>
              <br />
              TenderBuddy dirancang untuk berhenti.
            </p>
          </FadeIn>
        </>
      )}
    </Background>
  );
};
