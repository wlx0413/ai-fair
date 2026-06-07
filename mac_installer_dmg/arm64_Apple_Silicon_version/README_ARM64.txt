AI Music Recommender macOS Apple Silicon installer

This folder is for the native Apple Silicon / arm64 build.

Use this version on Macs with Apple M-series chips. It is not an Intel/Rosetta
translated build.

Expected installer name:
AI-Music-Recommender-macOS-arm64-Apple-Silicon-1.0.0.dmg

Architecture check:
file "AI Music Recommender.app/Contents/MacOS/AI Music Recommender"
lipo -info "AI Music Recommender.app/Contents/MacOS/AI Music Recommender"

Expected output: arm64
