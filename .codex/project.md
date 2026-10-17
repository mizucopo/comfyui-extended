# Project-specific guidance

- This repository builds `mizucopo/comfyui-extended`.
- Keep the documented CUDA runtime, ComfyUI tag, entrypoint and container paths consistent
  between Dockerfile and README.
- Model downloads and GPU generation are not part of ordinary image configuration checks.
- Docker Hub tokens belong in GitHub Actions secrets. Do not read, copy or commit their values.
- Main squash merges publish automatically after validation; release labels are not required.
  Preparing this configuration does not authorize an actual merge or Docker Hub push.
- `version` follows the official ComfyUI tag without its `v` prefix. Use the template's
  `upstream-revision` scheme and `revision` file for image-specific changes; never bump the
  upstream version based on image-only changes or tag collisions.
- Keep the single global COMFYUI_VERSION assignment aligned with `version` and update
  COMFYUI_COMMIT to that official tag's commit in the same change. Upstream updates clear
  `revision`; same-version changes use automatic rN. Preserve the checkout SHA verification.
- Keep PYTORCH_IMAGE as one complete tag-and-digest reference. Runtime-only updates preserve
  `version` and `revision` and receive their next rN during publication.
- Use Copier's normal three-way updates. Preserve the project-specific upstream revision
  policy, automatic merge publication, initial r0 handling and version checks when updating
  generated configuration.
