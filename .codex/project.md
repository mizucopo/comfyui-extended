# Project-specific guidance

- This repository builds `mizucopo/comfyui-extended`.
- Keep the documented CUDA runtime, ComfyUI tag, entrypoint and container paths consistent
  between Dockerfile and README.
- Model downloads and GPU generation are not part of ordinary image configuration checks.
- Docker Hub tokens belong in GitHub Actions secrets. Do not read, copy or commit their values.
- A request to prepare a release configuration does not authorize an actual Docker Hub push
  or merge. Do not add a release classification label without publication authorization.
- `version` follows the official ComfyUI tag without its `v` prefix. Use the template's
  `upstream-revision` scheme and `revision` file for image-specific changes; never bump the
  upstream version based on release classification or tag collisions.
- Keep Dockerfile's COMFYUI_VERSION aligned with `version` and pin COMFYUI_COMMIT to that
  official tag. Upstream updates clear `revision`; same-version changes use automatic rN.
- Use Copier's normal three-way updates. Preserve the project-specific upstream revision
  policy, initial r0 handling and version checks when updating generated configuration.
