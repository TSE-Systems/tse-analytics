#!/bin/sh
# Flatpak launcher for TSE Analytics.
# Force Qt onto the xcb platform plugin (X11 / XWayland); see the manifest finish-args.
export QT_QPA_PLATFORM=xcb
exec /app/lib/tse-analytics/tse-analytics "$@"
