# CLAUDE.md — NeuroSound Frontend

## Always Do First
- **Invoke the `frontend-design` skill** before writing any frontend code, every session, no exceptions.
- Read the global `../CLAUDE.md` for brand colors, typography, API contract, and model info.
- Check `brand_assets/` for logo and reference images before writing any code.

---

## Reference Images
- **Landing page** : `brand_assets/reference_landing.png`
  - Dark tech — black bg, cyan + violet accents, immersive full-width sections
- **Dashboard** : `brand_assets/reference_dashboard.png` (NeuralFlow style)
  - 3-column layout: sidebar left + main center + model status panel right
  - Dark cards with subtle colored borders, mini sparkline charts in stat cards
  - Match layout, spacing, typography, and color exactly
  - Swap NeuroSound content in — do not copy reference copy
- Screenshot output, compare against reference, fix mismatches, re-screenshot
- Do at least 2 comparison rounds

---

## Local Server
- **Always serve on localhost** — never screenshot a `file:///` URL.
- Start: `node serve.mjs` at `http://localhost:3000`
- If already running, do not start a second instance.

---

## Screenshot Workflow
- Puppeteer path: `C:/Users/hp/AppData/Local/Temp/puppeteer-test/`
- Chrome cache: `C:/Users/hp/.cache/puppeteer/`
- **Always screenshot:** `node screenshot.mjs http://localhost:3000`
- Saved to `./temporary screenshots/screenshot-N.png`
- Read PNG with Read tool after each screenshot — analyze visually
- Be specific: "heading is 32px but reference shows ~24px"

---

## Output Defaults
- Single `index.html` file, all styles inline
- Tailwind CSS via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Google Fonts: Syne + DM Mono + Outfit via `<link>` in `<head>`
- Placeholder images: `https://placehold.co/WIDTHxHEIGHT`
- Mobile-first responsive

---

## Navigation (SPA)
- Single Page Application — zero page reloads
- All pages in one `index.html`, shown/hidden via `.hidden` class
- `navigateTo(pageId)` switches pages
- Active nav link: cyan dot indicator (like NeuralFlow reference)
- Page transitions: `opacity` + `translateY` only — never `transition-all`

```javascript
function navigateTo(pageId) {
  document.querySelectorAll('.page').forEach(p => {
    p.classList.add('hidden');
    p.style.opacity = '0';
  });
  const page = document.getElementById(pageId);
  page.classList.remove('hidden');
  requestAnimationFrame(() => {
    page.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    page.style.opacity = '1';
    page.style.transform = 'translateY(0)';
  });
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
}
```

---

## Pages & Structure

### Page 1 — Landing (`page-landing`)
**Entry point. Multiple full-width sections. CTA "Start Analyzing" → page-dashboard.**

#### Section 1 — Hero
```
Layout    : Full-width, centered, min-height 100vh
Background: #0A0E1A + radial cyan glow top-center + violet glow bottom-right
            + SVG grain texture overlay 4% opacity
            + animated floating particles

Visual    : Animated sound waveform SVG — cyan stroke, glow filter, CSS animation

Content:
  Eyebrow : "AI-Powered Acoustic Intelligence"
            DM Mono · cyan · uppercase · tracking-widest · 0.75rem
  Headline: "Decode the Sound\nAround You"
            Syne · 5rem · white · tracking -0.03em · line-height 1.1
  Body    : "Upload any audio file or spectrogram and let our deep learning
             models identify what's making that sound — in milliseconds."
            Outfit · 1.125rem · #6B7280 · max-width 560px
  CTA     : "Start Analyzing →"
            Syne bold · bg-[#00D4FF] · text-[#0A0E1A] · px-8 py-4 · rounded-xl
            hover: scale(1.03) + stronger glow shadow
            onClick: navigateTo('page-dashboard')

Scroll indicator: animated down chevron, bottom center
```

