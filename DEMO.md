# Demo video — how to record and embed

A 2-minute, no-narration screencast is the single highest-ROI portfolio
asset for freelance work. More effective than a static screenshot, less
effort than a hosted live demo, no API cost.

Target length: **90–120 seconds**. Longer loses the viewer; shorter
doesn't show enough.

---

## Equipment

- **Recording**: [OBS Studio](https://obsproject.com/) (free, Windows/Mac/Linux)
- **Editing**: [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) free, or just use OBS raw
- **No audio needed** — captions are better; silent GIFs work too

---

## OBS one-time setup (10 min)

1. Install OBS Studio
2. **Settings → Output**:
   - Recording Format: `MP4`
   - Encoder: `x264` (software, universally compatible)
   - Rate Control: `CRF` 23
3. **Settings → Video**:
   - Base (canvas) resolution: `1920×1080`
   - Output (scaled) resolution: `1920×1080`
   - FPS: `30`
4. **Settings → Hotkeys**:
   - Start Recording: `F9`
   - Stop Recording: `F10`
5. In the main window:
   - Scenes → `+` → "askdocs demo"
   - Sources → `+` → **Display Capture** (your main monitor)

---

## Pre-recording checklist

- [ ] Close Slack, Teams, email — no popups mid-recording
- [ ] Browser: 1 window, 1 tab, no bookmarks bar visible
- [ ] Terminal: clean background (black), font size 16+
- [ ] Prepare 2 test PDFs in a known folder (name them clearly)
- [ ] Have 2 prepared questions written down
- [ ] Mouse cursor speed: medium (your usual is probably too fast for video)
- [ ] Do a 30-second trial recording to check framing + lag

---

## The script (storyboard)

Target: **~110 seconds total**. Each scene is a timed segment.

### Scene 1 — 0:00–0:10 | Hero shot

- Open http://localhost:3000 → the chat screen
- Title appears: `askdocs — ask your documents`
- Pause 2 seconds on the empty state
- **No text overlay** — the UI speaks for itself

### Scene 2 — 0:10–0:25 | Upload

- Navigate to `/admin`
- Drop a PDF (pick something recognizable — a research paper or
  product manual)
- Wait for the "chunks: N" response
- Repeat with a second PDF
- Pause briefly on the document list showing both files + chunk counts

### Scene 3 — 0:25–0:50 | First question (easy, in-corpus)

- Back to `/`
- Type a question that the uploaded doc definitely answers
  - Example: _"What is the main contribution of this paper?"_
- Streaming response plays — this is the money shot
- Highlight the inline `[chunk_id]` citations in the output
- Pause 2 seconds on the final answer

### Scene 4 — 0:50–1:15 | Second question (specific, cited)

- Ask something specific that needs retrieval
  - Example: _"What's the error rate on the test set?"_
- Again, show streaming + citations
- This shows retrieval quality — the model isn't making up numbers

### Scene 5 — 1:15–1:30 | Hallucination guardrail

- Ask something **completely off-topic**
  - Example: _"Who won the 2026 World Cup?"_
- The model should respond: _"I don't know based on the provided documents."_
- This is the trust shot — most RAG demos skip this

### Scene 6 — 1:30–1:50 | Admin + stats

- Navigate to `/admin`
- Show the stats panel: query count, avg latency, cost ($0 since Ollama)
- Zoom slightly on the "Est. cost: $0.0000" — the zero-cost proof

### Scene 7 — 1:50–2:00 | End card

- Static end card (make in Canva, 1920×1080, 10s hold):
  - Title: `askdocs`
  - Subtitle: `Open source · Zero API cost · Fully local`
  - URL: `github.com/jg-ai-lab/askdocs`
  - Author: `jg-ai-lab · xop123444@gmail.com`

---

## Post-recording

### Trim with OBS (no editing software needed)

OBS records a clean MP4 — if your raw take is 2:30 and you want 2:00:

1. Open the raw MP4 in VLC
2. Note the start/end you want to keep
3. Use `ffmpeg` (comes with OBS install):
   ```powershell
   ffmpeg -i raw.mp4 -ss 00:00:03 -to 00:02:00 -c copy demo.mp4
   ```

### Add captions (optional but worth it)

LinkedIn and Twitter auto-play **muted** — captions double view time.

1. [Submagic.com](https://submagic.com) — 1-click AI captions, free tier
2. Or [Kapwing](https://kapwing.com) — free with watermark

### Compress for GitHub embedding

GitHub README embeds have a **10 MB limit** per video.

```powershell
# Target: ~5 MB for a 2-min 1080p clip
ffmpeg -i demo.mp4 -vcodec libx264 -crf 28 -preset slow -movflags +faststart demo_compressed.mp4
```

If still too big, go to 720p:
```powershell
ffmpeg -i demo.mp4 -vf scale=1280:720 -vcodec libx264 -crf 26 demo_720p.mp4
```

### Make a GIF version for the README hero

Static README images don't autoplay. A short GIF does.

```powershell
# 15 seconds, 720p, optimized
ffmpeg -i demo.mp4 -ss 00:00:10 -t 15 -vf "fps=15,scale=720:-1:flags=lanczos" demo.gif
```

Expect ~5 MB. If larger, trim to 10 seconds or scale down.

---

## Embed in README

GitHub README supports MP4 upload via drag-and-drop in the web editor:

1. Edit `README.md` on github.com
2. Drag `demo.mp4` into the editor at the top
3. GitHub auto-uploads and generates a `<video>` tag
4. Commit

Or do it manually:
```markdown
## Demo

https://github.com/jg-ai-lab/askdocs/assets/<UPLOAD_ID>/demo.mp4
```

(You get the URL by dragging the file into any GitHub comment first.)

---

## Where to use the final video

- [ ] **GitHub README** of askdocs (top of the page)
- [ ] **Portfolio landing** (`index.html`) — add a `<video>` tag with the mp4
- [ ] **Upwork portfolio item** — upload directly
- [ ] **Fiverr Gig video** — the 60-sec version replaces the thumbnail
- [ ] **Kmong 상품 상세 이미지** — convert to GIF or screenshot sequence
- [ ] **LinkedIn post** — "I built an open-source RAG chatbot that runs
      100% locally" + mp4
- [ ] **Twitter/X post** — same, with the GIF version

---

## One session, all assets

Record **once**, output **five artifacts**:

1. `demo.mp4` — 2 min, 1080p, uncaptioned → GitHub README
2. `demo_captioned.mp4` — same with captions → LinkedIn/Twitter
3. `demo_60s.mp4` — trimmed → Fiverr Gig video
4. `demo.gif` — 15 sec highlight loop → README hero + Kmong detail
5. `end_card.png` — static end frame → portfolio landing thumbnail

Total session: **~2 hours** including setup, recording retakes, trim,
compress, and distribute.

That's your zero-dollar version of a Railway-hosted live demo.
