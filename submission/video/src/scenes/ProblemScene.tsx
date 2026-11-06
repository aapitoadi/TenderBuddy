import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS, toFrames } from '../data';
import { Background, SlideUp, AnimatedNumber, FadeIn } from '../components';

// ============================================================
// Scene 1: Masalah dan pengguna (audio-driven: ~86s)
// Audio: 1_25 (44s) + 2_25 (40s)
// Phase 1: 0-44s (Rani intro — matches 1_25)
// Phase 2: 44-66s (The work — first part of 2_25)
// Phase 3: 66-86s (The costly mistake — second part of 2_25)
// ============================================================
export const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const t = frame / fps;

  return (
    <Background>
      {/* Phase 1: The person (0-44s) */}
      {t < 44 && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
          <SlideUp delay={0.5} style={{ position: 'absolute', top: '20%', left: '10%', right: '10%' }}>
            <div style={{ color: COLORS.textDim, fontSize: 20, fontFamily: 'sans-serif', textAlign: 'center' }}>
              Balikpapan · Perusahaan konstruksi kecil · 24 pegawai
            </div>
          </SlideUp>

          <SlideUp delay={1.5} style={{ position: 'absolute', top: '30%', left: '10%', right: '10%' }}>
            <h1 style={{
              color: COLORS.text,
              fontSize: 56,
              fontWeight: 700,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              margin: 0,
            }}>
              Rani
            </h1>
            <p style={{
              color: COLORS.textDim,
              fontSize: 24,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              marginTop: 12,
            }}>
              Setiap musim tender, ia menerima paket dari LPSE
            </p>
          </SlideUp>

          <SlideUp delay={5} style={{ position: 'absolute', top: '52%', left: '15%', right: '15%' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: 40,
            }}>
              {['KAK', 'LDP', 'LDK', 'Addendum'].map((doc, i) => (
                <div
                  key={doc}
                  style={{
                    background: COLORS.surface,
                    border: `1px solid ${COLORS.border}`,
                    borderRadius: 12,
                    padding: '20px 32px',
                    color: COLORS.text,
                    fontSize: 24,
                    fontFamily: 'monospace',
                    opacity: interpolate(
                      frame - toFrames(5 + i * 0.8),
                      [0, toFrames(0.5)],
                      [0, 1],
                      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
                    ),
                  }}
                >
                  {doc}
                </div>
              ))}
            </div>
          </SlideUp>

          <SlideUp delay={10} style={{ position: 'absolute', top: '72%', left: '20%', right: '20%' }}>
            <div style={{
              color: COLORS.accent,
              fontSize: 32,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              fontWeight: 600,
            }}>
              40 – 100 halaman per paket
            </div>
          </SlideUp>
        </div>
      )}

      {/* Phase 2: The work (44-66s) */}
      {t >= 44 && t < 66 && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
          <FadeIn delay={0} style={{ position: 'absolute', top: '18%', left: '10%', right: '10%' }}>
            <p style={{
              color: COLORS.text,
              fontSize: 28,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              lineHeight: 1.6,
            }}>
              Tugasnya: menemukan semua syarat, mencocokkan dengan arsip,
              <br />
              lalu mengetik surat penawaran, pakta integritas, daftar personil,
              <br />
              dan tabel pengalaman.
            </p>
          </FadeIn>

          <FadeIn delay={4} style={{ position: 'absolute', top: '48%', left: '25%', right: '25%' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 60,
            }}>
              <div style={{ textAlign: 'center' }}>
                <AnimatedNumber value={1} delay={2} suffix=" paket" fontSize={64} color={COLORS.accent} />
                <div style={{ color: COLORS.textDim, fontSize: 20, fontFamily: 'sans-serif', marginTop: 8 }}>
                  per musim
                </div>
              </div>
              <div style={{ color: COLORS.textMuted, fontSize: 48, fontWeight: 300 }}>=</div>
              <div style={{ textAlign: 'center' }}>
                <AnimatedNumber value={2} delay={4} suffix=" hari" fontSize={64} color={COLORS.danger} />
                <div style={{ color: COLORS.textDim, fontSize: 20, fontFamily: 'sans-serif', marginTop: 8 }}>
                  kerja
                </div>
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={9} style={{ position: 'absolute', top: '75%', left: '30%', right: '30%' }}>
            <div style={{
              color: COLORS.textDim,
              fontSize: 22,
              fontFamily: 'sans-serif',
              textAlign: 'center',
            }}>
              <AnimatedNumber value={40} delay={7} suffix=" paket/tahun" fontSize={32} color={COLORS.textDim} />
            </div>
          </FadeIn>
        </div>
      )}

      {/* Phase 3: The costly mistake (66-86s) */}
      {t >= 66 && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
          <FadeIn delay={0} style={{ position: 'absolute', top: '20%', left: '10%', right: '10%' }}>
            <p style={{
              color: COLORS.text,
              fontSize: 28,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              lineHeight: 1.6,
            }}>
              Dan kesalahan yang paling mahal bukan salah ketik.
            </p>
          </FadeIn>

          <FadeIn delay={4} style={{ position: 'absolute', top: '35%', left: '15%', right: '15%' }}>
            <div style={{
              background: `${COLORS.danger}11`,
              border: `2px solid ${COLORS.danger}`,
              borderRadius: 16,
              padding: '32px 48px',
              display: 'flex',
              flexDirection: 'column',
              gap: 20,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ color: COLORS.danger, fontSize: 32, fontWeight: 700 }}>&#9888;</span>
                <span style={{ color: COLORS.text, fontSize: 24, fontFamily: 'sans-serif' }}>
                  Satu sertifikat yang sudah kadaluarsa
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ color: COLORS.danger, fontSize: 32, fontWeight: 700 }}>&#9888;</span>
                <span style={{ color: COLORS.text, fontSize: 24, fontFamily: 'sans-serif' }}>
                  Satu klaim pengalaman tanpa kontrak pendukung
                </span>
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={9} style={{ position: 'absolute', top: '68%', left: '20%', right: '20%' }}>
            <p style={{
              color: COLORS.danger,
              fontSize: 36,
              fontFamily: 'sans-serif',
              textAlign: 'center',
              fontWeight: 700,
            }}>
              Cukup untuk menggugurkan penawaran
              <br />
              atau berujung sanksi daftar hitam 2 tahun
            </p>
          </FadeIn>
        </div>
      )}
    </Background>
  );
};