#### Section 2 — How It Works
```
Layout  : 3 columns · py-32 · centered · max-width 1200px
Heading : "How It Works" · Syne · 3rem · white
Sub     : "Two models. One interface. Zero complexity." · Outfit · muted

3 glassmorphism cards:
  Card 1 — "Drop Your File"
    Icon : Upload SVG · cyan glow
    Body : "WAV audio or PNG spectrogram — drag, drop, done."

  Card 2 — "AI Classifies"
    Icon : Waveform/brain SVG · violet glow
    Body : "EfficientNetB3 or YAMNet processes your file in milliseconds."

  Card 3 — "Get Results"
    Icon : Chart bars SVG · cyan glow
    Body : "Top 5 predictions with confidence scores, instantly."

Card style:
  bg: rgba(255,255,255,0.03)
  border: 1px solid rgba(0,212,255,0.1)
  backdrop-filter: blur(8px)
  border-radius: 1rem
  hover: border-color rgba(0,212,255,0.3) + glow
```

#### Section 3 — Two Models
```
Layout  : 2 cards side by side · py-32
Heading : "Two Models. One Goal." · Syne · 3rem

Card 1 — EfficientNetB3
  Accent : #7C3AED (violet)
  Badge  : "SPECTROGRAM" · violet pill
  Title  : "EfficientNetB3 + Attention"
  Sub    : "Visual acoustic analysis"
  Body   : "Trained on 20,000 Mel spectrogram images.
             Recognizes 50 sound categories from PNG input."
  Input  : "PNG · 300×300px"

Card 2 — YAMNet
  Accent : #00D4FF (cyan)
  Badge  : "AUDIO" · cyan pill
  Title  : "YAMNet"
  Sub    : "Direct audio classification"
  Body   : "Pre-trained on 2M clips from AudioSet by Google.
             Classifies raw WAV files — no preprocessing needed."
  Input  : "WAV · 16kHz mono"

Card style: bg-[#111827] · border with accent at 20% opacity
            hover: border 60% + glow shadow
```

#### Section 4 — CTA Final
```
Layout    : Full-width centered · py-40
Background: darker + cyan radial glow center
Heading   : "Ready to Classify?" · Syne · 3.5rem · white
Body      : "Drop a sound. Get an answer." · Outfit · muted
CTA       : "Start Analyzing →" → navigateTo('page-dashboard')
```

---

### Page 2 — Dashboard (`page-dashboard`)
**Accessed via "Start Analyzing" CTA. Inspired by NeuralFlow reference.**
**3-column layout: Sidebar + Main + Right Panel**

#### Layout Structure
```
┌──────────────────────────────────────────────────────────────────┐
│  TOPBAR — "NeuroSound Dashboard" · subtitle · actions right      │
├─────────────┬────────────────────────────────┬───────────────────┤
│             │                                │                   │
│  SIDEBAR    │   MAIN AREA                    │  MODEL STATUS     │
│  160px      │   flex-1                       │  PANEL · 260px    │
│             │                                │                   │
│  OVERVIEW   │  ┌──────────────────────────┐  │  EfficientNetB3   │
│  Dashboard  │  │  STAT CARDS (3 cards)    │  │  ████████ 93.34%  │
│  History    │  │  Total · Accuracy · Top  │  │                   │
│             │  └──────────────────────────┘  │  YAMNet           │
│  CLASSIFY   │                                │  ████████ 88.5%   │
│  Upload WAV │  ┌──────────────────────────┐  │                   │
│  Upload PNG │  │  UPLOAD ZONE             │  │  ─────────────    │
│             │  │  drag & drop             │  │                   │
│  SYSTEM     │  └──────────────────────────┘  │  RECENT EVENTS    │
│  About      │                                │  • Dog · 94%      │
│  Settings   │  ┌──────────────────────────┐  │  • Rain · 87%     │
│             │  │  PREDICTION RESULTS      │  │  • Siren · 91%    │
│             │  │  (hidden until upload)   │  │                   │
│  ─────────  │  └──────────────────────────┘  │                   │
│  User info  │                                │                   │
└─────────────┴────────────────────────────────┴───────────────────┘
```

