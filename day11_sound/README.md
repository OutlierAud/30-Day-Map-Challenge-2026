# 30 Day Map Challenge | Day 11

### 11 November 2026 | Senses: Sound

## 🎬 [Play Sound Map](jungle_beats_quicktime.mp4)

## Jungle Beats

### A Sound Map In Time

Jungle Beats turns a mixed drum and birdsong recording into an animated sound map. The map builds from left to right as the recording plays. Orange strokes mark estimated drum hits, and yellow traces show tonal frequencies, with higher sounds plotted higher on the screen.

## What you need

- Your recording, saved as `junglebeats.mp3`
- [`render_jungle.py`](render_jungle.py)
- `uv` and FFmpeg available in Terminal

## Make the video

Place `junglebeats.mp3` and `render_jungle.py` in `day11_sound/`.  
Then, open Terminal at the repository root and run:

```sh
uv run --with numpy --with 'Pillow>=10.1' python day11_sound/render_jungle.py day11_sound/junglebeats.mp3 -o day11_sound/jungle_beats_sound_map.mp4
```

The script analyzes the recording and saves `day11_sound/jungle_beats_sound_map.mp4` with two audio tracks. QuickTime uses the default AAC track for playback. The second track preserves the original MP3 without re-encoding it.

## How the map works

The script estimates drum hits by looking for sudden increases in low-frequency energy. It highlights tonal frequencies that stand out from nearby frequencies. 

**Observed limitations**  
Because the drums and birds are already mixed, some drum hits may be missed or misidentified, and the yellow traces can include tones from both sounds.

The layout was tuned for the original recording, which is about 19 seconds long. The animation runs for 22 seconds so the finished map can hold on screen after the audio ends.

## Earlier prototype

Inspired by [librosa’s onset detection documentation](https://librosa.org/doc/main/api/generated/librosa.onset.onset_detect.html). The Jungle Beats renderer uses NumPy for its audio analysis.

## Audio credits

I mixed Jungle Beats myself using free audio clips downloaded from [Pixabay](https://pixabay.com/).
