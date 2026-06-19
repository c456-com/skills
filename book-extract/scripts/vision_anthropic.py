#!/usr/bin/env python3
"""Vision page extract via Anthropic Messages API (stdlib only)."""

from __future__ import annotations

import time
from pathlib import Path

from vision_common import (
    build_base_parser,
    chunk_batches,
    encode_image,
    extract_anthropic_text,
    http_post_json,
    list_images,
    load_json_config,
    load_prompt,
    page_output_path,
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
    image_paths: list[Path],
    max_tokens: int = 4096,
) -> str:
    content: list[dict] = []
    for path in image_paths:
        mime, data = encode_image(path)
        content.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": mime, "data": data},
            }
        )
    content.append({"type": "text", "text": prompt})

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": content}],
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    response = http_post_json("https://api.anthropic.com/v1/messages", headers, payload)
    return extract_anthropic_text(response)


def main() -> None:
    parser = build_base_parser("Extract book pages via Anthropic vision API")
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
    batch_size = args.batch_size or vision.get("max_images_per_request", 2)
    prompt = load_prompt(skill_root())

    all_images = list_images(images_dir)
    images = slice_images(all_images, args.start, args.end)

    print(f"Anthropic vision: {len(images)} pages, batch_size={batch_size}, model={model}")

    indexed = list(enumerate(images, start=args.start))
    batches = chunk_batches(indexed, batch_size)

    for batch in batches:
        indices = [i for i, _ in batch]
        paths = [p for _, p in batch]
        out_path = page_output_path(output_dir, indices[0])
        if args.resume and out_path.is_file():
            print(f"  skip {out_path} (resume)")
            continue

        print(f"  batch pages {indices[0]}-{indices[-1]}: {[p.name for p in paths]}")
        text = call_vision(
            api_key=api_key,
            model=model,
            prompt=prompt,
            image_paths=paths,
        )
        write_page_md(
            out_path,
            page_indices=indices,
            source_images=paths,
            body=text,
            backend="anthropic",
        )
        if args.delay:
            time.sleep(args.delay)

    print("Done.")


if __name__ == "__main__":
    main()
