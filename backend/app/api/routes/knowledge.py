"""知识库API路由"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    KnowledgeAddRequest,
    KnowledgeAddResponse,
    KnowledgeStatsResponse,
    KnowledgeDeleteResponse,
    KnowledgeDocument,
)
from ...services.knowledge_service import get_knowledge_service

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.post(
    "/query",
    response_model=KnowledgeQueryResponse,
    summary="查询知识库",
    description="根据查询文本搜索旅行知识库，返回相关的知识文档"
)
async def query_knowledge(request: KnowledgeQueryRequest):
    """查询知识库

    Args:
        request: 查询请求参数

    Returns:
        知识文档列表
    """
    try:
        knowledge_service = get_knowledge_service()

        results = knowledge_service.query(
            query_text=request.query,
            city=request.city,
            top_k=request.top_k
        )

        documents = [
            KnowledgeDocument(
                id=r["id"],
                content=r["content"],
                metadata=r["metadata"],
                score=r["score"]
            )
            for r in results
        ]

        return KnowledgeQueryResponse(
            success=True,
            message=f"找到 {len(documents)} 条相关知识",
            data=documents
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"知识库查询失败: {str(e)}"
        )


@router.post(
    "/add",
    response_model=KnowledgeAddResponse,
    summary="添加知识文档",
    description="向知识库中添加新的知识文档"
)
async def add_knowledge(request: KnowledgeAddRequest):
    """添加知识文档

    Args:
        request: 添加文档请求

    Returns:
        文档ID
    """
    try:
        knowledge_service = get_knowledge_service()

        doc_id = knowledge_service.add_document(
            content=request.content,
            metadata=request.metadata
        )

        if doc_id:
            return KnowledgeAddResponse(
                success=True,
                message="文档添加成功",
                doc_id=doc_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="文档添加失败，知识库可能未初始化"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"添加文档失败: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=KnowledgeStatsResponse,
    summary="知识库统计",
    description="获取知识库的统计信息"
)
async def get_knowledge_stats():
    """获取知识库统计信息

    Returns:
        统计信息
    """
    try:
        knowledge_service = get_knowledge_service()
        stats = knowledge_service.get_stats()

        return KnowledgeStatsResponse(
            success=stats.get("status") == "healthy",
            message="统计信息获取成功" if stats.get("status") == "healthy" else "知识库不可用",
            data=stats
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.delete(
    "/{doc_id}",
    response_model=KnowledgeDeleteResponse,
    summary="删除知识文档",
    description="从知识库中删除指定文档"
)
async def delete_knowledge(doc_id: str):
    """删除知识文档

    Args:
        doc_id: 文档ID

    Returns:
        删除结果
    """
    try:
        knowledge_service = get_knowledge_service()

        success = knowledge_service.delete_document(doc_id)

        if success:
            return KnowledgeDeleteResponse(
                success=True,
                message=f"文档 {doc_id} 已删除"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"文档 {doc_id} 不存在或删除失败"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除文档失败: {str(e)}"
        )