import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS, ARCH_ZONES, toFrames } from '../data';
import { Background, SlideUp, FadeIn, SceneTitle } from '../components';

// ============================================================
// Scene 3: Arsitektur dan trust boundary (audio-driven: ~67s)
// Audio: 4_1_25 (13s) + 5_25 (52s)
// Zones appear gradually, gate at ~20s, bottom note at ~50s
// ============================================================
export const ArchitectureScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const zoneWidth = 520;
  const zoneHeight = 420;
  const gap = 40;
  const totalWidth = zoneWidth * 3 + gap * 2;
  const startX = (1920 - totalWidth) / 2;

  return (
    <Background>
      <SceneTitle title="Arsitektur Tiga Zona" subtitle="Dibagi budasarkan hak akses, bukan jenis komponen" delay={0.5} />

      {/* Three zones */}
      <div style={{
        position: 'absolute',
        top: 200,
        left: startX,
        display: 'flex',
        gap,
      }}>
        {ARCH_ZONES.map((zone, i) => {
          const appearFrame = toFrames(3 + i * 4);
          const scale = spring({
            frame: frame - appearFrame,
            fps,
            config: { damping: 200 },
          });
          const opacity = interpolate(scale, [0, 1], [0, 1], { extrapolateRight: 'clamp' });

          return (
            <div
              key={zone.name}
              style={{
                width: zoneWidth,
                height: zoneHeight,
                background: `${zone.color}11`,
                border: `2px solid ${zone.color}`,
                borderRadius: 20,
                padding: 32,
                transform: `scale(${scale})`,
                opacity,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* Zone name */}
              <h2 style={{
                color: zone.color,
                fontSize: 32,
                fontWeight: 700,
                fontFamily: 'sans-serif',
                margin: 0,
              }}>
                {zone.name}
              </h2>
              <p style={{
                color: COLORS.textDim,
                fontSize: 16,
                fontFamily: 'sans-serif',
                marginTop: 8,
                lineHeight: 1.4,
              }}>
                {zone.subtitle}
              </p>

              {/* Rights */}
              <div style={{
                marginTop: 20,
                background: `${COLORS.bg}88`,
                borderRadius: 10,
                padding: '12px 16px',
              }}>
                <div style={{ color: COLORS.textMuted, fontSize: 14, fontFamily: 'sans-serif' }}>
                  Hak agen
                </div>
                <div style={{ color: COLORS.text, fontSize: 18, fontFamily: 'sans-serif', fontWeight: 600 }}>
                  {zone.rights}
                </div>
              </div>

              {/* Guards (only for Zona Putus) */}
              {zone.guards.length > 0 && (
                <div style={{ marginTop: 20 }}>
                  <div style={{ color: COLORS.textMuted, fontSize: 14, fontFamily: 'sans-serif', marginBottom: 10 }}>
                    Empat penjaga (tugas: menggagalkan)
                  </div>
                  {zone.guards.map((guard, gi) => {
                    const guardDelay = toFrames(8 + i * 4 + gi * 2);
                    const guardScale = spring({
                      frame: frame - guardDelay,
                      fps,
                      config: { damping: 200 },
                    });
                    return (
                      <div
                        key={guard}
                        style={{
                          background: `${zone.color}22`,
                          border: `1px dashed ${zone.color}`,
                          borderRadius: 8,
                          padding: '8px 14px',
                          marginBottom: 8,
                          color: COLORS.text,
                          fontSize: 16,
                          fontFamily: 'sans-serif',
                          opacity: interpolate(guardScale, [0, 1], [0, 1], { extrapolateRight: 'clamp' }),
                          transform: `translateX(${interpolate(guardScale, [0, 1], [-20, 0])}px)`,
                        }}
                      >
                        {guard}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Boundary */}
              <div style={{
                marginTop: 'auto',
                background: `${COLORS.bg}88`,
                borderRadius: 10,
                padding: '12px 16px',
                borderTop: `2px solid ${zone.color}`,
              }}>
                <div style={{ color: COLORS.textMuted, fontSize: 14, fontFamily: 'sans-serif' }}>
                  Pemeriksaan di batas
                </div>
                <div style={{ color: COLORS.text, fontSize: 15, fontFamily: 'sans-serif', marginTop: 4 }}>
                  {zone.boundary}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Approval gate line */}
      {t >= 20 && (
        <FadeIn delay={0} style={{
          position: 'absolute',
          top: 200,
          left: startX + zoneWidth * 2 + gap - 4,
          width: 8,
          height: zoneHeight,
        }}>
          <div style={{
            width: '100%',
            height: '100%',
            background: `linear-gradient(to bottom, transparent, ${COLORS.danger}, transparent)`,
            borderRadius: 4,
          }} />
        </FadeIn>
      )}

      {t >= 22 && (
        <FadeIn delay={0} style={{
          position: 'absolute',
          top: 200 + zoneHeight + 10,
          left: startX + zoneWidth * 2 + gap - 120,
          width: 240,
        }}>
          <div style={{
            background: `${COLORS.danger}22`,
            border: `2px solid ${COLORS.danger}`,
            borderRadius: 8,
            padding: '8px 16px',
            textAlign: 'center',
          }}>
            <div style={{ color: COLORS.danger, fontSize: 16, fontWeight: 700, fontFamily: 'sans-serif' }}>
              GERBANG PERSETUJUAN
            </div>
          </div>
        </FadeIn>
      )}

      {/* Bottom note */}
      {t >= 45 && (
        <FadeIn delay={0} style={{ position: 'absolute', bottom: 60, left: '10%', right: '10%' }}>
          <p style={{
            color: COLORS.text,
            fontSize: 22,
            fontFamily: 'sans-serif',
            textAlign: 'center',
            lineHeight: 1.5,
          }}>
            <span style={{ color: COLORS.accent, fontWeight: 700 }}>Keputusan lolos/tidak lolos dibuat deterministik</span>
            <br />
            Pada tender, hasil yang "hampir benar" sama nilainya dengan hasil yang salah.
          </p>
        </FadeIn>
      )}
    </Background>
  );
};
