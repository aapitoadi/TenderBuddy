import React from 'react';
import { Sequence, Audio, staticFile } from 'remotion';
import {
  FPS,
  TOTAL_DURATION,
  SCENES,
  AUDIO_CLIPS,
  toFrames,
} from './data';
import { ProblemScene } from './scenes/ProblemScene';
import { SolutionScene } from './scenes/SolutionScene';
import { ArchitectureScene } from './scenes/ArchitectureScene';
import { WorkflowScene } from './scenes/WorkflowScene';
import { TestingScene } from './scenes/TestingScene';
import { ReflectionScene } from './scenes/ReflectionScene';
import { ClosingScene } from './scenes/ClosingScene';

// ============================================================
// AudioLayer — plays all narration MP3s sequentially
// Each clip is placed in a Sequence at the correct offset
// ============================================================
const AudioLayer: React.FC = () => {
  let globalOffset = 0; // tracks cumulative audio start across all scenes

  const allClips: { file: string; startFrame: number; durationFrames: number }[] = [];

  (Object.keys(AUDIO_CLIPS) as string[]).forEach((sceneKey) => {
    const clips = AUDIO_CLIPS[sceneKey];
    const sceneStart = SCENES[sceneKey as keyof typeof SCENES]?.start ?? 0;

    let sceneOffset = 0;
    clips.forEach((clip) => {
      allClips.push({
        file: clip.file,
        startFrame: toFrames(sceneStart + sceneOffset),
        durationFrames: toFrames(clip.duration) + 5, // +5 frames buffer
      });
      sceneOffset += clip.duration;
    });
  });

  return (
    <>
      {allClips.map((clip, i) => (
        <Sequence
          key={`audio-${i}`}
          from={clip.startFrame}
          durationInFrames={clip.durationFrames}
        >
          <Audio src={staticFile(clip.file)} />
        </Sequence>
      ))}
    </>
  );
};

// ============================================================
// Main composition: sequences all 7 scenes + audio layer
// ============================================================
export const TenderBuddyDemo: React.FC = () => {
  const scenes = [
    { key: 'problem',      component: <ProblemScene />,      ...SCENES.problem },
    { key: 'solution',     component: <SolutionScene />,     ...SCENES.solution },
    { key: 'architecture', component: <ArchitectureScene />, ...SCENES.architecture },
    { key: 'workflow',     component: <WorkflowScene />,     ...SCENES.workflow },
    { key: 'testing',      component: <TestingScene />,      ...SCENES.testing },
    { key: 'reflection',   component: <ReflectionScene />,   ...SCENES.reflection },
    { key: 'closing',      component: <ClosingScene />,      ...SCENES.closing },
  ];

  return (
    <>
      {/* Visual scenes */}
      {scenes.map((scene) => {
        const fromFrame = toFrames(scene.start);
        const durationFrames = toFrames(scene.end - scene.start);

        return (
          <Sequence
            key={scene.key}
            from={fromFrame}
            durationInFrames={durationFrames}
            premountFor={FPS}
          >
            {scene.component}
          </Sequence>
        );
      })}

      {/* Audio narration layer — plays across entire video */}
      <AudioLayer />
    </>
  );
};
