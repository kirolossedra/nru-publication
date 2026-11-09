#!/usr/bin/env bash
# Recreate the project's exact compatible source stack in an empty source/ directory.
# System packages are intentionally not installed by this script; see Mission 1 docs.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ROOT="$PROJECT_ROOT/source/ns-3-dev"

if [[ -e "$PROJECT_ROOT/source" ]]; then
  echo "Refusing to reuse or overwrite existing source/: $PROJECT_ROOT/source" >&2
  exit 2
fi
for tool in git; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 2; }
done
mkdir -p "$PROJECT_ROOT/source"
git clone https://gitlab.com/nsnam/ns-3-dev.git "$SOURCE_ROOT"
git -C "$SOURCE_ROOT" checkout ac88b75eac1818c673cf2c939a96ac3005b1f051
mkdir -p "$SOURCE_ROOT/contrib"
git clone https://gitlab.com/cttc-lena/nr.git "$SOURCE_ROOT/contrib/nr"
git -C "$SOURCE_ROOT/contrib/nr" checkout fe0a1d2a5fb7d1547e46042041288a684893ba9e
git clone https://gitlab.com/cttc-lena/nr-u.git "$SOURCE_ROOT/contrib/nr-u"
git -C "$SOURCE_ROOT/contrib/nr-u" checkout 75a45143b1cd382326876a9597e856338673039a
git -C "$SOURCE_ROOT" apply "$PROJECT_ROOT/patches/ns-3.35-gcc-fixed-width-includes.patch"
git -C "$SOURCE_ROOT/contrib/nr-u" apply "$PROJECT_ROOT/patches/per-packet-latency.patch"
mkdir -p "$PROJECT_ROOT/logs"
RUN_TAG="$(date -u +%Y%m%dT%H%M%SZ)"
(
  cd "$SOURCE_ROOT"
  ./waf configure --enable-examples --enable-tests
) > "$PROJECT_ROOT/logs/configure-install-$RUN_TAG.log" 2>&1
(
  cd "$SOURCE_ROOT"
  ./waf build -j 4
) > "$PROJECT_ROOT/logs/build-install-$RUN_TAG.log" 2>&1

echo "Source stack configured and built. Run the baseline from $SOURCE_ROOT with ./waf --run cttc-nr-wifi-interference"
