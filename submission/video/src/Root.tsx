import React from 'react';
import { Composition } from 'remotion';
import { TenderBuddyDemo } from './TenderBuddyDemo';
import { FPS, WIDTH, HEIGHT, TOTAL_DURATION } from './data';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="TenderBuddyDemo"
      component={TenderBuddyDemo}
      durationInFrames={TOTAL_DURATION}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
