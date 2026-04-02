import { Composition } from "remotion";
import { VideoComposition } from "./Video";

// Data from pipeline state
const VIDEO_FILE = "test_dummy_20260402.mp4";

const SECTIONS = [
  { name: "IRAN CEASEFIRE RALLY", startTime: 0, endTime: 1.25 },
  { name: "OIL SHOCK REVERSAL", startTime: 1.25, endTime: 2.75 },
  { name: "SPACEX IPO FILING", startTime: 2.75, endTime: 3.75 },
  { name: "ELI LILLY GLP-1 PILL APPROVED", startTime: 3.75, endTime: 5.0 },
];

// Use approved photos (these would come from Component 5/6 in production)
const VISUALS = [
  { timestamp: 0.5, filePath: "photo_0s/image_001.jpg", type: "photo" as const, duration: 3 },
  { timestamp: 1.5, filePath: "photo_4s/image_001.jpg", type: "photo" as const, duration: 3 },
  { timestamp: 3.0, filePath: "photo_0s/image_001.jpg", type: "photo" as const, duration: 3 },
];

// Zoom moments (face zoom at peak emphasis)
const ZOOM_MOMENTS = [
  { start: 2.0, end: 3.5, peakZoom: 1.15 },
];

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SansarVideo"
        component={VideoComposition}
        durationInFrames={125} // 5 seconds at 25fps
        fps={25}
        width={1280}
        height={720}
        defaultProps={{
          videoFile: VIDEO_FILE,
          sections: SECTIONS,
          visuals: VISUALS,
          zoomMoments: ZOOM_MOMENTS,
        }}
      />
    </>
  );
};
