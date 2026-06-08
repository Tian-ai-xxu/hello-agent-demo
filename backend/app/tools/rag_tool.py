"""RAG知识检索工具 - 用于Agent集成"""

from typing import Dict, Any, List

from hello_agents.tools.base import Tool, ToolParameter

from ..services.knowledge_service import get_knowledge_service


class RAGTool(Tool):
    """RAG知识检索工具

    将知识库服务包装为Agent可调用的工具。
    通过 [TOOL_CALL:rag_search:query=...] 格式进行调用。
    """

    def __init__(self):
        """初始化RAG工具"""
        super().__init__(
            name="rag_search",
            description="搜索旅行知识库，获取目的地相关的旅行攻略、美食推荐、文化知识、交通建议等。返回相关的知识内容供行程规划参考。"
        )
        self._knowledge_service = get_knowledge_service()

    def get_parameters(self) -> List[ToolParameter]:
        """获取工具参数定义"""
        return [
            ToolParameter(
                name="query",
                type="string",
                description="搜索关键词，例如：'北京故宫攻略'、'成都美食推荐'、'上海交通指南'",
                required=True
            ),
            ToolParameter(
                name="city",
                type="string",
                description="城市名称，用于过滤结果，例如：'北京'、'上海'",
                required=False,
                default=""
            )
        ]

    def run(self, parameters: Dict[str, Any]) -> str:
        """执行知识检索

        Args:
            parameters: 包含 query（必需）和 city（可选）的参数字典

        Returns:
            str: 检索结果文本
        """
        try:
            query = parameters.get("query", "")
            city = parameters.get("city", "")

            if not query:
                return "错误: 查询关键词不能为空"

            # 确保知识库已初始化
            self._knowledge_service._ensure_initialized()

            # 查询知识库
            results = self._knowledge_service.query(
                query_text=query,
                city=city if city else None,
                top_k=5
            )

            if not results:
                return "知识库中未找到相关内容。请根据您的知识为用户提供旅行建议。"

            # 格式化结果
            formatted_text = self._format_results(results)
            return formatted_text

        except Exception as e:
            return f"知识检索失败: {str(e)}"

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """格式化检索结果为可读文本

        Args:
            results: 检索结果列表

        Returns:
            格式化后的文本
        """
        lines = ["以下是从旅行知识库中检索到的相关信息：\n"]

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            title = metadata.get("title", "知识片段")
            content = result.get("content", "")
            score = result.get("score", 0)

            lines.append(f"【{i}. {title}】（相关度: {score:.0%}）")
            lines.append(content)
            lines.append("")

        return "\n".join(lines)