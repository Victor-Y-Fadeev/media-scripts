#!/usr/bin/env python3
from __future__ import annotations

import argparse
import colorsys
from dataclasses import dataclass
from typing import List, Tuple

from PIL import Image, ImageDraw


@dataclass(frozen=True)
class Gap:
    x: int
    bottom_y: int


def rgb_to_l_0_255(r: int, g: int, b: int) -> float:
    """
    Convert RGB (0..255) to HLS Lightness L in 0..255.
    colorsys uses floats 0..1 and returns H, L, S (HLS).
    """
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    _h, l, _s = colorsys.rgb_to_hls(rf, gf, bf)
    return l * 255.0


def load_l_matrix(img: Image.Image) -> List[List[float]]:
    """
    Build L (lightness) matrix [y][x] in 0..255 for the entire image.
    """
    img = img.convert("RGB")
    w, h = img.size
    px = img.load()
    L = [[0.0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            L[y][x] = rgb_to_l_0_255(r, g, b)
    return L


def find_gaps(
    L: List[List[float]],
    thr: float = 25.0,
    bottom_y: int | None = None,
    require_full_column_dark: bool = True,
) -> List[Gap]:
    """
    Find x positions where in the bottom row:
        prev L > thr, cur L <= thr, next L > thr
    Then optionally validate that for all y in column x: L[y][x] <= thr.
    """
    h = len(L)
    if h == 0:
        return []
    w = len(L[0])

    by = (h - 1) if bottom_y is None else bottom_y
    if not (0 <= by < h):
        raise ValueError(f"bottom_y={bottom_y} is out of range for height={h}")

    gaps: List[Gap] = []
    row = L[by]

    # avoid x=0 and x=w-1 because we need prev and next
    for x in range(1, w - 1):
        prev_l = row[x - 1]
        cur_l = row[x]
        next_l = row[x + 1]

        if prev_l > thr and cur_l <= thr and next_l > thr:
            if require_full_column_dark:
                # Verify entire vertical line is dark (L <= thr)
                col_ok = True
                for y in range(h):
                    if L[y][x] > thr:
                        col_ok = False
                        break
                if not col_ok:
                    continue

            gaps.append(Gap(x=x, bottom_y=by))

    return gaps


def draw_gaps(
    img: Image.Image,
    gaps: List[Gap],
    out_path: str,
    line_width: int = 1,
) -> None:
    """
    Save a copy of the image with vertical lines drawn at each gap x.
    (Default color = red.)
    """
    out = img.convert("RGB").copy()
    draw = ImageDraw.Draw(out)
    w, h = out.size
    for g in gaps:
        x = g.x
        draw.line([(x, 0), (x, h - 1)], fill=(255, 0, 0), width=line_width)
    out.save(out_path)


def main() -> None:
    ap = argparse.ArgumentParser(description="Find vertical dark gaps in spectrogram image via HLS lightness.")
    ap.add_argument("image", help="Input PNG/JPG/etc")
    ap.add_argument("--thr", type=float, default=25.0, help="Lightness threshold in 0..255 (default: 25)")
    ap.add_argument(
        "--bottom-y",
        type=int,
        default=None,
        help="Row index to scan (default: last row). Use 255 if you really mean y=255.",
    )
    ap.add_argument(
        "--no-column-check",
        action="store_true",
        help="Disable 'entire column must be dark' validation",
    )
    ap.add_argument("--mark-out", default=None, help="If set, save marked image with detected gaps drawn")
    ap.add_argument("--line-width", type=int, default=1, help="Line width for marking (default: 1)")
    args = ap.parse_args()

    img = Image.open(args.image)
    L = load_l_matrix(img)

    gaps = find_gaps(
        L,
        thr=args.thr,
        bottom_y=args.bottom_y,
        require_full_column_dark=not args.no_column_check,
    )

    # Print results
    print(f"Image size: {img.size[0]}x{img.size[1]}")
    print(f"Threshold L <= {args.thr}")
    if args.bottom_y is None:
        print(f"Bottom row used: y={img.size[1]-1}")
    else:
        print(f"Bottom row used: y={args.bottom_y}")

    xs = [g.x for g in gaps]
    print(f"Found gaps: {len(xs)}")
    if xs:
        print("x positions:", ", ".join(map(str, xs)))

    if args.mark_out:
        draw_gaps(img, gaps, args.mark_out, line_width=args.line_width)
        print(f"Marked image saved to: {args.mark_out}")


if __name__ == "__main__":
    main()