#### Sidebar
```
Width     : 160px · fixed height 100vh · bg-[#0A0E1A]
Border    : 1px solid rgba(0,212,255,0.08) right side
Logo      : "NeuroSound" · Syne bold · white + cyan waveform icon · top

Sections with labels (DM Mono · #6B7280 · uppercase · 0.65rem · tracking-widest):

  OVERVIEW
    • Dashboard     ← active: cyan dot left + text-white
    • History       ← navigateTo('page-history')

  CLASSIFY
    • Upload WAV    ← triggers WAV upload flow
    • Upload PNG    ← triggers PNG upload flow

  SYSTEM
    • About         ← navigateTo('page-about')
    • Settings      ← navigateTo('page-settings') [placeholder]

Bottom: user avatar + name "NeuroSound User" · small text
Active link style: cyan dot (●) left + text-white + bg-[#111827] rounded
```

#### Topbar
```
Height    : 56px · bg-[#0A0E1A]/80 · backdrop-blur-md
Border    : bottom 1px solid rgba(0,212,255,0.08)
Left      : "Dashboard" · Syne · 1.25rem · white
            "Real-time • Updated just now" · DM Mono · 0.75rem · #6B7280
Right     : Time filter pills (1D · 7D · 30D · 90D) · same style as NeuralFlow
            Export button · bg-[#111827] · border cyan/20 · Outfit
```

#### Stat Cards (3 cards top of main area)
```
Card 1 — Total Analyses
  Label : "TOTAL ANALYSES" · DM Mono · muted · uppercase
  Value : dynamic count from history DB · Syne · 2rem · white
  Sub   : "↑ analyses today" · green

Card 2 — Best Accuracy
  Label : "BEST ACCURACY"
  Value : "93.34%" · Syne · 2rem · cyan
  Sub   : "EfficientNetB3 model"

Card 3 — Classes Available
  Label : "SOUND CLASSES"
  Value : "50" · Syne · 2rem · violet
  Sub   : "ESC-50 dataset"

Card style:
  bg-[#111827] · border border-[#00D4FF]/10 · rounded-xl · p-5
  Mini sparkline or icon top-right (like NeuralFlow)
  hover: border-[#00D4FF]/30
```

#### Upload Zone (main area center)
```
- Dashed border: 2px dashed rgba(0,212,255,0.4)
- Background: rgba(0,212,255,0.02)
- Icon: waveform SVG (WAV) or grid SVG (PNG) · cyan · 48px
- Title: "Drop your file here" · Syne · 1.25rem · white
- Sub  : "WAV audio or PNG spectrogram · max 10MB" · Outfit · muted
- Button: "Browse Files" · small · border cyan
- On hover: pulse glow + border opacity 100%
- After drop: show filename badge + size + model badge + "Analyze" button
- Model badge:
    WAV → cyan pill "YAMNet"
    PNG → violet pill "EfficientNetB3"
```

#### Prediction Results (hidden until analysis complete)
```
Appears below upload zone after API response.

Layout: 2 columns
  Left  : Top prediction + confidence + model used
  Right : Top 5 confidence bars

Top prediction:
  Label    : "PREDICTION" · DM Mono · muted · uppercase
  Class    : predicted label · Syne · 2.5rem · white
  Confidence badge:
    > 80%  → bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30
    50-80% → bg-[#F59E0B]/10 text-[#F59E0B]
    < 50%  → bg-[#EF4444]/10 text-[#EF4444]
  Model used: small pill bottom (YAMNet or EfficientNetB3)

Top 5 bars:
  Each row: label left · bar center · percentage right
  Bar fill: linear-gradient(90deg, #00D4FF, #7C3AED)
  Bar height: 6px · border-radius 9999px
  Staggered reveal: nth-child delays 0.1s each
  Bar width transitions: cubic-bezier(0.34, 1.56, 0.64, 1) 0.8s

Card: bg-[#111827] · border border-[#00D4FF]/10 · rounded-2xl · p-6
```

