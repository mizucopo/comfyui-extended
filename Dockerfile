# pc-setup PR398 uses the same CUDA 13.0 runtime and ComfyUI revision.
FROM pytorch/pytorch:2.14.1-cuda13.0-cudnn9-runtime@sha256:3c0b174a1339193a5bcc4b37d737c9f5ca3c4782a2293d3888e4271367eddf44

ARG COMFYUI_REVISION=98cc0bf84b7cb1383654c5b402e7612d875d6d22

LABEL org.opencontainers.image.title="comfyui-extended" \
    org.opencontainers.image.description="ComfyUI with the PyTorch CUDA 13.0 runtime" \
    org.opencontainers.image.source="https://github.com/mizucopo/comfyui-extended"

RUN apt-get update \
    && apt-get install -y --no-install-recommends git libgl1 libglib2.0-0 python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN git init /opt/ComfyUI \
    && cd /opt/ComfyUI \
    && git remote add origin https://github.com/Comfy-Org/ComfyUI.git \
    && git fetch --depth 1 origin "$COMFYUI_REVISION" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "$COMFYUI_REVISION"

# Keep the base image's matching torch/torchvision/torchaudio CUDA wheels.
RUN python -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    HF_HOME=/models/huggingface

RUN python -c 'import importlib.metadata as m; print("\n".join(n+"=="+m.version(n) for n in ("torch", "torchvision", "torchaudio")))' > /tmp/torch-constraints \
    && python -m pip install --no-cache-dir -c /tmp/torch-constraints -r /opt/ComfyUI/requirements.txt \
    && rm /tmp/torch-constraints

WORKDIR /opt/ComfyUI
EXPOSE 8188
ENTRYPOINT ["python", "main.py"]
CMD ["--listen", "0.0.0.0", "--port", "8188", "--disable-all-custom-nodes", "--disable-partner-nodes"]
