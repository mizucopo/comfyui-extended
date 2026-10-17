# Project-specific guidance

- This repository builds `mizucopo/comfyui-extended`; normal development is on the Mac mini.
- Keep the CUDA runtime, ComfyUI revision, entrypoint and mount paths compatible with the
  documented pc-setup PR398 baseline. Do not edit pc-setup from this repository's tasks.
- Model downloads and GPU generation are not part of ordinary image configuration checks.
- Docker Hub tokens belong in GitHub Actions secrets. Do not read, copy or commit their values.
- A request to prepare a release configuration does not authorize an actual Docker Hub push
  or merge. The initial setup PR remains a Draft with no release classification label.
- Preserve generated workflows and release helpers. Put repository-specific runtime behavior
  in Dockerfile and README; update Copier-managed files through the template.
