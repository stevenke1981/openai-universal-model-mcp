---
name: openai-image-generation
description: Generate or edit images with OpenAI GPT Image models through the Platform API. Trigger for image generation, image edit, reference image, transparent PNG, 生圖, 圖片編輯, 去背, or GPT Image.
---

# OpenAI Image Generation and Editing

## Choose the path

- New image from a prompt: `openai_generate_image`.
- Edit an existing local image: `openai_edit_image`.
- Multi-turn visual reasoning or image generation as part of a conversation: use `openai_create_response` with a supported mainline model and an `image_generation` tool in `tools_json`.
- Image understanding without generation: use `openai_create_response` with `input_image` content.

## Execution rules

1. Discover and inspect the requested image model.
2. Use a current documented GPT Image model ID. Do not assume a display label equals an API ID.
3. Choose size, quality, background, complexity, and output format deliberately.
4. For GPT Image 2.6, use `complexity=low|medium|high` when useful; the model also supports SVG and animated GIF output.
5. For GIF output, set `frame_count` from 2 to 16 and choose `frame_duration_ms` intentionally.
6. Use `n` conservatively; every image may incur cost.
5. For edits, preserve the original file and write a new output under the artifact directory.
6. Return the exact saved path and format. Do not claim a file was saved unless the tool returns a path.
7. Use mask/markup only when the endpoint and model documentation confirms support.

## Continuity workflow

For character or storyboard work, keep a stable reference image, describe invariant identity/wardrobe/camera/background, and make one controlled change per edit. Review each output before using it as the next reference.

## Chinese intent

「生成圖片」「修改圖片」「透明背景」「保留人物不變」「參考圖生圖」 are image-task triggers.