#### Right Panel — Model Status
```
Width  : 260px · bg-[#0A0E1A] · border-left rgba(0,212,255,0.08)

Section: "MODEL STATUS" · DM Mono · muted · uppercase

Model 1 — EfficientNetB3
  Status dot: green (loaded)
  Name: "EfficientNetB3" · Outfit · white · 0.875rem
  Progress ring or bar: 93.34% · violet
  Tag: "SPECTROGRAM · PROD" · DM Mono · muted · 0.65rem

Model 2 — YAMNet
  Status dot: green (loaded)
  Name: "YAMNet" · Outfit · white
  Progress ring or bar: 88.5% · cyan
  Tag: "AUDIO · PROD" · DM Mono · muted · 0.65rem

Divider

Section: "RECENT ANALYSES"
  Last 5 predictions from DB:
  Each row:
    • Colored dot (cyan WAV / violet PNG)
    • Class name · Outfit · white · 0.875rem
    • Confidence · DM Mono · muted
    • Time ago · DM Mono · muted · 0.75rem
  "View all →" link · cyan · bottom
```

#### Loading State (during API call)
```
- Upload zone: shimmer skeleton overlay
- Results area: 3 skeleton bars
- Right panel recent: pulsing placeholder rows
- Topbar subtitle: "Analyzing..." with spinning indicator
- WAV: 3 bouncing waveform bars animation
- PNG: spinning ring animation
```

---

### Page 3 — History (`page-history`)
**Full table of all past predictions from the current session.**

#### Layout
```
Same sidebar (3-column) + topbar as dashboard.
Topbar title: "Analysis History" · subtitle: "All your past classifications"
```

#### Main Area
```
Header row:
  Left : "Analysis History" · Syne · 1.5rem · white
  Right: Filter pills — All · WAV · PNG
         Active filter: bg-[#00D4FF]/10 · border-[#00D4FF]/30 · text-[#00D4FF]
         Inactive: bg-[#111827] · text-muted

Table:
  Sticky header · bg-[#0A0E1A] · border-bottom rgba(0,212,255,0.08)
  Alternating rows: bg-[#111827] / bg-[#1C2333]
  Row hover: bg-[#1C2333] transition

  Columns:
    DATE        · DM Mono · 0.8rem · muted · "Apr 29, 2026 · 14:32"
    FILE        · Outfit · white · filename truncated max 20 chars
    TYPE        · badge pill:
                    WAV → bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30
                    PNG → bg-[#7C3AED]/10 text-[#7C3AED] border-[#7C3AED]/30
    MODEL       · DM Mono · 0.75rem · muted · "YAMNet" or "EfficientNetB3"
    PREDICTION  · Outfit · white · bold · predicted class name
    CONFIDENCE  · DM Mono · colored:
                    > 80%  → #10B981 (green)
                    50-80% → #F59E0B (amber)
                    < 50%  → #EF4444 (red)
    DELETE      · trash SVG icon · #6B7280 · hover: #EF4444 · cursor pointer
                  onClick: remove row from table + update Total Analyses count

Empty state (no analyses yet):
  Centered waveform SVG illustration · cyan · 80px
  "No analyses yet" · Syne · 1.25rem · white
  "Upload a file to get started" · Outfit · muted
  "Start Analyzing →" button · cyan · onClick: navigateTo('page-dashboard')
```

---

### Page 4 — About (`page-about`)
**Model details, accuracy scores, ESC-50 classes, platform info.**
**NO GitHub links. NO source code links. NO external links of any kind.**

#### Layout
```
Same sidebar (3-column) + topbar as dashboard.
Topbar title: "About NeuroSound" · subtitle: "Models, classes, and platform info"
```

