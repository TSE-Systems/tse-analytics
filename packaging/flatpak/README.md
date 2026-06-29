# Flatpak packaging (Linux)

This directory packages TSE Analytics as a Flatpak for **direct / private distribution**
(a single `.flatpak` bundle or a self-hosted repo). It wraps the PyInstaller build rather than
building from source, because the project pins Python `3.14.5` and a heavy scientific / Rust
dependency stack that no stock Flatpak runtime can reproduce offline.

> Not Flathub-eligible — Flathub requires building from source, not bundling a pre-built binary.

> **Build the PyInstaller bundle inside a manylinux container, not on the host.** glibc is
> backward- but not forward-compatible: a bundle built on a bleeding-edge host (e.g. Fedora's
> glibc 2.43) pulls in system libraries that require that glibc and then fail inside the
> older-glibc runtime with `version 'GLIBC_2.43' not found`. The Flatpak SDK is too minimal —
> it lacks libraries PySide6 links (e.g. the Kerberos `libgssapi_krb5.so.2` chain QtNetwork needs)
> and is immutable. `task flatpak-dist` therefore builds inside `manylinux_2_34`
> (AlmaLinux 9, glibc 2.34): a full distro where `dnf` provides every native lib Qt needs, while
> glibc 2.34 stays older than the runtime so the bundle is portable. Requires `podman` (or
> `docker`).

## Files

| File | Purpose |
| --- | --- |
| `io.github.TSE_Systems.tse_analytics.yml` | flatpak-builder manifest |
| `io.github.TSE_Systems.tse_analytics.desktop` | Desktop entry |
| `io.github.TSE_Systems.tse_analytics.metainfo.xml` | AppStream metadata |
| `io.github.TSE_Systems.tse_analytics.png` | 256×256 app icon |
| `tse-analytics.sh` | Launcher (forces `QT_QPA_PLATFORM=xcb`) |
| `build-dist-in-manylinux.sh` | Builds the PyInstaller bundle inside a manylinux container |

## Prerequisites (one-time)

```sh
# Flatpak tooling + a container engine for the bundle build
sudo dnf install flatpak flatpak-builder podman        # Fedora
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Runtime + SDK used by flatpak-builder. Must match `runtime-version` in the manifest.
flatpak install flathub org.freedesktop.Platform//25.08 org.freedesktop.Sdk//25.08
```

## Build & run

```sh
task flatpak-dist      # PyInstaller inside the SDK -> dist/tse-analytics/
task flatpak           # flatpak-builder --install (user)
flatpak run io.github.TSE_Systems.tse_analytics
```

Do **not** use `task deploy` for the Flatpak — it runs PyInstaller on the host and produces a
binary that requires the host's glibc (see the note above). `task deploy` remains for the Windows
build and for a host-native Linux build.

## Single-file bundle for distribution

```sh
task flatpak-dist
task flatpak-bundle    # -> dist/tse-analytics.flatpak
```

Install on a target machine (the freedesktop 25.08 runtime must be available there):

```sh
flatpak install --user dist/tse-analytics.flatpak
```

## Regenerating the icon

The committed PNG is extracted from `resources/icons/app.ico`. To regenerate:

```sh
# ImageMagick
magick "resources/icons/app.ico[0]" -resize 256x256 \
  packaging/flatpak/io.github.TSE_Systems.tse_analytics.png
# or icoutils
icotool -x -w 256 -o packaging/flatpak/io.github.TSE_Systems.tse_analytics.png \
  resources/icons/app.ico
```

## Notes

- **`QT_QPA_PLATFORM=xcb`** is forced three ways: in the app code (`tse_analytics/main.py`,
  for any Linux run), in the launcher script, and via `--env` in the manifest. xcb (X11 /
  XWayland) is the reliable path for the PyInstaller-bundled Qt inside the sandbox.
- **Missing xcb library?** If `flatpak run` reports `Could not load the Qt platform plugin "xcb"`,
  the bundled Qt is missing a system lib (commonly `libxcb-cursor.so.0`). Since the bundle is built
  inside the SDK (`task flatpak-dist`), the lib must be available there — the freedesktop SDK
  normally provides the xcb libraries, but if not, add the missing library as a module to the
  manifest.
- **`--filesystem=home`** is broad; tighten to XDG portals / specific directories later if desired.
