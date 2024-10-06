from typing import Any

from litestar.openapi.plugins import ScalarRenderPlugin


# 由于 Scalar Plugin 实现逻辑中硬编码了 openapi.json 文件的路径
# 导致 API 通过反代暴露于 /api 路径下时 Scalar 无法正常找到 OpenAPI Schema
# 因此造成了文档无法展示，此处通过覆盖 openapi.json 查找逻辑解决此问题
class CustomScalarRenderPlugin(ScalarRenderPlugin):
    @staticmethod
    def get_openapi_json_route(request: Any) -> str:  # noqa: ANN401
        del request
        return "/api/docs/openapi.json"


def generate_openapi_config_params() -> dict[str, Any]:
    return {
        "path": "/docs",
        "render_plugins": (CustomScalarRenderPlugin(path="/"),),
        "use_handler_docstrings": True,
    }
