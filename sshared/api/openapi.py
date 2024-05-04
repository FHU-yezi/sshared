from typing import Any, Dict

from litestar.openapi.plugins import ScalarRenderPlugin


def generate_openapi_config_params() -> Dict[str, Any]:
    return {
        "path": "/docs",
        "render_plugins": (ScalarRenderPlugin(path="/"),),
        "use_handler_docstrings": True,
    }