#### Section 1 — "Our Models"
```
Heading : "Our Models" · Syne · 2rem · white
Sub     : "State-of-the-art deep learning for acoustic classification"
          Outfit · muted

2 cards side by side · gap-6:

Card 1 — EfficientNetB3 + Attention
  Accent        : #7C3AED (violet)
  Top border    : 3px solid #7C3AED
  Badge         : "SPECTROGRAM" · violet pill · top-right
  Title         : "EfficientNetB3 + Attention" · Syne · 1.25rem · white
  Accuracy      : "93.34%" · Syne · 2.5rem · violet · bold
  Sub           : "Test Accuracy" · DM Mono · muted · uppercase · 0.7rem
  Divider       : 1px solid rgba(124,58,237,0.2)
  Stats grid (2×2):
    Training Images : "20,000"
    Sound Classes   : "50"
    Input Size      : "300×300px"
    Architecture    : "EfficientNetB3 + MHA"
  Training info:
    "Phase 1 — Backbone frozen · lr=8e-4"
    "Phase 2 — Fine-tuning · BN frozen · 20 layers"
  Card: bg-[#111827] · border border-[#7C3AED]/20 · rounded-2xl · p-6

Card 2 — YAMNet
  Accent        : #00D4FF (cyan)
  Top border    : 3px solid #00D4FF
  Badge         : "AUDIO" · cyan pill · top-right
  Title         : "YAMNet" · Syne · 1.25rem · white
  Accuracy      : "88.5%" · Syne · 2.5rem · cyan · bold
  Sub           : "Val Accuracy" · DM Mono · muted · uppercase · 0.7rem
  Divider       : 1px solid rgba(0,212,255,0.2)
  Stats grid (2×2):
    Training WAV    : "2,000"
    Sound Classes   : "50"
    Input Format    : "16kHz mono"
    Pretrained on   : "AudioSet 2M clips"
  Training info:
    "Residual Dense head · Label smoothing 0.1"
    "5× augmentation · Phase 1 + Phase 2"
  Card: bg-[#111827] · border border-[#00D4FF]/20 · rounded-2xl · p-6
```

#### Section 2 — "ESC-50 Sound Classes"
```
Heading : "50 Sound Classes" · Syne · 2rem · white
Sub     : "Environmental Sound Classification dataset — 50 categories across 5 groups"
          Outfit · muted

5 group rows with group label + badges:

  ANIMALS (10) · label: cyan
    dog · sheep · hen · cow · insects · frog · pig · rooster · cat · crow
    Badge style: bg-[#00D4FF]/10 · text-[#00D4FF] · border-[#00D4FF]/20

  NATURE (10) · label: teal (#2DD4BF)
    chirping_birds · rain · wind · sea_waves · crickets ·
    thunderstorm · pouring_water · toilet_flush · crackling_fire · water_drops
    Badge style: bg-[#2DD4BF]/10 · text-[#2DD4BF] · border-[#2DD4BF]/20

  HUMAN (10) · label: amber (#F59E0B)
    brushing_teeth · laughing · crying_baby · clapping · footsteps ·
    drinking_sipping · snoring · coughing · sneezing · breathing
    Badge style: bg-[#F59E0B]/10 · text-[#F59E0B] · border-[#F59E0B]/20

  INTERIOR (10) · label: violet (#7C3AED)
    vacuum_cleaner · mouse_click · washing_machine · clock_tick · glass_breaking ·
    door_wood_creaks · keyboard_typing · clock_alarm · can_opening · door_wood_knock
    Badge style: bg-[#7C3AED]/10 · text-[#7C3AED] · border-[#7C3AED]/20

  URBAN (10) · label: white/muted
    chainsaw · airplane · train · engine · siren ·
    hand_saw · helicopter · car_horn · church_bells · fireworks
    Badge style: bg-white/5 · text-[#9CA3AF] · border-white/10

Badge style general: DM Mono · 0.7rem · px-2 py-1 · rounded-md · border
```

#### Section 3 — "Platform"
```
Heading : "Platform" · Syne · 2rem · white
Sub     : "Built for engineers and researchers"

3 cards in a row · NO external links · NO GitHub:

  Card 1 — "Deep Learning"
    Icon : SVG brain/neural · cyan glow · 40px
    Title: "Deep Learning" · Syne · 1rem · white
    Body : "Two state-of-the-art models trained on ESC-50,
            achieving above human-level accuracy (81% baseline)."

  Card 2 — "Real-time Analysis"
    Icon : SVG lightning bolt · violet glow · 40px
    Title: "Real-time Analysis" · Syne · 1rem · white
    Body : "Upload any WAV or PNG spectrogram and get
            instant classification results in milliseconds."

  Card 3 — "50 Sound Classes"
    Icon : SVG waveform · cyan glow · 40px
    Title: "50 Sound Classes" · Syne · 1rem · white
    Body : "From dog barks to thunderstorms —
            comprehensive environmental sound recognition."

Card style: bg-[#111827] · border border-[#00D4FF]/10 · rounded-xl · p-6
            hover: border-[#00D4FF]/30 + glow
```

