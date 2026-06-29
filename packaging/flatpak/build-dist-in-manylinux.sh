#!/usr/bin/env bash
#
# Build the PyInstaller bundle inside a manylinux container.
#
# Why a container and not the host or the Flatpak SDK:
#   * Host (e.g. Fedora 44, glibc 2.43): the bundle pulls in host system libraries that
#     require the host glibc, which is NEWER than the Flatpak runtime's. glibc is backward-
#     but not forward-compatible, so it fails with `version 'GLIBC_2.43' not found`.
#   * freedesktop SDK: has the X11/Qt stack but is missing assorted system libraries that
#     PySide6 links (e.g. the libgssapi_krb5.so.2 / Kerberos chain that QtNetwork needs),
#     and the SDK is immutable so they can't be installed.
#   * manylinux (AlmaLinux 9, glibc 2.34): a full distro with dnf — install every native
#     library Qt needs — while glibc 2.34 stays OLDER than the runtime, so the bundle is
#     portable into org.freedesktop.Platform.
#
# Output: dist/tse-analytics/  (consumed by `task flatpak` / `task flatpak-bundle`)

set -euo pipefail

IMAGE="${MANYLINUX_IMAGE:-quay.io/pypa/manylinux_2_34_x86_64}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

ENGINE="$(command -v podman || command -v docker || true)"
if [ -z "$ENGINE" ]; then
  echo "ERROR: neither podman nor docker found. Install one (Fedora: sudo dnf install podman)."
  exit 1
fi

echo ">> Project: $PROJECT_DIR"
echo ">> Engine:  $ENGINE"
echo ">> Image:   $IMAGE"

# System libraries PySide6/Qt (xcb platform plugin, QtNetwork, multimedia, ...) and other
# wheels load at runtime. PyInstaller bundles whatever the analysed binaries link to, so they
# must be present in the build container. Installed from AlmaLinux 9 (glibc 2.34) → portable.
SYS_LIBS="
  krb5-libs libcom_err keyutils-libs openssl-libs
  glib2 dbus-libs
  fontconfig freetype libpng libjpeg-turbo libtiff
  libX11 libXext libXrender libXi libXrandr libXcursor libXfixes
  libXcomposite libXdamage libXtst libXau libxcb libxkbcommon libxkbcommon-x11
  libICE libSM
  xcb-util xcb-util-image xcb-util-keysyms xcb-util-renderutil xcb-util-wm xcb-util-cursor
  mesa-libGL mesa-libEGL libglvnd-glx libglvnd-egl libglvnd-opengl
  nss nspr
"

# `:z` relabels the bind mount for SELinux (Fedora). Rootless podman maps container root to the
# host user, so dist/ ends up owned by the invoking user.
# UV_PYTHON_PREFERENCE=only-managed forces uv's python-build-standalone interpreter, which ships a
# shared libpython (PyInstaller requires it); the manylinux /opt/python builds are static-only.
"$ENGINE" run --rm \
  -v "$PROJECT_DIR":/work:z \
  -w /work \
  -e HOME=/work/build/manylinux-home \
  -e UV_PROJECT_ENVIRONMENT=/work/build/manylinux-venv \
  -e SYS_LIBS="$SYS_LIBS" \
  -e UV_PYTHON_PREFERENCE=only-managed \
  "$IMAGE" \
  bash -c '
    set -euo pipefail

    echo ">> Enabling repos and installing system libraries ..."
    dnf -y install dnf-plugins-core || true
    dnf config-manager --set-enabled crb || dnf config-manager --set-enabled powertools || true
    dnf -y install epel-release || true
    dnf -y install $SYS_LIBS

    echo ">> Installing uv ..."
    export PATH="$HOME/.local/bin:$PATH"
    if ! command -v uv >/dev/null 2>&1; then
      curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    echo ">> uv sync (frozen) ..."
    uv sync --frozen

    echo ">> Running PyInstaller ..."
    uv run pyinstaller --clean --noconfirm packaging/tse-analytics.spec
  '

echo ">> Done. Bundle at: $PROJECT_DIR/dist/tse-analytics"
echo ">> Sanity checks:"
echo "     # max glibc requirement should be <= the runtime's (no GLIBC_2.4x from the host):"
echo "     find dist/tse-analytics -name '*.so*' -exec objdump -T {} + 2>/dev/null | grep -oE 'GLIBC_[0-9.]+' | sort -uV | tail -1"
echo "     # krb5 chain must be bundled:"
echo "     ls dist/tse-analytics/_internal/libgssapi_krb5.so.2"
