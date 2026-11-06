import { Config } from '@remotion/cli/config';

// ============================================================
// Encoding quality settings
// ============================================================
// Problem: Remotion's default H.264 output uses ~188 kbps at 1080p.
// That is far too low for text-heavy screen content — the encoder
// blurs glyph edges to hide compression artifacts.
//
// Fix: drive the encoder with CRF (Constant Rate Factor) instead of a
// fixed bitrate, so flat background areas compress well while text
// edges stay crisp.

// CRF 16 = near-visually-lossless. Range 0-51 for h264, lower is better.
// 16 keeps text razor sharp; 18 is also acceptable for 1080p.
Config.setCrf(16);

// Keep frames as PNG while rendering: JPEG artifacts around text edges
// get baked into the source and can never be recovered later.
Config.setVideoImageFormat('png');

// JPEG quality still applies to any JPEG-based intermediate steps.
Config.setJpegQuality(100);

// True 4:2:0 chroma. Avoids the full-range (yuvj) quirk that can
// shift brightness on some players.
Config.setPixelFormat('yuv420p');

// Mark the video as BT.709 — the correct color space for HD.
Config.setColorSpace('bt709');

// h264 with yuv420p plays everywhere (browsers, phones, judges' laptops).
Config.setCodec('h264');

// Overwrite output without prompting.
Config.setOverwriteOutput(true);
