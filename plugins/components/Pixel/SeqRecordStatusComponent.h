/** Description:
This file defines a UI component called SeqRecordStatusComponent that displays real-time
recording status information for the sequencer in the Keyboard view.

It shows:
1. A thin horizontal progress bar indicating the current step position within the loop
2. "REC" indicator when recording is active (sequencer playing + recording enabled)
3. Loop count showing how many takes have been recorded

The component connects to the Sequencer plugin to get live data about step position,
playback state, and recording state.

sha: auto-generated
*/
#ifndef _UI_PIXEL_COMPONENT_SEQ_RECORD_STATUS_H_
#define _UI_PIXEL_COMPONENT_SEQ_RECORD_STATUS_H_

#include "plugins/audio/stepInterface.h"
#include "plugins/components/component.h"
#include "plugins/components/utils/color.h"

/*md
## SeqRecordStatusComponent

Displays recording status for keyboard view:
- Progress bar showing current step position
- REC indicator when recording
- Loop/take count

*/

class SeqRecordStatusComponent : public Component {
protected:
    uint16_t stepCount = 32;
    int16_t lastStepCounter = -1;
    uint16_t* stepCounterPtr = nullptr;
    bool* isPlayingPtr = nullptr;
    bool* recordingEnabledPtr = nullptr;
    size_t* recordedLoopsCountPtr = nullptr;
    size_t lastRecordedLoopsCount = 0;
    ValueInterface* recordArmVal = nullptr;
    float lastRecordArmValue = -1.0f;

    Color background;
    Color progressBarBg;
    Color progressBarFg;
    Color recColor;
    Color armColor;
    Color textColor;
    void* font = nullptr;

public:
    SeqRecordStatusComponent(ComponentInterface::Props props)
        : Component(props)
        , background(styles.colors.background)
        , progressBarBg(darken(styles.colors.primary, 0.7))
        , progressBarFg(styles.colors.primary)
        , recColor({ 0xFF, 0x40, 0x40 }) // Red for REC indicator
        , armColor({ 0xFF, 0xA0, 0x00 }) // Orange for ARM indicator
        , textColor(alpha(styles.colors.text, 0.6))
    {
        font = draw.getFont("PoppinsLight_8");

        jobRendering = [this](unsigned long now) {
            bool needRender = false;
            
            // Check if step counter changed (while playing)
            if (isPlayingPtr && *isPlayingPtr && stepCounterPtr && lastStepCounter != *stepCounterPtr) {
                lastStepCounter = *stepCounterPtr;
                needRender = true;
            }
            
            // Check if not playing anymore
            if (isPlayingPtr && !*isPlayingPtr && lastStepCounter != -1) {
                lastStepCounter = -1;
                needRender = true;
            }
            
            // Check if recorded loops count changed
            if (recordedLoopsCountPtr && *recordedLoopsCountPtr != lastRecordedLoopsCount) {
                lastRecordedLoopsCount = *recordedLoopsCountPtr;
                needRender = true;
            }
            
            // Check if record arm state changed
            if (recordArmVal && recordArmVal->get() != lastRecordArmValue) {
                lastRecordArmValue = recordArmVal->get();
                needRender = true;
            }
            
            if (needRender) {
                renderNext();
            }
        };

        /*md md_config:SeqRecordStatus */
        nlohmann::json& config = props.config;

        /// The audio plugin sequencer.
        AudioPlugin* seqPlugin = getPluginPtr(config, "audioPlugin", track); //eg: "Sequencer"
        stepCount = *(uint16_t*)seqPlugin->data(seqPlugin->getDataId("STEP_COUNT"));
        stepCounterPtr = (uint16_t*)seqPlugin->data(seqPlugin->getDataId("STEP_COUNTER"));
        isPlayingPtr = (bool*)seqPlugin->data(seqPlugin->getDataId("IS_PLAYING"));
        recordingEnabledPtr = (bool*)seqPlugin->data(seqPlugin->getDataId("RECORDING_ENABLED"));
        recordedLoopsCountPtr = (size_t*)seqPlugin->data(seqPlugin->getDataId("RECORDED_LOOPS_COUNT"));
        recordArmVal = watch(seqPlugin->getValue("RECORD_ARM"));
        logDebug("SeqRecordStatus: recordArmVal=%p", recordArmVal);

        /// The background color.
        background = draw.getColor(config["bgColor"], background);

        /// The progress bar background color.
        progressBarBg = draw.getColor(config["progressBarBgColor"], progressBarBg);

        /// The progress bar foreground color.
        progressBarFg = draw.getColor(config["progressBarFgColor"], progressBarFg);

        /// The REC indicator color.
        recColor = draw.getColor(config["recColor"], recColor);

        /// The text color.
        textColor = draw.getColor(config["textColor"], textColor);

        /*md md_config_end */
    }

    void render() override
    {
        draw.filledRect(relativePosition, size, { background });

        bool isPlaying = isPlayingPtr && *isPlayingPtr;
        bool isRecording = isPlaying && recordingEnabledPtr && *recordingEnabledPtr;

        int x = relativePosition.x;
        int y = relativePosition.y;
        int barHeight = 3; // Thin progress bar

        // Calculate progress bar width
        int progressBarWidth = size.w - 80; // Leave space for REC and Loop count
        
        // Draw progress bar background
        draw.filledRect({ x, y + (size.h - barHeight) / 2 }, { progressBarWidth, barHeight }, { progressBarBg });

        // Draw progress bar foreground (current position)
        if (isPlaying && stepCounterPtr && stepCount > 0) {
            int progressW = (progressBarWidth * (*stepCounterPtr + 1)) / stepCount;
            draw.filledRect({ x, y + (size.h - barHeight) / 2 }, { progressW, barHeight }, { progressBarFg });
        }

        // Draw REC/ARM indicator
        int textY = y + (size.h - 8) / 2;
        bool isArmed = recordArmVal && recordArmVal->get() > 0;
        
        // Debug: always show something to verify rendering
        if (recordArmVal) {
            logDebug("SeqRecordStatus render: isArmed=%d armValue=%.1f isPlaying=%d", isArmed, recordArmVal->get(), isPlaying);
        }
        
        if (isPlaying && isArmed) {
            // Recording active - show REC in red
            draw.text({ x + progressBarWidth + 4, textY }, "REC", 8, { recColor, .font = font });
        } else if (isArmed) {
            // Armed but not playing - show ARM in orange
            draw.text({ x + progressBarWidth + 4, textY }, "ARM", 8, { armColor, .font = font });
        }

        // Draw loop count
        size_t loopCount = recordedLoopsCountPtr ? *recordedLoopsCountPtr : 0;
        if (loopCount > 0) {
            std::string loopText = "L" + std::to_string(loopCount);
            draw.textRight({ x + size.w - 2, textY }, loopText, 8, { textColor, .font = font });
        }
    }
};

#endif
