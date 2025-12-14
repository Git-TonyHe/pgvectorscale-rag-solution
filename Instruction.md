# Pgvectorscale RAG 解决方案使用指南

## 项目概述

这是一个基于PostgreSQL + pgvectorscale构建的高性能RAG（检索增强生成）解决方案。项目使用Infini-AI的bge-m3模型生成嵌入向量，结合Timescale Vector进行高效向量搜索，并利用DeepSeek-V3模型生成智能回答。

### 技术栈
- **向量数据库**: PostgreSQL + pgvectorscale + Timescale Vector
- **嵌入模型**: Infini-AI bge-m3 (1024维)
- **LLM模型**: Infini-AI DeepSeek-V3
- **编程语言**: Python 3.7+
- **容器化**: Docker + Docker Compose

## 快速开始

### 1. 环境准备

**前提条件：**
- Docker（用于运行TimescaleDB）
- Python 3.7+
- Infini-AI API密钥（从 https://cloud.infini-ai.com 注册获取）
- PostgreSQL客户端（可选，如TablePlus、DBeaver或psql CLI）

### 2. 启动数据库服务

```bash
# 进入项目目录
cd /Users/tonyhe/py_vector/pgvectorscale-rag-solution

# 启动TimescaleDB容器
docker-compose -f docker/docker-compose.yml up -d
```

### 3. 配置环境变量

检查并配置 `app/.env` 文件：

```env
INFINI_BASE_URL =https://cloud.infini-ai.com/maas/v1
INFINI_API_KEY=your_infini_ai_api_key_here
TIMESCALE_SERVICE_URL=postgresql://postgres:password@127.0.0.1:5432/postgres
```

**重要提示：**
- 使用 `127.0.0.1` 而不是 `localhost` 以避免连接问题
- 确保API密钥正确无误

### 4. 安装Python依赖

```bash
# 创建虚拟环境（如果尚未创建）
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 5. 插入向量数据

```bash
python app/insert_vectors.py
```

这个脚本会执行以下操作：
1. 从 `data/faq_dataset.csv` 加载FAQ数据（包含20个常见问题）
2. 使用bge-m3模型生成1024维的嵌入向量
3. 创建数据库表和索引（DiskANN索引）
4. 将向量数据插入PostgreSQL

### 6. 运行相似性搜索演示

```bash
python app/similarity_search.py
```

这个演示脚本展示了：
- 基本相似性搜索
- 元数据过滤（按类别筛选）
- 时间范围过滤
- LLM驱动的响应生成

## 项目结构详解

```
pgvectorscale-rag-solution/
├── app/                    # 应用程序代码
│   ├── config/
│   │   └── settings.py     # 配置管理，环境变量加载
│   ├── database/
│   │   ├── connect_postgres.py  # 数据库连接工具
│   │   └── vector_store.py      # 向量存储操作（核心）
│   ├── services/
│   │   ├── llm_factory.py       # LLM客户端工厂
│   │   └── synthesizer.py       # 响应合成器
│   ├── insert_vectors.py        # 数据插入脚本
│   ├── similarity_search.py     # 搜索演示脚本
│   └── .env                    # 环境变量配置
├── data/
│   └── faq_dataset.csv         # 示例FAQ数据集（分号分隔）
├── docker/
│   └── docker-compose.yml      # Docker配置（TimescaleDB）
├── requirements.txt            # Python依赖包列表
├── README.md                   # 项目原始文档
├── LICENCE                     # MIT许可证
└── .gitignore                  # Git忽略文件
```

## 核心功能

### 1. 高性能向量搜索
- 使用Timescale Vector的DiskANN索引进行快速近似最近邻搜索
- 支持余弦相似度计算（使用 `<=>` 操作符）
- 优化的查询性能，适合大规模向量数据集

### 2. 混合搜索能力
- **元数据过滤**：按类别、标签等属性筛选
- **时间范围过滤**：按创建时间筛选数据
- **组合查询**：支持AND/OR逻辑操作

### 3. 智能响应生成
- 结合检索到的上下文生成自然语言回答
- 使用DeepSeek-V3模型进行内容合成
- 提供思考过程透明化（显示推理步骤）

### 4. 可扩展架构
- 模块化设计，易于扩展和定制
- 支持自定义嵌入模型和LLM模型
- 灵活的数据库配置

## 详细使用示例

### 基本搜索

```python
from app.database.vector_store import VectorStore

# 初始化向量存储
vec = VectorStore()

# 执行相似性搜索
results = vec.search("What are your shipping options?", limit=3)

# 查看结果
for result in results:
    print(f"距离: {result['distance']:.4f}")
    print(f"内容: {result['contents']}")
    print(f"元数据: {result['metadata']}")
    print("-" * 50)
```

### 元数据过滤

```python
# 按类别过滤
metadata_filter = {"category": "Shipping"}
results = vec.search("shipping", limit=3, metadata_filter=metadata_filter)
```

### 时间范围过滤

```python
from datetime import datetime

# 搜索特定时间范围内的数据
time_range = (datetime(2024, 9, 1), datetime(2024, 9, 30))
results = vec.search("customer service", limit=3, time_range=time_range)
```

### 完整RAG流程

```python
from app.database.vector_store import VectorStore
from app.services.synthesizer import Synthesizer

# 初始化
vec = VectorStore()
synthesizer = Synthesizer()

# 1. 检索相关上下文
question = "How can I track my order?"
contexts = vec.search(question, limit=5)

