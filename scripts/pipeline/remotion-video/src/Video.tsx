import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
  Easing,
} from "remotion";
import { Video } from "@remotion/media";

// ─── TYPES ────────────────────────────────────────────────────────────────────

type VisualType = "photo" | "article" | "chart";

interface Section {
  name: string;
  startTime: number;
  endTime: number;
}

interface Visual {
  timestamp: number;
  filePath: string;
  type: VisualType;
  duration?: number;
}

interface ZoomMoment {
  start: number;
  end: number;
  peakZoom?: number;
}

interface VideoCompositionProps {
  videoFile: string;
  sections: Section[];
  visuals: Visual[];
  zoomMoments?: ZoomMoment[];
  outputWidth?: number;
  outputHeight?: number;
}

// ─── SECTION LABEL ─────────────────────────────────────────────────────────────

const SectionLabel: React.FC<{
  text: string;
  position: "left" | "right";
  startFrame: number;
  endFrame: number;
  fps: number;
}> = ({ text, position, startFrame, endFrame, fps }) => {
  const frame = useCurrentFrame();
  const inDuration = 10; // frames for fade in
  const outDuration = 10; // frames for fade out

  const isVisible = frame >= startFrame && frame <= endFrame;

  const opacity = interpolate(frame, [startFrame, startFrame + inDuration, endFrame - outDuration, endFrame], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  const xPos = position === "right" ? "72%" : "2%";

  return (
    <div
      style={{
        position: "absolute",
        top: 20,
        left: xPos,
        opacity,
        backgroundColor: "rgba(0,0,0,0.6)",
        padding: "8px 16px",
        borderRadius: 6,
        border: "3px solid white",
        transform: "translateY(-10px)",
      }}
    >
      <span
        style={{
          color: "white",
          fontSize: 28,
          fontWeight: 900,
          fontFamily: "sans-serif",
          textTransform: "uppercase",
          letterSpacing: 1,
          textShadow: "2px 2px 4px rgba(0,0,0,0.9)",
        }}
      >
        {text}
      </span>
    </div>
  );
};

// ─── CORNER OVERLAY ────────────────────────────────────────────────────────────

const CornerOverlay: React.FC<{
  imagePath: string;
  timestamp: number;
  duration: number;
  fps: number;
  corner: "bottom-right" | "bottom-left";
  slideIn?: boolean;
  slideDirection?: "left" | "right";
}> = ({ imagePath, timestamp, duration, fps, corner, slideIn, slideDirection }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - timestamp * fps;

  const appearDuration = slideIn ? 12 : 8; // frames
  const durFrames = Math.max(10, (duration ?? 3) * fps);
  const fadeOutDuration = Math.max(5, Math.floor(durFrames * 0.1));
  // fadeOutStart: start fading out well before the end, after fade-in finishes
  const fadeOutStart = durFrames - fadeOutDuration;

  const opacity = interpolate(
    localFrame,
    [0, appearDuration, fadeOutStart, durFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Scale: zoom in from 0.8 to 1.0 as it appears
  const scale = interpolate(localFrame, [0, appearDuration], [0.8, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.5)),
  });

  // Slide in from side
  let xOffset = 0;
  if (slideIn && slideDirection === "right") {
    xOffset = interpolate(localFrame, [0, appearDuration], [-400, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.quad),
    });
  } else if (slideIn && slideDirection === "left") {
    xOffset = interpolate(localFrame, [0, appearDuration], [400, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.quad),
    });
  }

  const isVisible = localFrame >= 0 && localFrame <= durFrames;
  if (!isVisible) return null;

  const x = corner === "bottom-right" ? 748 + xOffset : 20 + xOffset;
  const y = 412;

  return (
    <div
      style={{
        position: "absolute",
        bottom: y,
        left: x,
        width: 512,
        opacity,
        transform: `scale(${scale})`,
        transformOrigin: corner === "bottom-right" ? "bottom right" : "bottom left",
        borderRadius: 8,
        overflow: "hidden",
        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
      }}
    >
      <img
        src={staticFile(imagePath)}
        style={{
          width: "100%",
          height: "auto",
          display: "block",
          objectFit: "cover",
        }}
      />
    </div>
  );
};

// ─── FULL SCREEN OVERLAY ───────────────────────────────────────────────────────

