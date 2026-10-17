# Project-specific guidance

- This repository builds `mizucopo/comfyui-extended`.
- Keep the documented CUDA runtime, ComfyUI revision, entrypoint and container paths consistent
  between Dockerfile and README.
- Model downloads and GPU generation are not part of ordinary image configuration checks.
- Docker Hub tokens belong in GitHub Actions secrets. Do not read, copy or commit their values.
- A request to prepare a release configuration does not authorize an actual Docker Hub push
  or merge. The initial setup PR remains a Draft with no release classification label.
- Preserve generated workflows and release helpers. Put repository-specific runtime behavior
  in Dockerfile and README; update Copier-managed files through the template.