---

## API Integration

**CRITICAL: Never use mock predictions. Always call the real backend.**

### Backend URL
```javascript
const API_BASE = 'http://localhost:8000/api';
```

### WAV Upload → YAMNet
```javascript
async function predictWav(file) {
  showLoadingState('Analyzing audio...');
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/predict/wav`, {
      method: 'POST', body: formData
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const result = await res.json();
    // result = { prediction, confidence, top5: [{label, confidence}], model, filename, timestamp }
    displayPredictionResults(result);
    await refreshHistory();
  } catch (err) {
    showErrorState(err.message);
  } finally {
    hideLoadingState();
  }
}
```

### PNG Upload → EfficientNetB3
```javascript
async function predictSpectrogram(file) {
  showLoadingState('Reading spectrogram...');
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/predict/spectrogram`, {
      method: 'POST', body: formData
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const result = await res.json();
    displayPredictionResults(result);
    await refreshHistory();
  } catch (err) {
    showErrorState(err.message);
  } finally {
    hideLoadingState();
  }
}
```

### Auto-detect model by file extension
```javascript
async function handleFileUpload(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  if (ext === 'wav')       await predictWav(file);
  else if (ext === 'png')  await predictSpectrogram(file);
  else showErrorState('Only .wav and .png files accepted');
}
```

### Display results
```javascript
function displayPredictionResults(result) {
  // Top prediction
  document.getElementById('pred-class').textContent      = result.prediction;
  document.getElementById('pred-confidence').textContent = (result.confidence * 100).toFixed(1) + '%';
  document.getElementById('pred-model').textContent      = result.model;

  // Top 5 bars — staggered animation
  result.top5.forEach((item, i) => {
    const bar = document.getElementById(`bar-${i}`);
    bar.style.animationDelay = `${i * 0.1}s`;
    bar.querySelector('.label').textContent      = item.label;
    bar.querySelector('.pct').textContent        = (item.confidence * 100).toFixed(1) + '%';
    bar.querySelector('.fill').style.width       = (item.confidence * 100) + '%';
  });

  // Show results card
  document.getElementById('prediction-results').classList.remove('hidden');
}
```

### History
```javascript
async function refreshHistory() {
  const res  = await fetch(`${API_BASE}/history`);
  const data = await res.json();
  // data = { items: [...], total: N }
  renderHistoryTable(data.items);
  renderRecentAnalyses(data.items.slice(0, 5));
  updateTotalCount(data.total);
}

async function deleteHistoryItem(id) {
  await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' });
  await refreshHistory();
}
```

### Health check — model status dots
```javascript
async function checkHealth() {
  try {
    const res    = await fetch(`${API_BASE}/health`);
    const health = await res.json();
    // { status, models_loaded: { yamnet_hub, yamnet, spectrogram } }
    const allLoaded = Object.values(health.models_loaded).every(v => v);
    document.getElementById('models-status-dot').style.color   = allLoaded ? '#10B981' : '#EF4444';
    document.getElementById('models-status-text').textContent  = allLoaded ? 'MODELS READY' : 'LOADING...';
  } catch {
    document.getElementById('models-status-text').textContent = 'OFFLINE';
  }
}
// Call on page load
checkHealth();
```

### Loading state
```javascript
function showLoadingState(message) {
  document.getElementById('loading-text').textContent = message;
  document.getElementById('loading-overlay').classList.remove('hidden');
  document.getElementById('prediction-results').classList.add('hidden');
}
function hideLoadingState() {
  document.getElementById('loading-overlay').classList.add('hidden');
}
function showErrorState(message) {
  document.getElementById('error-message').textContent = message;
  document.getElementById('error-banner').classList.remove('hidden');
  setTimeout(() => document.getElementById('error-banner').classList.add('hidden'), 4000);
}
```

---

## Premium UI Enhancements
**These are required on the landing page — not optional.**

### 1. Hero — Mouse-reactive particles
```javascript
// Canvas behind hero content
// Particles drift slowly + move toward cursor on mousemove
// Waveform SVG pulses continuously
// Hero content parallax on scroll: translateY = scrollY * 0.3
```

### 2. New Section — Exceeding Human Performance
Insert BETWEEN How It Works and Two Models sections.

Heading : Exceeding Human Performance · Syne · 3rem · white
Sub     : State-of-the-art results on the ESC-50 benchmark

3 animated counters (IntersectionObserver trigger on scroll):
  93.34% · EfficientNetB3 Test Accuracy · violet
  88.5%  · YAMNet Val Accuracy · cyan
  +12pts · Above Human Baseline · green #10B981
  Each animates 0 to final value in 1.5s ease-out when visible

Comparison bars:
  Row 1: Human Baseline · 81%    · gray bar
  Row 2: NeuroSound     · 93.34% · cyan to violet gradient bar
  Bars animate width 0 to final on scroll · height 10px · rounded

### 3. Navbar — Enhanced glassmorphism on scroll
On scroll > 50px JS adds .scrolled class:
  background: rgba(10,14,26,0.95)
  border-bottom: 1px solid rgba(0,212,255,0.2)
  box-shadow: 0 4px 24px rgba(0,212,255,0.05)
  transition: 0.3s ease on all properties

### 4. Logo — Pulse blink animation
Apply to waveform icon ONLY (not the text):
  @keyframes logo-pulse:
    0%,100%: opacity 1 + drop-shadow 0 0 6px #00D4FF + 0 0 12px #00D4FF
    50%: opacity 0.6 + drop-shadow 0 0 2px #00D4FF
  animation: logo-pulse 2s ease-in-out infinite
  Apply to navbar logo AND sidebar logo

### 5. CTA Buttons — Ripple effect on click
All Start Analyzing buttons:
  On click: expanding circle from click point
  Color: rgba(0,212,255,0.3) · scale 0 to 40 · opacity 1 to 0 · 0.6s

### 6. Footer — Professional 3-column layout
Left  : NeuroSound logo + pulse icon + AI-Powered Acoustic Intelligence
Center: Nav links Landing · Dashboard · History · About (hover: white)
Right : Built with EfficientNetB3 + YAMNet / ESC-50 dataset · 50 classes
Bottom: gradient line cyan to violet + copyright centered

### 7. Scroll animations — Section reveal
All sections use IntersectionObserver:
  Initial: opacity 0 + translateY 40px
  On enter: opacity 1 + translateY 0 · transition 0.7s ease-out
  Cards stagger: 0.1s delay per nth-child

### 8. Background — Layered radial gradients
Hero background:
  radial cyan glow top-center: rgba(0,212,255,0.12)
  radial violet glow bottom-right: rgba(124,58,237,0.10)
  deep blue center: rgba(10,14,30,0.8)
  SVG grain texture overlay: opacity 0.04 via ::after pseudo-element

---

## Anti-Generic Guardrails
- **Colors:** Never default Tailwind. Always brand colors.
- **Shadows:** Never flat `shadow-md`. Color-tinted layered shadows.
- **Typography:** Always Syne + DM Mono + Outfit. No exceptions.
- **Gradients:** Layer radial gradients. SVG grain texture for depth.
- **Animations:** Only `transform` + `opacity`. Never `transition-all`.
- **States:** hover + focus-visible + active on every clickable element.
- **Depth:** bg-primary → bg-secondary → bg-elevated. Never flat.
- **Background:** Radial gradient mesh — never solid color.
- **Hero:** Always animated visual — static is not acceptable.
- **Sidebar active:** Cyan dot indicator exactly like NeuralFlow reference.
- **Stat cards:** Always have mini sparkline or icon top-right like NeuralFlow.

---

## Hard Rules
- Do not show accuracy scores on landing page — only on About page
- Do not add sections not in this spec
- Do not improve a reference — match it exactly
- Do not stop after one screenshot — always 2+ rounds
- Do not use `transition-all`
- Do not use default Tailwind blue/indigo
- Do not reload page for navigation
- Do not use Arial, Inter, Roboto, or system fonts
- Do not call API without showing loading state first
- CTA "Start Analyzing" always navigates to `page-dashboard`
- Dashboard always shows 3-column layout on desktop: sidebar + main + right panel