# 2. 生成智能回答
response = synthesizer.generate_response(
    question=question,
    context=contexts
)

# 3. 输出结果
print(f"问题: {question}")
print(f"回答: {response.answer}")
print(f"是否有足够上下文: {response.enough_context}")
print("思考过程:")
for thought in response.thought_process:
    print(f"  - {thought}")
```

## 使用自定义数据

### 1. 准备数据文件

创建CSV文件，格式参考 `data/faq_dataset.csv`：

```csv
question;answer;category
你的问题1;答案1;类别1
你的问题2;答案2;类别2
```

### 2. 修改插入脚本

编辑 `app/insert_vectors.py` 中的数据处理逻辑：

```python
# 修改文件路径
df = pd.read_csv("your_data.csv", sep=";")

# 自定义内容格式
def prepare_record(row):
    content = f"问题: {row['question']}\n答案: {row['answer']}"
    # ... 其他处理逻辑
```

### 3. 运行插入

```bash
python app/insert_vectors.py
```

## 故障排除指南

### 常见问题

#### 1. 数据库连接失败
**症状**: 连接超时或拒绝连接
**解决方案**:
- 使用 `127.0.0.1` 而不是 `localhost`
- 检查Docker容器是否运行：`docker ps`
- 验证端口5432是否被占用

#### 2. API密钥错误
**症状**: Infini-AI API调用失败
**解决方案**:
- 确认API密钥正确
- 检查 `INFINI_BASE_URL` 配置
- 验证账户是否有足够额度

#### 3. 向量维度不匹配
**症状**: "vector dimension mismatch" 错误
**解决方案**:
- bge-m3模型使用1024维，不是1536维
- 更新配置：`EMBEDDING_DIMENSIONS=1024`

#### 4. Predicates功能错误
**症状**: `TypeError: Subscripted generics cannot be used with class and instance checks`
**解决方案**:
- 这是 `timescale_vector` v0.0.7在Python 3.9下的bug
- 使用 `metadata_filter` 替代 `Predicates`

### 调试技巧

1. **测试数据库连接**:
   ```bash
   python app/database/connect_postgres.py
   ```

2. **检查环境变量**:
   ```python
   from app.config.settings import get_settings
   settings = get_settings()
   print(settings.openai.api_key)  # 检查API密钥
   ```

3. **查看日志**:
   ```bash
   # 查看Docker容器日志
   docker logs timescaledb
   ```

## 性能优化

### 索引策略

对于大规模数据集（10k+向量），建议创建索引：

```python
# 在 vector_store.py 中
def create_index(self):
    """创建DiskANN索引加速搜索"""
    # 现有实现已包含
```

### 批量操作

对于大量数据插入，使用批量操作：

```python
# 分批插入数据
batch_size = 100
for i in range(0, len(records_df), batch_size):
    batch = records_df[i:i+batch_size]
    vec.upsert(batch)
```

### 查询优化

- 合理设置 `limit` 参数，避免返回过多结果
- 使用元数据过滤减少搜索空间
- 对常用查询条件创建索引

## 扩展开发

### 添加新功能

1. **支持其他嵌入模型**:
   - 修改 `app/services/llm_factory.py`
   - 实现新的嵌入生成器

2. **集成其他LLM**:
   - 扩展 `Synthesizer` 类
   - 添加新的模型配置

3. **自定义检索策略**:
   - 修改 `VectorStore.search()` 方法
   - 实现混合检索算法

### API开发

将RAG系统封装为REST API：

```python
from fastapi import FastAPI
from app.database.vector_store import VectorStore
from app.services.synthesizer import Synthesizer

app = FastAPI()
vec = VectorStore()
synthesizer = Synthesizer()

@app.post("/query")
async def query_rag(question: str):
    contexts = vec.search(question, limit=5)
    response = synthesizer.generate_response(question, contexts)
    return response.dict()
```

## 最佳实践

### 1. 环境管理
- 使用虚拟环境隔离依赖
- 将敏感信息存储在 `.env` 文件中
- 不要将 `.env` 文件提交到版本控制

### 2. 数据质量
- 确保训练数据清洁、准确
- 定期更新向量索引
- 监控搜索质量指标

### 3. 性能监控
- 记录查询响应时间
- 监控API使用情况
- 定期优化数据库性能

### 4. 安全考虑
- 保护API密钥和数据库凭证
- 实施查询频率限制
- 验证用户输入

## 资源链接

### 官方文档
- [Pgvectorscale GitHub](https://github.com/timescale/pgvectorscale)
- [Timescale Vector文档](https://www.timescale.com/products/vector)
- [Infini-AI平台](https://cloud.infini-ai.com)

### 学习资源
- [YouTube教程](https://youtu.be/hAdEuDBN57g)
- [RAG最佳实践指南](https://www.timescale.com/blog/rag-is-more-than-just-vector-search/)
- [向量数据库比较](https://www.timescale.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost/)

### 社区支持
- [Timescale社区论坛](https://www.timescale.com/community)
- [GitHub Issues](https://github.com/daveebbelaar/pgvectorscale-rag-solution/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/pgvectorscale)

## 许可证

本项目基于MIT许可证开源。详见 [LICENCE](LICENCE) 文件。

---

*最后更新: 2025年12月13日*  
*文档版本: 1.0*  
*项目版本: 基于 commit 1a599d29f15c196fb51d89b06fd68de9b4084836*

如需进一步帮助或有任何问题，请参考原始 [README.md](README.md) 或提交GitHub Issue。
