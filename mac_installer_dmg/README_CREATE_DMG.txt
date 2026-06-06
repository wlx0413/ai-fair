AI Music Recommender macOS installer

The final app is already staged here:
mac_installer_dmg/staging_ai_music_recommender_v1/AI Music Recommender.app

To create the DMG from the project root, run:

hdiutil create -volname "AI Music Recommender" -srcfolder "mac_installer_dmg/staging_ai_music_recommender_v1" -format UDZO "mac_installer_dmg/AI-Music-Recommender-macOS-1.0.0.dmg"

The DMG will contain:
- AI Music Recommender.app
- Applications shortcut

Install by opening the DMG and dragging AI Music Recommender.app to Applications.
