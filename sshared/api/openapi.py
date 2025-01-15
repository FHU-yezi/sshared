from litestar.openapi.plugins import ScalarRenderPlugin

OPENAPI_CONFIG_PARAMS = {
    "path": "/docs",
    "render_plugins": (ScalarRenderPlugin(path="/"),),
    "use_handler_docstrings": True,
}
