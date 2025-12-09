/** Description:
This script defines a component named `SeqRecordStatus` for displaying sequencer
recording status in the keyboard view.

The component shows:
- A thin progress bar indicating current step position within the loop
- "REC" indicator when recording is active
- Loop count showing number of recorded takes

Configuration options:
- audioPlugin: The sequencer plugin to monitor
- bgColor: Background color
- progressBarBgColor: Progress bar background color
- progressBarFgColor: Progress bar foreground color
- recColor: Color for the REC indicator
- textColor: Color for text elements

sha: auto-generated
*/
import { getJsonComponent } from '../ui';

export const SeqRecordStatus = getJsonComponent<{
    audioPlugin: string;
    bgColor?: string;
    progressBarBgColor?: string;
    progressBarFgColor?: string;
    recColor?: string;
    textColor?: string;
}>('SeqRecordStatus');
