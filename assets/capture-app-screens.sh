#!/usr/bin/env bash
# Maddy app capture harness (for Claude Code on macOS).
# Captures real, current-build app screens + flows from the iOS Simulator at native resolution.
# Prereqs: Xcode + simulator, the Maddy app running on a booted sim (npx expo run:ios).
set -euo pipefail

DEVICE="${DEVICE:-iPhone 16 Pro Max}"
OUT="${OUT:-out}"
mkdir -p "$OUT"

boot() {
  xcrun simctl boot "$DEVICE" 2>/dev/null || true
  open -a Simulator || true
  echo "Booted: $DEVICE. Launch/refresh the Maddy app, then run captures."
}

# still: shot <name>   (navigate the app to the target FIRST, then call)
shot() {
  local name="$1"
  xcrun simctl io booted screenshot --type=png "$OUT/$name.png"
  echo "  still  -> $OUT/$name.png"
}

# recording: rec_start <name> ... do the flow ... rec_stop
REC_PID=""
rec_start() {
  REC_NAME="$1"
  xcrun simctl io booted recordVideo --codec=h264 "$OUT/$REC_NAME.mov" &
  REC_PID=$!
  echo "  rec    -> $OUT/$REC_NAME.mov (perform the flow, then call rec_stop)"
}
rec_stop() {
  [ -n "$REC_PID" ] && kill -INT "$REC_PID" 2>/dev/null || true
  wait "$REC_PID" 2>/dev/null || true
  echo "  saved  -> $OUT/$REC_NAME.mov"
  REC_PID=""
}

# optional: normalize a recording to 1080x1920 9:16 (Descript can also take native)
normalize() { # normalize in.mov out.mp4
  ffmpeg -y -loglevel error -i "$1" -vf "scale=1080:-2,crop=1080:1920" -c:v libx264 -pix_fmt yuv420p "$2"
  echo "  norm   -> $2"
}

# ---- Target checklist (drive the app to each, then capture) ----
# STILLS:
#   app-focus-light      user Home, capacity=Moving slow, one task        (U1,U3,U4,MC2)
#   app-focus-dark       same in Night Owl theme                          (U1,U4 dark)
#   app-start            Home, one-thing start, task not done             (C4,U2)
#   app-capacity-sheet   "How are you showing up", "I can't right now" up  (U5,MC3,MC1)
#   app-thats-okay       RestScreen "That's okay"                         (U5,MC3)
#   app-amber-nudge      a reminder/warning rendered in amber (not red)   (MC1)
#   app-supporter-home   OuterRingHome "Cheering for [name]"              (S1,S2)
#   app-supporter-compose EncourageComposer, cheer typed                 (S1,S2)
#   app-peer-home        OuterRingHome "Standing alongside [name]"        (P1,P2)
#   app-together         "With [name] today" presence                    (P1,P2)
#   app-circle           CircleScreen "Your circle"                       (C1,C3)
#   app-rest-breathe     RestScreen breathe                               (MC1,MC3)
#   app-showingup        ShowingUpScreen tracker                          (U5)
#   app-care             CareScreen                                       (texture)
#
# RECORDINGS:
#   flow-capacity-to-okay  capacity picker -> "I can't right now" -> "That's okay"  (MC3,U5)
#   flow-complete-task     mark task done -> calm reward (no red)                   (U1,U2,U3,U4)
#   flow-send-cheer        supporter Send a cheer -> sends -> confirm               (S1,S2)
#   flow-narrow-to-one     multi -> single focus (only if it animates natively)    (MC2)
#
# Example:
#   boot
#   # (navigate to Home, capacity Moving slow, one task)
#   shot app-focus-light
#   # (open capacity picker)
#   rec_start flow-capacity-to-okay ; # tap "I can't right now" ; rec_stop

"$@"
