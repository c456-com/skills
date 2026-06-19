#!/usr/bin/env python3
"""Vision page extract via OpenAI-compatible multimodal API (stdlib only)."""

from __future__ import annotations

import time
from pathlib import Path

from vision_common import (
    build_base_parser,
    chunk_batches,
    encode_image,
    extract_openai_text,
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
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    image_paths: list[Path],
    max_tokens: int = 4096,
) -> str:
    base = base_url.rstrip("/")
    url = f"{base}/chat/completions" if not base.endswith("/chat/completions") else base

    content: list[dict] = [{"type": "text", "text": prompt}]
    for path in image_paths:
        mime, data = encode_image(path)
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{data}"},
            }
        )

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = http_post_json(url, headers, payload)
    return extract_openai_text(response)


def main() -> None:
    parser = build_base_parser("Extract book pages via OpenAI-compatible vision API")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    images_dir = Path(args.images_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    config = load_json_config(project_root)
    if config.get("vision_mode") == "agent_native":
        raise SystemExit("vision_mode is agent_native; use Agent Read tool instead of this script.")

    vision = config.get("vision", {})
    api_key = resolve_api_key(config, ["OPENAI_API_KEY", "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY"])
    base_url = vision.get("base_url", "https://api.openai.com/v1").strip()
    model = vision.get("model", "gpt-4o")
    batch_size = args.batch_size or vision.get("max_images_per_request", 2)
    prompt = load_prompt(skill_root())

    all_images = list_images(images_dir)
    images = slice_images(all_images, args.start, args.end)

    print(f"OpenAI-compatible vision: {len(images)} pages, batch_size={batch_size}, model={model}")

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
            base_url=base_url,
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
            backend="openai_compatible",
        )
        if args.delay:
            time.sleep(args.delay)

    print("Done.")


if __name__ == "__main__":
    main()
