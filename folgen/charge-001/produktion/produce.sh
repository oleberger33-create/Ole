#!/usr/bin/env bash
# Baut Charge 001 komplett: Ton + Zeitplan, Bilder (parallel, echte Bildrate aus timeline.json, 60 fps), fertiges MP4.
#   ./produce.sh <arbeitsordner> <tts-modelle> <schriftenordner>
set -euo pipefail
WORK=${1:?arbeitsordner}; MODELS=${2:?tts-modelle}; FONTS=${3:?schriften}
HERE=$(cd "$(dirname "$0")" && pwd)
WORKERS=${WORKERS:-4}
mkdir -p "$WORK"
cd "$HERE"
python3 prep_assets.py
python3 build.py "$WORK" "$MODELS"

read -r N FPS < <(python3 -c "import json;t=json.load(open('$WORK/timeline.json'));print(round(t['total']*t['fps']),t['fps'])")
echo "Bilder: $N bei $FPS fps, $WORKERS Worker"
export NODE_PATH=${NODE_PATH:-$(npm root -g)}
pids=()
: > "$WORK/teile.txt"
for ((k = 0; k < WORKERS; k++)); do
  a=$((N * k / WORKERS)); b=$((N * (k + 1) / WORKERS))
  node render.js "$WORK/timeline.json" "$FONTS" "$WORK/teil$k.mp4" $a $b > "$WORK/render$k.log" 2>&1 &
  pids+=($!)
  echo "file 'teil$k.mp4'" >> "$WORK/teile.txt"
done
for p in "${pids[@]}"; do wait "$p"; done
ffmpeg -loglevel error -y -f concat -safe 0 -i "$WORK/teile.txt" -c copy "$WORK/bild.mp4"

# Lautheit auf -14 LUFS (YouTube-Referenz), zwei Durchgänge
read -r I TP LRA TH OFF < <(ffmpeg -hide_banner -nostats -i "$WORK/mix.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 \
  | python3 -c "import sys,json;s=sys.stdin.read();j=json.loads(s[s.rindex('{'):]);print(j['input_i'],j['input_tp'],j['input_lra'],j['input_thresh'],j['target_offset'])")
ffmpeg -loglevel error -y -i "$WORK/bild.mp4" -i "$WORK/mix.wav" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=48000" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$WORK/charge-001.mp4"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$WORK/charge-001.mp4"
