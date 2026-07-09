#!/usr/bin/env python3
"""Extract book pages via Anthropic API — 1 image → 1 .md file."""

from __future__ import annotations

import time
from pathlib import Path

from vision_common import (
    build_base_parser,
    encode_image,
    extract_anthropic_text,
    http_post_json,
    list_images,
    load_json_config,
    load_prompt,
    page_output_path,
    parse_page_meta,
    resolve_api_key,
    skill_root,
    slice_images,
    write_page_md,
)


def call_vision(
    *,
    api_key: str,
    model: str,
    prompt: str,
    image_path: Path,
    max_tokens: int = 4096,
) -> str:
    mime, data = encode_image(image_path)

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": mime, "data": data},
                    },
                ],
            }
        ],
        "temperature": 0,
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    response = http_post_json("https://api.anthropic.com/v1/messages", headers, payload)
    return extract_anthropic_text(response)


def main() -> None:
    parser = build_base_parser("Extract book pages via Anthropic API — 1 image → 1 .md")
    parser.add_argument("--batch-size", type=int, default=1, help=argparse.SUPPRESS)
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    images_dir = Path(args.images_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    config = load_json_config(project_root)
    if config.get("vision_mode") == "agent_native":
        raise SystemExit("vision_mode is agent_native; use Agent Read tool instead of this script.")

    vision = config.get("vision", {})
    api_key = resolve_api_key(config, ["ANTHROPIC_API_KEY"])
    model = vision.get("model", "claude-sonnet-4-20250514")
    prompt = load_prompt(skill_root())

    all_images = list_images(images_dir)
    images = slice_images(all_images, args.start, args.end)

    print(f"Anthropic vision: {len(images)} pages, 1 image → 1 .md, model={model}")

    for i, img in enumerate(images, start=args.start):
        out_path = page_output_path(output_dir, i)
        if args.resume and out_path.is_file():
            print(f"  skip {out_path} (resume)")
            continue

        print(f"  page {i}: {img.name}")
        text = call_vision(
            api_key=api_key,
            model=model,
            prompt=prompt,
            image_path=img,
        )
        meta, clean_body = parse_page_meta(text)
        write_page_md(
            out_path,
            page_index=i,
            source_image=img,
            body=clean_body,
            backend="anthropic",
            meta=meta,
        )
        if args.delay:
            time.sleep(args.delay)

    print("Done.")


if __name__ == "__main__":
    import argparse