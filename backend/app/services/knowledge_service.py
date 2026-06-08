"""知识库服务 - 基于ChromaDB的RAG知识库管理（使用本地TF-IDF嵌入）"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np

from ..config import get_settings


class KnowledgeService:
    """知识库服务（单例模式）

    使用ChromaDB作为向量数据库，sklearn TfidfVectorizer作为嵌入模型。
    支持Markdown文档的自动分块、嵌入和语义检索。
    完全离线工作，不需要下载任何模型。
    """

    def __init__(self):
        """初始化知识库服务（延迟加载）"""
        self._vectorizer = None
        self._chroma_client = None
        self._collection = None
        self._initialized = False
        self._init_error = None

    def _ensure_initialized(self) -> bool:
        """确保服务已初始化，返回是否成功"""
        if self._initialized:
            return True
        if self._init_error:
            return False

        try:
            self._init_vectorizer()
            self._init_chromadb()
            self._initialized = True
            return True
        except Exception as e:
            self._init_error = str(e)
            print(f"[WARN]  知识库服务初始化失败: {e}")
            print("   旅行规划功能仍可正常使用，但知识库不可用")
            return False

    def _init_vectorizer(self):
        """初始化TF-IDF向量化器"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.preprocessing import normalize
            print("[IMPORT] 正在初始化TF-IDF向量化器...")
            # 使用支持中文的分词级别TF-IDF
            self._vectorizer = TfidfVectorizer(
                analyzer='char_wb',  # 字符级别n-gram，适合中文
                ngram_range=(2, 4),  # 2-4字符的n-gram
                max_features=10000,  # 最大特征数
                sublinear_tf=True,   # 使用1+log(tf)
            )
            self._normalize = normalize
            print("[OK] TF-IDF向量化器初始化成功")
        except ImportError:
            raise ImportError(
                "scikit-learn 未安装，请运行: pip install scikit-learn"
            )

    def _init_chromadb(self):
        """初始化ChromaDB客户端和集合"""
        settings = get_settings()

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            # 确保持久化目录存在
            persist_dir = settings.get_chromadb_persist_dir()
            os.makedirs(persist_dir, exist_ok=True)

            print(f"[IMPORT] 正在初始化ChromaDB: {persist_dir}")

            self._chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False)
            )

            # 获取或创建集合
            try:
                self._collection = self._chroma_client.get_collection(
                    name="trip_knowledge"
                )
                print(f"[OK] 知识库集合已存在: {self._collection.count()} 条记录")
            except Exception:
                self._collection = self._chroma_client.create_collection(
                    name="trip_knowledge",
                    metadata={
                        "description": "旅行知识库",
                        "embedding_model": "tfidf-char-ngram",
                        "hnsw:space": "cosine"
                    }
                )
                print("[OK] 知识库集合已创建")

        except ImportError:
            raise ImportError(
                "chromadb 未安装，请运行: pip install chromadb"
            )
        except Exception as e:
            raise RuntimeError(f"初始化ChromaDB失败: {e}")

    def embed(self, texts: List[str]) -> List[List[float]]:
        """生成文本嵌入向量（使用TF-IDF）

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        if not texts:
            return []

        try:
            # 检查vectorizer是否已fit（需要有语料库）
            if not hasattr(self._vectorizer, 'vocabulary_') or not self._vectorizer.vocabulary_:
                # 如果没有fit过，先fit当前文本
                matrix = self._vectorizer.fit_transform(texts)
            else:
                matrix = self._vectorizer.transform(texts)

            # 归一化向量
            normalized = self._normalize(matrix, norm='l2')
            # 转换为稠密列表
            embeddings = normalized.toarray().tolist()
            return embeddings
        except Exception as e:
            print(f"[WARN]  嵌入生成失败: {e}")
            return []

    def ingest_documents(self, force: bool = False) -> int:
        """从knowledge_data_dir加载所有Markdown文档并索引

        Args:
            force: 是否强制重新索引（即使已索引过）

        Returns:
            索引的文档块数量
        """
        if not self._ensure_initialized():
            return 0

        # 检查是否已索引过
        if not force and self._collection.count() > 0:
            print(f"[BOOK] 知识库已有 {self._collection.count()} 条记录，跳过索引")
            return self._collection.count()

        settings = get_settings()
        knowledge_dir = settings.get_knowledge_data_dir()

        if not os.path.exists(knowledge_dir):
            os.makedirs(knowledge_dir, exist_ok=True)
            print(f"[DIR] 知识库目录已创建: {knowledge_dir}")
            # 创建一个README文件
            readme_path = os.path.join(knowledge_dir, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# 旅行知识库\n\n请将Markdown格式的旅行知识文档放入此目录。\n")
            return 0

        print(f"[BOOK] 开始索引知识文档: {knowledge_dir}")

        # 收集所有Markdown文件
        md_files = []
        for root, dirs, files in os.walk(knowledge_dir):
            for file in files:
                if file.endswith(".md") and file != "README.md":
                    md_files.append(os.path.join(root, file))

        if not md_files:
            print("[BOOK] 未找到知识文档，跳过索引")
            return 0

        print(f"[FILE] 找到 {len(md_files)} 个Markdown文档")

        # 如果force=True，清空已有数据
        if force and self._collection.count() > 0:
            # 删除旧集合，创建新集合
            self._chroma_client.delete_collection("trip_knowledge")
            self._collection = self._chroma_client.create_collection(
                name="trip_knowledge",
                metadata={
                    "description": "旅行知识库",
                    "embedding_model": "tfidf-char-ngram",
                    "hnsw:space": "cosine"
                }
            )

        all_chunks = []
        all_metadatas = []
        all_ids = []

        for file_path in md_files:
            chunks, metadatas, ids = self._chunk_document(file_path)
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
            all_ids.extend(ids)

        if not all_chunks:
            print("[BOOK] 没有可索引的内容")
            return 0

        print(f"[WRITE] 共 {len(all_chunks)} 个文档块，正在生成嵌入...")

        # 使用所有chunks来fit vectorizer（第一次）
        # 重置vectorizer，用全量数据重新fit
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            max_features=10000,
            sublinear_tf=True,
        )

        # 生成嵌入
        embeddings = self.embed(all_chunks)
        if not embeddings:
            print("[WARN]  嵌入生成失败，无法索引文档")
            return 0

        print(f"[OK] 嵌入生成完成，维度: {len(embeddings[0])}")

        # 批量添加到ChromaDB
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_end = min(i + batch_size, len(all_chunks))
            self._collection.add(
                ids=all_ids[i:batch_end],
                documents=all_chunks[i:batch_end],
                embeddings=embeddings[i:batch_end],
                metadatas=all_metadatas[i:batch_end]
            )

        print(f"[OK] 知识库索引完成: {len(all_chunks)} 个文档块")
        return len(all_chunks)

    def _chunk_document(self, file_path: str) -> tuple:
        """将Markdown文档分块

        按 ## 二级标题分块，每块包含标题和内容。

        Args:
            file_path: 文档路径

        Returns:
            (chunks, metadatas, ids) 三元组
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[WARN]  读取文件失败 {file_path}: {e}")
            return [], [], []

        # 提取文档标题（第一个 # 标题）
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        doc_title = title_match.group(1).strip() if title_match else Path(file_path).stem

        # 提取城市信息（从文件名或内容中）
        source_file = Path(file_path).name
        city = self._extract_city(source_file, content)

        chunks = []
        metadatas = []
        ids = []

        # 按 ## 二级标题分割
        sections = re.split(r"\n(?=##\s)", content)

        chunk_idx = 0

        for section in sections:
            # 提取section标题
            section_title_match = re.search(r"^##\s+(.+)$", section, re.MULTILINE)
            section_title = section_title_match.group(1).strip() if section_title_match else doc_title

            # 清理内容：移除标题行，合并空白
            lines = section.strip().split("\n")
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith("#") and not line.startswith("##"):
                    if not section_title_match:
                        continue
                cleaned_lines.append(line)

            chunk_text = "\n".join(cleaned_lines).strip()

            # 跳过太短的块
            if len(chunk_text) < 50:
                continue

            # 丰富块内容：添加文档标题作为上下文
            enriched_text = f"[{doc_title} - {section_title}] {chunk_text}"

            chunks.append(enriched_text)
            metadatas.append({
                "source": source_file,
                "city": city,
                "title": section_title,
                "doc_title": doc_title,
                "chunk_index": chunk_idx
            })
            ids.append(f"{source_file}_{chunk_idx}")
            chunk_idx += 1

        return chunks, metadatas, ids

    def _extract_city(self, source_file: str, content: str) -> str:
        """从文件名或内容中提取城市名"""
        city_map = {
            "beijing": "北京",
            "shanghai": "上海",
            "guangzhou": "广州",
            "shenzhen": "深圳",
            "chengdu": "成都",
            "hangzhou": "杭州",
            "xian": "西安",
        }
        # 从文件名提取
        file_stem = Path(source_file).stem.lower()
        for key, city_name in city_map.items():
            if key in file_stem:
                return city_name

        # 从内容第一行标题提取
        title_match = re.search(r"^#\s*(.+?)旅游", content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()

        return ""

    def query(
        self,
        query_text: str,
        city: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索知识库

        Args:
            query_text: 查询文本
            city: 可选的城市过滤
            top_k: 返回结果数量

        Returns:
            检索结果列表，每项包含 id, content, metadata, score
        """
        if not self._ensure_initialized():
            return []

        if self._collection.count() == 0:
            return []

        try:
            # 生成查询嵌入
            query_embedding = self.embed([query_text])
            if not query_embedding:
                return []

            # 构建过滤条件
            where_filter = None
            if city:
                where_filter = {"city": city}

            # 查询
            results = self._collection.query(
                query_embeddings=query_embedding,
                n_results=min(top_k, self._collection.count()),
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            # 格式化结果
            formatted = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    # ChromaDB使用距离，转换为相似度分数（cosine距离）
                    distance = results["distances"][0][i] if results["distances"] else 0
                    # 余弦相似度 = 1 - 余弦距离（对于归一化向量）
                    score = 1.0 - distance / 2.0  # 归一化到0-1范围

                    formatted.append({
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "score": round(score, 4)
                    })

            return formatted

        except Exception as e:
            print(f"[WARN]  知识库查询失败: {e}")
            return []

    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """添加单个文档到知识库

        Args:
            content: 文档内容（Markdown格式）
            metadata: 文档元数据

        Returns:
            文档ID，失败返回None
        """
        if not self._ensure_initialized():
            return None

        try:
            doc_id = f"manual_{self._collection.count() + 1}"

            # 生成嵌入
            embedding = self.embed([content])
            if not embedding:
                return None

            self._collection.add(
                ids=[doc_id],
                documents=[content],
                embeddings=embedding,
                metadatas=[metadata or {}]
            )

            print(f"[OK] 文档已添加: {doc_id}")
            return doc_id

        except Exception as e:
            print(f"[WARN]  添加文档失败: {e}")
            return None

    def delete_document(self, doc_id: str) -> bool:
        """删除知识库中的文档

        Args:
            doc_id: 文档ID

        Returns:
            是否成功
        """
        if not self._ensure_initialized():
            return False

        try:
            self._collection.delete(ids=[doc_id])
            print(f"[OK] 文档已删除: {doc_id}")
            return True
        except Exception as e:
            print(f"[WARN]  删除文档失败: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息

        Returns:
            统计信息字典
        """
        if not self._ensure_initialized():
            return {
                "status": "error",
                "error": self._init_error or "未初始化",
                "document_count": 0
            }

        try:
            count = self._collection.count()

            # 获取城市分布
            city_counts = {}
            if count > 0:
                # 获取所有元数据
                all_data = self._collection.get(include=["metadatas"])
                if all_data and all_data["metadatas"]:
                    for meta in all_data["metadatas"]:
                        city = meta.get("city", "通用")
                        city_counts[city] = city_counts.get(city, 0) + 1

            return {
                "status": "healthy",
                "document_count": count,
                "city_distribution": city_counts,
                "embedding_model": "tfidf-char-ngram"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "document_count": 0
            }


# 全局知识库服务实例
_knowledge_service: Optional[KnowledgeService] = None


def get_knowledge_service() -> KnowledgeService:
    """获取知识库服务实例（单例模式）"""
    global _knowledge_service

    if _knowledge_service is None:
        _knowledge_service = KnowledgeService()

    return _knowledge_service