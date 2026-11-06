import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS, toFrames } from './data';

// ============================================================
// FadeIn — simple opacity fade driven by frame
// ============================================================
export const FadeIn: React.FC<{
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, duration = 1, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(
    frame - toFrames(delay),
    [0, toFrames(duration)],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  return <div style={{ ...style, opacity }}>{children}</div>;
};

// ============================================================
// SlideUp — slide from below with fade
// ============================================================
export const SlideUp: React.FC<{
  children: React.ReactNode;
  delay?: number;
  distance?: number;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, distance = 40, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - toFrames(delay),
    fps,
    config: { damping: 200 },
  });

  const translateY = interpolate(progress, [0, 1], [distance, 0]);
  const opacity = interpolate(progress, [0, 1], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ ...style, transform: `translateY(${translateY}px)`, opacity }}>
      {children}
    </div>
  );
};

// ============================================================
// ScaleIn — scale from small with spring
// ============================================================
export const ScaleIn: React.FC<{
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame: frame - toFrames(delay),
    fps,
    config: { damping: 200 },
  });

  return (
    <div style={{ ...style, transform: `scale(${scale})` }}>{children}</div>
  );
};

// ============================================================
// Background — dark gradient background
// ============================================================
export const Background: React.FC<{ children?: React.ReactNode }> = ({
  children,
}) => {
  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `radial-gradient(ellipse at 50% 30%, ${COLORS.bgLight} 0%, ${COLORS.bg} 70%)`,
      }}
    >
      {children}
    </div>
  );
};

// ============================================================
// SceneTitle — large title with subtitle
// ============================================================
export const SceneTitle: React.FC<{
  title: string;
  subtitle?: string;
  delay?: number;
}> = ({ title, subtitle, delay = 0 }) => {
  return (
    <div
      style={{
        position: 'absolute',
        top: 60,
        left: 80,
        right: 80,
      }}
    >
      <SlideUp delay={delay}>
        <h1
          style={{
            color: COLORS.text,
            fontSize: 42,
            fontWeight: 700,
            margin: 0,
            fontFamily: 'sans-serif',
          }}
        >
          {title}
        </h1>
      </SlideUp>
      {subtitle && (
        <SlideUp delay={delay + 0.3}>
          <p
            style={{
              color: COLORS.textDim,
              fontSize: 22,
              fontWeight: 400,
              margin: '8px 0 0 0',
              fontFamily: 'sans-serif',
            }}
          >
            {subtitle}
          </p>
        </SlideUp>
      )}
    </div>
  );
};

// ============================================================
// Badge — colored pill
// ============================================================
export const Badge: React.FC<{
  text: string;
  color?: string;
  delay?: number;
}> = ({ text, color = COLORS.primary, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame: frame - toFrames(delay),
    fps,
    config: { damping: 200 },
  });

  return (
    <div
      style={{
        display: 'inline-block',
        padding: '6px 18px',
        borderRadius: 8,
        backgroundColor: `${color}22`,
        border: `1px solid ${color}`,
        color: color,
        fontSize: 18,
        fontWeight: 600,
        fontFamily: 'sans-serif',
        transform: `scale(${scale})`,
      }}
    >
      {text}
    </div>
  );
};

// ============================================================
// ProgressBar — animated progress
// ============================================================
export const ProgressBar: React.FC<{
  value: number;
  max: number;
  color?: string;
  delay?: number;
  width?: number;
}> = ({ value, max, color = COLORS.primary, delay = 0, width = 400 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - toFrames(delay),
    fps,
    config: { damping: 200 },
  });

  const pct = (value / max) * 100 * progress;

  return (
    <div
      style={{
        width,
        height: 12,
        borderRadius: 6,
        backgroundColor: COLORS.border,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          width: `${pct}%`,
          height: '100%',
          borderRadius: 6,
          backgroundColor: color,
        }}
      />
    </div>
  );
};

// ============================================================
// AnimatedNumber — count up
// ============================================================
export const AnimatedNumber: React.FC<{
  value: number;
  delay?: number;
  suffix?: string;
  prefix?: string;
  fontSize?: number;
  color?: string;
}> = ({ value, delay = 0, suffix = '', prefix = '', fontSize = 64, color = COLORS.text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = interpolate(
    frame - toFrames(delay),
    [0, toFrames(1.5)],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const displayValue = Math.round(value * progress);

  return (
    <span
      style={{
        fontSize,
        fontWeight: 700,
        color,
        fontFamily: 'sans-serif',
      }}
    >
      {prefix}
      {displayValue.toLocaleString('id-ID')}
      {suffix}
    </span>
  );
};
