from litestar.openapi.plugins import ScalarRenderPlugin

OPENAPI_CONFIG_PARAMS = {
    "path": "/docs",
    # TODO: 通过自定义 OpenAPIRenderPlugin，支持自定义 Scalar 设置
    "render_plugins": (ScalarRenderPlugin(path="/"),),
    "use_handler_docstrings": True,
}
