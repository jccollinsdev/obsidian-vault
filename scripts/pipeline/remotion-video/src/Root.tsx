import { Composition } from "remotion";
import { Slideshow } from "./Video";

const SLIDES = [
  { imagePath: "photo_IRAN/image_002.jpg", title: "Iran Ceasefire Rally" },
  { imagePath: "photo_OIL/image_002.jpg", title: "Oil Shock Reversal" },
  { imagePath: "photo_SPACEX/image_002.jpg", title: "SpaceX IPO Filing" },
  { imagePath: "photo_LILLY/image_003.png", title: "Eli Lilly GLP-1 Pill Approved" },
];

// Each slide: 3s display + 1s gap. Last slide ends without gap.
const SLIDE_DURATION = 3; // seconds
const GAP = 1; // seconds
const TOTAL_FRAMES = SLIDES.length * SLIDE_DURATION * 25 + (SLIDES.length - 1) * GAP * 25;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SansarSlideshow"
        component={Slideshow}
        durationInFrames={TOTAL_FRAMES}
        fps={25}
        width={1280}
        height={720}
        defaultProps={{ slides: SLIDES }}
      />
    </>
  );
};
