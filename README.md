# SmartOrderingAgent

智能餐厅助手 Demo，包含 Vue 前端、FastAPI 后端、LangChain Agent、
MySQL、Redis 和 Milvus。

## 功能

- 智能聊天和餐厅业务工具调用
- FAQ 快速问答推荐
- 菜品列表和特色菜查询
- 预订创建和预订列表
- 基于 BGE-M3 和 Milvus 的菜品语义搜索

## 项目文档

- [项目结构与调用流程](PROJECT_OVERVIEW.txt)
- [数据重建与部署教程](DATA_REBUILD_GUIDE.md)

## 快速启动

1. 安装 Python、Node.js、MySQL、Redis 和 Milvus。
2. 根据 `.env.example` 创建和配置 `.env`。
3. 导入 `menu.sql` 初始化 MySQL。
4. 运行 `agent/redis_data_sync.py` 重建 Redis FAQ。
5. 下载 BGE-M3 到 `models/bge-m3`。
6. 运行 `agent/milvus_data_sync.py` 重建 Milvus 菜单向量。
7. 启动后端：

   ```powershell
   .\.venv\Scripts\python.exe run.py
   ```

8. 启动前端：

   ```powershell
   cd ui
   npm install
   npm run dev
   ```

9. 访问 `http://localhost:3000`。

详细步骤请阅读 [DATA_REBUILD_GUIDE.md](DATA_REBUILD_GUIDE.md)。
