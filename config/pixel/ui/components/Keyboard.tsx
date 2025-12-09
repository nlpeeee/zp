import * as React from '@/libs/react';

import { KnobAction } from '@/libs/nativeComponents/KnobAction';
import { KnobValue } from '@/libs/nativeComponents/KnobValue';
import { NoteGrid } from '@/libs/nativeComponents/NoteGrid';
import { SeqRecordStatus } from '@/libs/nativeComponents/SeqRecordStatus';
import { Text } from '@/libs/nativeComponents/Text';
import { A1, A2, A3, A4, B1, B2, B3, B4, C1, C2, C3, C4, ScreenWidth, ScreenHeight, W2_4, W1_4, W3_4 } from '../constants';
import { enc1, enc2, enc3, enc4 } from '../constantsValue';
import { Layout } from './Layout';
import { rgb } from '@/libs/ui';

export type Props = {
    name: string;
    track: number;
    synthName: string;
    color: string;
    title: string;
};

export function Keyboard({ name, track, synthName, color, title }: Props) {
    const gridBounds = [...enc1.bounds];
    gridBounds[2] = W2_4 - 2;
    let keyIndex = 0;
    const menuTextColor = rgb(75, 75, 75);
    return (
        <Layout
            viewName={name}
            color={color}
            synthName={synthName}
            title={title}
            content={
                <>
                    <NoteGrid
                        audioPlugin="Sequencer"
                        track={track}
                        bounds={gridBounds}
                        encScale={enc1.encoderId}
                        encOctave={enc2.encoderId}
                        keys={[
                            { key: A1, action: `.key:${keyIndex++}` },
                            { key: A2, action: `.key:${keyIndex++}` },
                            { key: A3, action: `.key:${keyIndex++}` },
                            { key: A4, action: `.key:${keyIndex++}` },

                            { key: B1, action: `.key:${keyIndex++}` },
                            { key: B2, action: `.key:${keyIndex++}` },
                            { key: B3, action: `.key:${keyIndex++}` },
                            { key: B4, action: `.key:${keyIndex++}` },

                            { key: C1, action: `.key:${keyIndex++}` },
                            { key: C2, action: `.key:${keyIndex++}` },
                        ]}
                    />

                    <KnobValue
                        audioPlugin="Sequencer"
                        param="RECORD_ARM"
                        {...enc3}
                        color="primary"
                        track={track}
                    />

                    {/* Recording status bar at top */}
                    <SeqRecordStatus
                        audioPlugin="Sequencer"
                        track={track}
                        bounds={[120, 4, 190, 12]}
                    />

                    <Text
                        fontSize={12}
                        text="Loop"
                        bounds={[enc4.bounds[0], 15, 80, 16]}
                        font="PoppinsLight_12"
                        color={'#8f8f8fff'}
                    />

                    <KnobValue
                        audioPlugin="Sequencer"
                        param="PLAYING_LOOPS"
                        {...enc4}
                        color="primary"
                        track={track}
                    />

                    {/* Bottom row labels */}
                    <Text
                        text="Save"
                        bounds={[W2_4 - 20, ScreenHeight - 20, W1_4, 16]}
                        centered={true}
                        color={menuTextColor}
                    />
                    <Text
                        text="Exit"
                        bounds={[W3_4 - 30, ScreenHeight - 20, W1_4, 16]}
                        centered={true}
                        color={menuTextColor}
                    />

                    {/* C3: Save recording, C4: Exit */}
                    <KnobAction
                        keys={[
                            {
                                key: C3,
                                action: `data:Sequencer:${track}:SAVE_RECORD`,
                            },
                            {
                                key: C4,
                                action: `setView:&previous`,
                            },
                        ]}
                    />
                </>
            }
        />
    );
}