const FullScreenOverlay: React.FC<{
  imagePath: string;
  timestamp: number;
  duration: number;
  fps: number;
}> = ({ imagePath, timestamp, duration, fps }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - timestamp * fps;
  const dur = duration ?? 3;

  const fadeIn = 8;
  const fadeOut = 12;
  const totalFrames = Math.max(20, dur * fps);

  const opacity = interpolate(
    localFrame,
    [0, fadeIn, totalFrames - fadeOut, totalFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const isVisible = localFrame >= 0 && localFrame <= totalFrames;
  if (!isVisible) return null;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        opacity,
      }}
    >
      <img
        src={staticFile(imagePath)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          backgroundColor: "black",
        }}
      />
    </div>
  );
};

// ─── FACE ZOOM ────────────────────────────────────────────────────────────────

const FaceZoom: React.FC<{
  videoSrc: string;
  zoomMoments: ZoomMoment[];
  fps: number;
}> = ({ videoSrc, zoomMoments, fps }) => {
  const frame = useCurrentFrame();

  let currentZoom = 1;

  for (const zm of zoomMoments) {
    const startF = zm.start * fps;
    const endF = zm.end * fps;
    const peakZoom = zm.peakZoom ?? 1.15;
    const rampFrames = 12; // 0.5s ramp in/out

    if (frame >= startF && frame <= endF) {
      const progress = (frame - startF) / (endF - startF);
      const inRamp = 0.5; // first 50% of window is zoom in
      const outRamp = 0.5; // last 50% is zoom out

      if (progress < inRamp) {
        currentZoom = interpolate(progress / inRamp, [0, 1], [1, peakZoom], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.quad),
        });
      } else if (progress > outRamp) {
        const outProgress = (progress - outRamp) / (1 - outRamp);
        currentZoom = interpolate(outProgress, [0, 1], [peakZoom, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.in(Easing.quad),
        });
      } else {
        currentZoom = peakZoom;
      }
      break;
    }
  }

  const w = 1280;
  const h = 720;
  const newW = Math.round(w * currentZoom);
  const newH = Math.round(h * currentZoom);
  const cropLeft = (newW - w) / 2;
  const cropTop = (newH - h) / 2;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: w,
        height: h,
        overflow: "hidden",
        transform: `scale(${currentZoom})`,
        transformOrigin: "center center",
      }}
    >
      <Video
        src={staticFile(videoSrc)}
        style={{ width: newW, height: newH, marginLeft: -cropLeft, marginTop: -cropTop }}
      />
    </div>
  );
};

// ─── MAIN VIDEO COMPOSITION ────────────────────────────────────────────────────

export const VideoComposition: React.FC<VideoCompositionProps> = ({
  videoFile,
  sections,
  visuals,
  zoomMoments = [],
}) => {
  const { fps } = useVideoConfig();

  // Sort sections by start time
  const sortedSections = [...sections].sort((a, b) => a.startTime - b.startTime);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Base video with optional zoom */}
      {zoomMoments.length > 0 ? (
        <FaceZoom videoSrc={videoFile} zoomMoments={zoomMoments} fps={fps} />
      ) : (
        <Video
          src={staticFile(videoFile)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      )}

      {/* Section Labels */}
      {sortedSections.map((sec, idx) => (
        <Sequence key={`label-${idx}`} from={Math.round(sec.startTime * fps)}>
          <SectionLabel
            text={sec.name}
            position={idx % 2 === 0 ? "right" : "left"}
            startFrame={0}
            endFrame={Math.round((sec.endTime - sec.startTime) * fps)}
            fps={fps}
          />
        </Sequence>
      ))}

      {/* Visuals */}
      {visuals.map((v, idx) => {
        const localFrom = Math.round(v.timestamp * fps);
        const dur = v.duration ?? 3;

        return (
          <Sequence key={`visual-${idx}`} from={localFrom}>
            {v.type === "article" ? (
              <FullScreenOverlay
                imagePath={v.filePath}
                timestamp={0}
                duration={dur}
                fps={fps}
              />
            ) : (
              <CornerOverlay
                imagePath={v.filePath}
                timestamp={0}
                duration={dur}
                fps={fps}
                corner="bottom-right"
                slideIn={idx > 0 && v.timestamp - (visuals[idx - 1]?.timestamp ?? 0) < 0.5}
                slideDirection="right"
              />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
