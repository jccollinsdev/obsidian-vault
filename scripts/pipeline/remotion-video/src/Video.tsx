import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
  Easing,
} from "remotion";

// ─── TYPES ────────────────────────────────────────────────────────────────────

interface Slide {
  imagePath: string;
  title: string;
}

// ─── CENTERED IMAGE ────────────────────────────────────────────────────────────

const CenteredSlide: React.FC<{
  slide: Slide;
  from: number;
  fps: number;
}> = ({ slide, from, fps }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - from;
  const duration = 3 * fps; // 3 seconds per slide

  // Fade in over 15 frames, hold, fade out over 15 frames
  const fadeIn = 15;
  const fadeOut = 15;
  const hold = duration - fadeIn - fadeOut;

  const opacity = interpolate(
    localFrame,
    [0, fadeIn, fadeIn + hold, duration],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) }
  );

  // Subtle scale up from 0.95 to 1.0 as it fades in
  const scale = interpolate(localFrame, [0, fadeIn], [0.95, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  if (localFrame < 0 || localFrame >= duration) return null;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#000",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      {/* Title */}
      <div
        style={{
          color: "white",
          fontSize: 48,
          fontWeight: 900,
          fontFamily: "sans-serif",
          textTransform: "uppercase",
          letterSpacing: 2,
          textShadow: "2px 4px 8px rgba(0,0,0,0.9)",
          marginBottom: 32,
          textAlign: "center",
          padding: "0 40px",
        }}
      >
        {slide.title}
      </div>

      {/* Centered image */}
      <img
        src={staticFile(slide.imagePath)}
        style={{
          maxWidth: "80%",
          maxHeight: "65%",
          objectFit: "contain",
          borderRadius: 8,
          boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
        }}
      />
    </div>
  );
};

// ─── MAIN COMPOSITION ─────────────────────────────────────────────────────────

interface SlideshowProps {
  slides: Slide[];
}

export const Slideshow: React.FC<SlideshowProps> = ({ slides }) => {
  const { fps } = useVideoConfig();
  const gapFrames = fps; // 1 second gap

  let currentFrame = 0;
  const sequences: React.ReactNode[] = [];

  for (let i = 0; i < slides.length; i++) {
    const from = currentFrame;
    const duration = 3 * fps; // 3 seconds per slide
    currentFrame += duration + gapFrames;

    sequences.push(
      <Sequence key={`slide-${i}`} from={from}>
        <CenteredSlide slide={slides[i]} from={0} fps={fps} />
      </Sequence>
    );
  }

  return <AbsoluteFill style={{ backgroundColor: "#000" }}>{sequences}</AbsoluteFill>;
};
