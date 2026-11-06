import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS, WORKFLOW_STEPS, COMPLIANCE_STATS, COMPLIANCE_ROWS, toFrames } from '../data';
import { Background, SlideUp, FadeIn, AnimatedNumber } from '../components';

// ============================================================
// Scene 4: Alur kerja dan fitur utama (audio-driven: ~107s)
// Audio: 6_25(25s) + 7_25(32s) + 8_25(23s) + Tahap1(3s) + Tahap2(4s) + 9_25(18s)
// Phase 1 Rencana: 0-25s, Phase 2 Checklist: 25-57s,
// Phase 3 Matriks: 57-80s, Phase 4 Berkas: 80-107s
// ============================================================
export const WorkflowScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  return (
    <Background>
      {/* Phase 1: Rencana (0-25s) */}
      {t < 25 && (
        <>
          <SlideUp delay={0.5} style={{ position: 'absolute', top: 60, left: 80, right: 80 }}>
            <h1 style={{ color: COLORS.text, fontSize: 42, fontWeight: 700, fontFamily: 'sans-serif', margin: 0 }}>
              Tahap 1 — Rencana
            </h1>
          </SlideUp>

          {/* Terminal mockup */}
          <FadeIn delay={1.5} style={{ position: 'absolute', top: 160, left: 120, right: 120 }}>
            <div style={{
              background: '#0c0e16',
              border: `1px solid ${COLORS.border}`,
              borderRadius: 12,
              overflow: 'hidden',
              fontFamily: 'monospace',
              fontSize: 22,
            }}>
              {/* Terminal title bar */}
              <div style={{
                background: COLORS.bgLight,
                padding: '10px 16px',
                display: 'flex',
                gap: 8,
                borderBottom: `1px solid ${COLORS.border}`,
              }}>
                <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#ff5f56' }} />
                <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#ffbd2e' }} />
                <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#27c93f' }} />
              </div>
              {/* Terminal content */}
              <div style={{ padding: 24, color: '#94a3b8' }}>
                <div style={{ color: COLORS.success }}>$ python src/pipeline.py rencana</div>
                <div style={{ marginTop: 16, opacity: interpolate(frame - toFrames(3), [0, toFrames(1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
                  <span style={{ color: COLORS.textDim }}>&gt; Membaca KAK...</span>
                </div>
                <div style={{ opacity: interpolate(frame - toFrames(5), [0, toFrames(1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
                  <span style={{ color: COLORS.textDim }}>&gt; Membaca profil perusahaan...</span>
                </div>
                <div style={{ opacity: interpolate(frame - toFrames(7), [0, toFrames(1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
                  <span style={{ color: COLORS.textDim }}>&gt; Ekstraksi persyaratan...</span>
                </div>
                <div style={{ opacity: interpolate(frame - toFrames(9), [0, toFrames(1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
                  <span style={{ color: COLORS.textDim }}>&gt; Verifikasi kutipan...</span>
                </div>
                <div style={{ marginTop: 16, opacity: interpolate(frame - toFrames(12), [0, toFrames(1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
                  <span style={{ color: COLORS.success }}>&#10003; 29 persyaratan diekstrak</span>
                </div>
                <div style={{ opacity: interpolate(frame - toFrames(14), [0, toFrames(1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
                  <span style={{ color: COLORS.success }}>&#10003; 29/29 kutipan terverifikasi</span>
                </div>
                <div style={{ marginTop: 16, opacity: interpolate(frame - toFrames(17), [0, toFrames(1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
                  <span style={{ color: COLORS.warning }}>&#9888; Keputusan: LOLOS BERSYARAT</span>
                </div>
              </div>
            </div>
          </FadeIn>

          {/* Stats row */}
          {t >= 18 && (
            <FadeIn delay={0} style={{ position: 'absolute', top: 560, left: 120, right: 120 }}>
              <div style={{ display: 'flex', justifyContent: 'center', gap: 60 }}>
                <StatCard label="Total syarat" value={29} color={COLORS.primary} delay={0} />
                <StatCard label="Memenuhi" value={22} color={COLORS.success} delay={1} />
                <StatCard label="Kurang dokumen" value={7} color={COLORS.accent} delay={2} />
                <StatCard label="Tidak memenuhi" value={0} color={COLORS.danger} delay={3} />
              </div>
            </FadeIn>
          )}
        </>
      )}

      {/* Phase 2: Checklist (25-57s) */}
      {t >= 25 && t < 57 && (
        <>
          <SlideUp delay={0} style={{ position: 'absolute', top: 60, left: 80, right: 80 }}>
            <h1 style={{ color: COLORS.text, fontSize: 42, fontWeight: 700, fontFamily: 'sans-serif', margin: 0 }}>
              Tahap 2 — Checklist Persyaratan
            </h1>
          </SlideUp>

          <FadeIn delay={1} style={{ position: 'absolute', top: 150, left: 120, right: 120 }}>
            <p style={{ color: COLORS.textDim, fontSize: 22, fontFamily: 'sans-serif', textAlign: 'center' }}>
              Setiap baris punya dokumen, bagian, dan kutipan.
              <br />
              Kalau kutipan tidak ditemukan, butir itu tidak dipakai untuk memutuskan.
            </p>
          </FadeIn>

          {/* Checklist table */}
          <FadeIn delay={3} style={{ position: 'absolute', top: 270, left: 120, right: 120 }}>
            <div style={{
              background: COLORS.surface,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 12,
              overflow: 'hidden',
            }}>
              {/* Header */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '120px 1fr 200px 100px',
                padding: '12px 20px',
                background: COLORS.bgLight,
                color: COLORS.textDim,
                fontSize: 16,
                fontFamily: 'sans-serif',
                fontWeight: 600,
                borderBottom: `1px solid ${COLORS.border}`,
              }}>
                <div>Kode</div>
                <div>Persyaratan</div>
                <div>Sumber</div>
                <div>Verifikasi</div>
              </div>
              {/* Rows */}
              {COMPLIANCE_ROWS.slice(0, 7).map((row, i) => {
                const rowDelay = 4 + i * 2;
                const rowOpacity = interpolate(
                  frame - toFrames(rowDelay),
                  [0, toFrames(0.5)],
                  [0, 1],
                  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
                );
                const rowTranslateY = interpolate(
                  frame - toFrames(rowDelay),
                  [0, toFrames(0.5)],
                  [10, 0],
                  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
                );

                const statusColor = row.status === 'memenuhi' ? COLORS.success :
                                   row.status === 'kurang' ? COLORS.accent : COLORS.danger;
                const statusLabel = row.status === 'memenuhi' ? 'MEMENUHI' :
                                   row.status === 'kurang' ? 'KURANG' : 'TIDAK';

                return (
                  <div
                    key={i}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '120px 1fr 200px 100px',
                      padding: '14px 20px',
                      borderBottom: i < 6 ? `1px solid ${COLORS.border}` : 'none',
                      opacity: rowOpacity,
                      transform: `translateY(${rowTranslateY}px)`,
                      alignItems: 'center',
                    }}
                  >
                    <div style={{ color: COLORS.textMuted, fontSize: 18, fontFamily: 'monospace' }}>
                      SYR-{String(i + 1).padStart(2, '0')}
                    </div>
                    <div style={{ color: COLORS.text, fontSize: 18, fontFamily: 'sans-serif' }}>
                      {row.requirement}
                    </div>
                    <div style={{ color: COLORS.textDim, fontSize: 16, fontFamily: 'sans-serif' }}>
                      KAK &sect; {i + 2}.1
                    </div>
                    <div style={{
                      display: 'inline-block',
                      padding: '4px 10px',
                      borderRadius: 6,
                      background: `${statusColor}22`,
                      border: `1px solid ${statusColor}`,
                      color: statusColor,
                      fontSize: 13,
                      fontWeight: 600,
                      fontFamily: 'sans-serif',
                      textAlign: 'center',
                    }}>
                      {statusLabel}
                    </div>
                  </div>
                );
              })}
            </div>
          </FadeIn>

          <FadeIn delay={25} style={{ position: 'absolute', bottom: 50, left: '15%', right: '15%' }}>
            <p style={{ color: COLORS.text, fontSize: 22, fontFamily: 'sans-serif', textAlign: 'center' }}>
              <span style={{ color: COLORS.accent }}>Tidak ada syarat yang "kedengarannya masuk akal" tapi sebenarnya tidak ada.</span>
            </p>
          </FadeIn>
        </>
      )}

      {/* Phase 3: Matriks (57-80s) */}
      {t >= 57 && t < 80 && (
        <>
          <SlideUp delay={0} style={{ position: 'absolute', top: 60, left: 80, right: 80 }}>
            <h1 style={{ color: COLORS.text, fontSize: 42, fontWeight: 700, fontFamily: 'sans-serif', margin: 0 }}>
              Tahap 3 — Matriks Kepatuhan
            </h1>
          </SlideUp>

          <FadeIn delay={1} style={{ position: 'absolute', top: 140, left: 120, right: 120 }}>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 24 }}>
              {/* Three status legend */}
              {[
                { label: 'Memenuhi', desc: 'Bukti ada, masih berlaku, nilai cukup', color: COLORS.success },
                { label: 'Kurang Dokumen', desc: 'Bukti tidak ada', color: COLORS.accent },
                { label: 'Tidak Memenuhi', desc: 'Bukti ada tapi gagal', color: COLORS.danger },
              ].map((s, i) => (
                <FadeIn key={s.label} delay={1 + i * 1}>
                  <div style={{
                    background: `${s.color}11`,
                    border: `1px solid ${s.color}`,
                    borderRadius: 10,
                    padding: '12px 24px',
                    textAlign: 'center',
                    width: 300,
                  }}>
                    <div style={{ color: s.color, fontSize: 20, fontWeight: 700, fontFamily: 'sans-serif' }}>
                      {s.label}
                    </div>
                    <div style={{ color: COLORS.textDim, fontSize: 14, fontFamily: 'sans-serif', marginTop: 4 }}>
                      {s.desc}
                    </div>
                  </div>
                </FadeIn>
              ))}
            </div>
          </FadeIn>

          {/* Highlight: Ahli K3 */}
          <FadeIn delay={6} style={{ position: 'absolute', top: 280, left: 120, right: 120 }}>
            <div style={{
              background: COLORS.surface,
              border: `2px solid ${COLORS.accent}`,
              borderRadius: 16,
              padding: 32,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
                <span style={{ color: COLORS.accent, fontSize: 28, fontWeight: 700, fontFamily: 'sans-serif' }}>
                  Ahli K3
                </span>
                <div style={{
                  padding: '4px 14px',
                  borderRadius: 6,
                  background: `${COLORS.accent}22`,
                  border: `1px solid ${COLORS.accent}`,
                  color: COLORS.accent,
                  fontSize: 16,
                  fontWeight: 600,
                }}>
                  KURANG DOKUMEN
                </div>
              </div>
              <p style={{ color: COLORS.text, fontSize: 20, fontFamily: 'sans-serif', lineHeight: 1.6, margin: 0 }}>
                Punya SKK Konstruksi. Tapi KAK juga meminta sertifikat Ahli K3 Umum dari Kemenaker.
                <br />
                Itu belum terbit. Statusnya <span style={{ color: COLORS.accent, fontWeight: 700 }}>kurang dokumen</span> &mdash;
                bukan memenuhi. Agen tidak mengisi nomor sertifikat yang belum ada.
              </p>
            </div>
          </FadeIn>

          {/* Highlight: Pengalaman #4 */}
          <FadeIn delay={12} style={{ position: 'absolute', top: 500, left: 120, right: 120 }}>
            <div style={{
              background: COLORS.surface,
              border: `2px solid ${COLORS.danger}`,
              borderRadius: 16,
              padding: 28,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ color: COLORS.danger, fontSize: 24, fontWeight: 700, fontFamily: 'sans-serif' }}>
                  Pengalaman #4 — Nilai Rp2M
                </span>
                <div style={{
                  padding: '4px 14px',
                  borderRadius: 6,
                  background: `${COLORS.danger}22`,
                  border: `1px solid ${COLORS.danger}`,
                  color: COLORS.danger,
                  fontSize: 16,
                  fontWeight: 600,
                }}>
                  DIKECUALIKAN
                </div>
              </div>
              <p style={{ color: COLORS.textDim, fontSize: 18, fontFamily: 'sans-serif', marginTop: 12, marginBottom: 0 }}>
                Dikerjakan sebagai subkontraktor. KAK melarangnya. Agen menangkap itu.
              </p>
            </div>
          </FadeIn>
        </>
      )}

      {/* Phase 4: Berkas (80-107s) */}
      {t >= 80 && (
        <>
          <SlideUp delay={0} style={{ position: 'absolute', top: 60, left: 80, right: 80 }}>
            <h1 style={{ color: COLORS.text, fontSize: 42, fontWeight: 700, fontFamily: 'sans-serif', margin: 0 }}>
              Tahap 4 — Berkas Dihasilkan
            </h1>
          </SlideUp>

          <FadeIn delay={1} style={{ position: 'absolute', top: 150, left: 120, right: 120 }}>
            <p style={{ color: COLORS.textDim, fontSize: 22, fontFamily: 'sans-serif', textAlign: 'center' }}>
              Setelah disetujui, lima dokumen ditulis.
            </p>
          </FadeIn>

          {/* Five document cards */}
          <div style={{ position: 'absolute', top: 240, left: 80, right: 80, display: 'flex', justifyContent: 'center', gap: 20, flexWrap: 'wrap' }}>
            {[
              { name: '01_Surat_Penawaran.docx', note: 'Nilai penawaran dikosongkan', highlight: true },
              { name: '02_Pakta_Integritas.docx', note: 'Standard template', highlight: false },
              { name: '03_Daftar_Personil_Inti.docx', note: 'Ahli K3: BELUM ADA (merah)', highlight: true },
              { name: '04_Tabel_Pengalaman.docx', note: 'Pengalaman #4 dikecualikan', highlight: false },
              { name: '05_Daftar_Persyaratan.docx', note: '29 butir bersumber', highlight: false },
            ].map((doc, i) => (
              <FadeIn key={doc.name} delay={2 + i * 1.5}>
                <div style={{
                  width: 320,
                  background: COLORS.surface,
                  border: `1px solid ${doc.highlight ? COLORS.accent : COLORS.border}`,
                  borderRadius: 12,
                  padding: 24,
                }}>
                  <div style={{
                    fontSize: 32,
                    marginBottom: 12,
                  }}>
                    {doc.highlight ? '&#128196;' : '&#128221;'}
                  </div>
                  <div style={{
                    color: COLORS.text,
                    fontSize: 16,
                    fontFamily: 'monospace',
                    fontWeight: 600,
                    wordBreak: 'break-all',
                  }}>
                    {doc.name}
                  </div>
                  <div style={{
                    color: doc.highlight ? COLORS.accent : COLORS.textDim,
                    fontSize: 14,
                    fontFamily: 'sans-serif',
                    marginTop: 8,
                  }}>
                    {doc.note}
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>

          {/* Honesty callout */}
          <FadeIn delay={15} style={{ position: 'absolute', top: 560, left: '20%', right: '20%' }}>
            <div style={{
              background: `${COLORS.accent}11`,
              border: `2px solid ${COLORS.accent}`,
              borderRadius: 16,
              padding: '28px 40px',
              textAlign: 'center',
            }}>
              <p style={{
                color: COLORS.text,
                fontSize: 24,
                fontFamily: 'sans-serif',
                margin: 0,
                lineHeight: 1.6,
              }}>
                Nilai penawaran sengaja dikosongkan.
                <br />
                <span style={{ color: COLORS.accent, fontWeight: 700 }}>
                  Itu keputusan komersial direktur, bukan wewenang agen.
                </span>
                <br />
                Lebih baik kosong dan jujur daripada terisi tapi salah.
              </p>
            </div>
          </FadeIn>
        </>
      )}
    </Background>
  );
};

// Helper: Stat card
const StatCard: React.FC<{
  label: string;
  value: number;
  color: string;
  delay: number;
}> = ({ label, value, color, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame: frame - toFrames(delay),
    fps,
    config: { damping: 200 },
  });

  return (
    <div style={{
      width: 220,
      background: COLORS.surface,
      border: `1px solid ${color}`,
      borderRadius: 12,
      padding: '20px 24px',
      textAlign: 'center',
      transform: `scale(${scale})`,
    }}>
      <AnimatedNumber value={value} delay={delay} fontSize={56} color={color} />
      <div style={{ color: COLORS.textDim, fontSize: 16, fontFamily: 'sans-serif', marginTop: 4 }}>
        {label}
      </div>
    </div>
  );
};
