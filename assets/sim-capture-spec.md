# Maddy video: Simulator capture spec (for Claude Code)

**Purpose.** Capture fresh, real, current-code app screens and flows for the video board, straight from the iOS Simulator. Do not reuse the May 2026 vault screenshots as final assets: treat them as reference only. Some are dated against HEAD (`61601ef`). Everything shipped as "the app" in a video must be captured from the current build.

**Honesty rule.** Only real app UI from the running build goes in the "app screen" slots. No mockups, no hand-built screens passed as product. If a screen or state does not exist in the current build, flag it, do not fabricate it.

---

## Setup

- **Repo:** `jerrunge/maddy` (this repo). Run the app on a booted Simulator (Expo / RN: `npx expo run:ios` or the project's run script).
- **Device:** iPhone 16 Pro Max simulator. Native capture is 1290 x 2796, which clears the App Store / video minimum. (15 Pro Max is an acceptable fallback.)
- **Themes:** capture the light hero shots in **Cotton Candy Sky** (surface `#FAFCFF`, gradient `#E0F2FE`→`#FCE7F3`) and the moody variants in **Night Owl** (surface `#0E0E14`). Both already read well. Theme is set in-app (Sensory / Theme).
- **Demo data:** use the founder's seeded test accounts. Keep the on-screen name consistent within a single video. Names already in use are fine (Jeremy / Shawna / Jill / Nana). Do not put real third-party PII on screen.
- **Capacity:** several screens depend on the "How are you showing up" pick. Real options in current code: `Moving slow`, `Just okay`, `Restless`, `Feeling good`, `I can't right now`. Pick the one named per shot below.

## Capture mechanics (harness)

Use `capture-app-screens.sh` in this folder. Core commands:

```bash
# still, native resolution
xcrun simctl io booted screenshot --type=png "out/<name>.png"

# screen recording (Ctrl-C to stop), then optionally normalize with ffmpeg
xcrun simctl io booted recordVideo --codec=h264 "out/<name>.mov"
```

Navigate the app to each target (Code drives the UI, or do it by hand), then capture. Output names below match the board's asset slots exactly, so the wiring is drop-in.

---

## Stills to capture (real screens)

| Output name | Screen (current code) | Mode | State to set | Used by |
|---|---|---|---|---|
| `app-focus-light` | user Home, "Today" / single task (`components/home`) | User | capacity = Moving slow, one task visible (e.g. "Get dressed") | U1, U3, U4, MC2 |
| `app-focus-dark` | same, Night Owl theme | User | capacity = Moving slow, one task | U1, U4 (dark cut) |
| `app-start` | user Home, the "one thing" start state, task not yet done | User | one task, fresh | C4, U2 |
| `app-capacity-sheet` | "How are you showing up" picker | User | sheet open, "I can't right now" visible in the list | U5, MC3, MC1 |
| `app-thats-okay` | rest / permission state after "I can't right now" (`RestScreen`) | User | the "That's okay" screen | U5, MC3 |
| `app-amber-nudge` | any reminder / window-closing nudge that renders in **amber** (theme `warning` is amber, never red) | User | trigger a gentle reminder/warning state | MC1 (proof: warns amber, not red) |
| `app-supporter-home` | `OuterRingHome` "Cheering for [name]" | Outer ring, supporter | recent cheers + Wins visible | S1, S2 |
| `app-supporter-compose` | `EncourageComposer` ("Send a cheer") | Outer ring, supporter | composer open, a cheer typed | S1, S2 |
| `app-peer-home` | `OuterRingHome` "Standing alongside [name]" | Outer ring, peer | presence + Wins visible | P1, P2 |
| `app-together` | the "With [name] today" / alongside presence state | User or peer | active "ready to go since…" presence | P1, P2 |
| `app-circle` | `CircleScreen` "Your circle" | User | circle grid + a couple of cheers in the feed | C1, C3, general |
| `app-rest-breathe` | `RestScreen` / breathe ("breathe in…") | User | calm breathing state | MC1, MC3, texture |
| `app-showingup` | `ShowingUpScreen` "Showing up" tracker | User | the weeks grid populated | U5, texture |
| `app-care` | `CareScreen` "Care" tab | User | Care content tiles | texture, caregiver |

## Recordings to capture (real flows, the part static screenshots can't show)

| Output name | Flow | Mode | Notes | Used by |
|---|---|---|---|---|
| `flow-capacity-to-okay` | open capacity picker → tap "I can't right now" → land on "That's okay" | User | the no-failure-state, in motion, the emotional core of MC3/U5 | MC3, U5 |
| `flow-complete-task` | mark the single task done → the gentle reward / no-red celebration | User | proves the payoff is calm, amber/green, never punishing | U1, U2, U3, U4 |
| `flow-send-cheer` | supporter taps "Send a cheer" → cheer sends → confirmation | Outer ring, supporter | the cheer-not-surveillance moment | S1, S2 |
| `flow-narrow-to-one` | (only if the build animates it) multi-item view collapsing to the single focus | User | if it doesn't animate natively, skip; the concept b-roll `mc2_one_thing` covers it | MC2 |

After capture, leave files in `out/`. They get reviewed, then the keepers go to the vault asset bank and the board's asset slots are pointed at them. Recordings can be handed to Descript as-is (full res); no re-export needed.

---

## What is already generated (no Sim needed)

The non-app hook graphics and Maddy's word-cards are already rendered, brand-correct, in `assets/broll-generated/` (9:16, 1080x2920 mp4 + poster):
`mc1_no_red`, `mc2_one_thing`, `mc3_cant_now`, `c3_reminder_wall`, `c4_lazy_strike`, `u1_todo_crack`, `u2_vibes_snap`, `u4_badge_pulse`, `u5_word_swap`, `u3_step_stack`. Plus the existing live-action b-roll bank (`broll-circle/checkin/day-low/day-strong/rest/showingup`).

So the only thing that needs the Simulator is the **real app UI** in the two tables above. Everything else is in hand.
