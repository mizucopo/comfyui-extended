ARG COMFYUI_VERSION=0.41.3
ARG COMFYUI_COMMIT=8713616fcc321624e306bbd36be5906203dcb0dc
ARG COMFYUI_GGUF_COMMIT=373048b8403a7820620065210a691263d4da0a61
ARG PYTORCH_IMAGE=pytorch/pytorch:2.14.1-cuda13.0-cudnn9-runtime@sha256:3c0b174a1339193a5bcc4b37d737c9f5ca3c4782a2293d3888e4271367eddf44

FROM ${PYTORCH_IMAGE}
ARG COMFYUI_VERSION
ARG COMFYUI_COMMIT
ARG COMFYUI_GGUF_COMMIT

LABEL org.opencontainers.image.title="comfyui-extended" \
    org.opencontainers.image.description="ComfyUI with the PyTorch CUDA runtime" \
    org.opencontainers.image.source="https://github.com/mizucopo/comfyui-extended"

RUN apt-get update \
    && apt-get install -y --no-install-recommends git libgl1 libglib2.0-0 python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN git init /opt/ComfyUI \
    && cd /opt/ComfyUI \
    && git remote add origin https://github.com/Comfy-Org/ComfyUI.git \
    && git fetch --depth 1 origin "refs/tags/v${COMFYUI_VERSION}" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "$COMFYUI_COMMIT"

# This fork accepts the qwen_image21 GGUF architecture.
RUN git init /opt/ComfyUI/custom_nodes/ComfyUI-GGUF \
    && cd /opt/ComfyUI/custom_nodes/ComfyUI-GGUF \
    && git remote add origin https://github.com/leejet/ComfyUI-GGUF.git \
    && git fetch --depth 1 origin "$COMFYUI_GGUF_COMMIT" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "$COMFYUI_GGUF_COMMIT"

# Keep the base image's matching torch/torchvision/torchaudio CUDA wheels.
RUN python -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    HF_HOME=/models/huggingface

RUN python -c 'import importlib.metadata as m; print("\n".join(n+"=="+m.version(n) for n in ("torch", "torchvision", "torchaudio")))' > /tmp/torch-constraints \
    && python -m pip install --no-cache-dir -c /tmp/torch-constraints -r /opt/ComfyUI/requirements.txt \
        -r /opt/ComfyUI/custom_nodes/ComfyUI-GGUF/requirements.txt \
    && rm /tmp/torch-constraints

WORKDIR /opt/ComfyUI
EXPOSE 8188
ENTRYPOINT ["python", "main.py"]
CMD ["--listen", "0.0.0.0", "--port", "8188", "--disable-all-custom-nodes", "--whitelist-custom-nodes", "ComfyUI-GGUF", "--disable-partner-nodes"]
