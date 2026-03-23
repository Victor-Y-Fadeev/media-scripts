#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from typing import List, Tuple

from PIL import Image


def parse_points(s: str) -> List[int]:
    """
    Parse comma/space separated list of integers: "269, 722 1127"
    """
    parts = [p.strip() for p in s.replace(",", " ").split()]
    pts: List[int] = []
    for p in parts:
        if not p:
            continue
        pts.append(int(p))
    return pts


def build_segments(width: int, breaks: List[int]) -> List[Tuple[int, int]]:
    """
    Given image width and list of break x positions, build half-open segments [l, r).
    Example width=10, breaks=[3,7] => [(0,3),(3,7),(7,10)]
    """
    b = sorted(set(breaks))
    # Keep only valid internal boundaries (0 < x < width)
    b = [x for x in b if 0 < x < width]

    segments: List[Tuple[int, int]] = []
    start = 0
    for x in b:
        segments.append((start, x))
        start = x
    segments.append((start, width))
    return segments


def expand_segment(seg: Tuple[int, int], idx: int, margin: int, width: int) -> Tuple[int, int]:
    """
    Expand segment boundaries to include neighboring pixels.

    Rule matching your examples:
    - For the first segment, expand only RIGHT by margin: [0, r+margin)
    - For the last segment, expand only LEFT by margin: [l-margin, width)
    - For middle segments, expand BOTH sides by margin: [l-margin, r+margin)

    Clamped to [0, width].
    """
    l, r = seg
    if margin <= 0:
        return (l, r)

    if idx == 0:
        l2 = l
        r2 = r + margin
    elif r == width:  # last
        l2 = l - margin
        r2 = r
    else:
        l2 = l - margin
        r2 = r + margin

    l2 = max(0, l2)
    r2 = min(width, r2)
    if r2 < l2:
        r2 = l2
    return (l2, r2)


def make_output_name(in_path: str, i: int) -> str:
    """
    File.png -> File.001.png
    If input is File (no ext) -> File.001.png
    """
    base = os.path.basename(in_path)
    root, ext = os.path.splitext(base)
    if not ext:
        ext = ".png"
    return f"{root}.{i:03d}{ext}"


def slice_image(
    img: Image.Image,
    segments: List[Tuple[int, int]],
    margin: int,
    out_dir: str,
    in_path: str,
) -> None:
    """
    For each segment, create an RGBA image of same size:
    - Outside [l, r): fully transparent
    - Inside [l, r): original pixels
    """
    img_rgba = img.convert("RGBA")
    w, h = img_rgba.size

    for idx, seg in enumerate(segments):
        l, r = expand_segment(seg, idx, margin, w)

        # Create fully transparent output
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        # Paste the visible region
        if r > l:
            region = img_rgba.crop((l, 0, r, h))  # box is (left, upper, right, lower)
            out.paste(region, (l, 0))

        out_name = make_output_name(in_path, idx + 1)
        out_path = os.path.join(out_dir, out_name)
        out.save(out_path)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Split spectrogram image into N same-size PNGs: only one segment visible, rest transparent."
    )
    ap.add_argument("image", help="Input image (PNG recommended)")
    ap.add_argument(
        "--breaks",
        required=True,
        help='Comma/space-separated x breakpoints, e.g. "269,722,1127"',
    )
    ap.add_argument(
        "--margin",
        type=int,
        default=0,
        help="Neighbor pixels to include near boundaries (default: 0).",
    )
    ap.add_argument(
        "--out-dir",
        default=".",
        help="Output directory (default: current directory).",
    )

    args = ap.parse_args()

    img = Image.open(args.image)
    w, h = img.size
    breaks = parse_points(args.breaks)

    segments = build_segments(w, breaks)
    os.makedirs(args.out_dir, exist_ok=True)

    slice_image(img, segments, args.margin, args.out_dir, args.image)

    print(f"Image size: {w}x{h}")
    print(f"Breaks ({len(sorted(set(breaks)))}): {sorted(set(breaks))}")
    print(f"Segments: {len(segments)}")
    print(f"Margin: {args.margin}")
    print(f"Output dir: {os.path.abspath(args.out_dir)}")
    print(f"Output pattern: {os.path.splitext(os.path.basename(args.image))[0]}.###.png")


if __name__ == "__main__":
    main()
