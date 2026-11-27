#!/bin/sh
set -eu

image=$1
probe_dir=$(mktemp -d)
trap 'rm -rf "$probe_dir"' EXIT

cat > "$probe_dir/main.py" <<'PY'
import json

import comfy.options

comfy.options.enable_args_parsing()
from comfy.cli_args import args

print(json.dumps([
    args.listen,
    args.port,
    args.disable_all_custom_nodes,
    args.whitelist_custom_nodes,
    args.disable_partner_nodes,
    args.lowvram,
]))
PY

check_startup() {
    scenario=$1
    expected=$2
    shift 2
    actual=$(docker run --rm --volume "$probe_dir/main.py:/opt/ComfyUI/main.py:ro" "$@")
    if [ "$actual" != "$expected" ]; then
        printf '%s\nExpected: %s\nActual: %s\n' "$scenario" "$expected" "$actual" >&2
        return 1
    fi
    printf '%s: OK\n' "$scenario"
}

check_startup 'Default startup' '["0.0.0.0", 8188, true, ["ComfyUI-GGUF"], true, false]' "$image"
check_startup 'Additional option' '["0.0.0.0", 8188, true, ["ComfyUI-GGUF"], true, true]' "$image" --lowvram
check_startup 'Repeated options' '["127.0.0.1", 8190, true, ["AnotherNode"], true, false]' \
    "$image" --listen 127.0.0.1 --port 8190 --whitelist-custom-nodes AnotherNode
check_startup 'Explicit override' '["127.0.0.1", 8190, false, [], false, false]' \
    --entrypoint python "$image" main.py --port 8190
