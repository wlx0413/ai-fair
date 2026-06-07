AI Music Recommender macOS installer

This installer should be built from the Apple Silicon native app:
mac_app_content_final/AI Music Recommender.app

Before creating the DMG, verify the executable is arm64:

file "mac_app_content_final/AI Music Recommender.app/Contents/MacOS/AI Music Recommender"
lipo -info "mac_app_content_final/AI Music Recommender.app/Contents/MacOS/AI Music Recommender"

The output must say arm64, not x86_64.

The final app is already staged here:
mac_installer_dmg/staging_ai_music_recommender_v1/AI Music Recommender.app

To create the DMG from the project root, run:

hdiutil create -volname "AI Music Recommender" -srcfolder "mac_installer_dmg/staging_ai_music_recommender_v1" -format UDZO "mac_installer_dmg/AI-Music-Recommender-macOS-1.0.0.dmg"

The DMG will contain:
- AI Music Recommender.app
- Applications shortcut

Install by opening the DMG and dragging AI Music Recommender.app to Applications.
