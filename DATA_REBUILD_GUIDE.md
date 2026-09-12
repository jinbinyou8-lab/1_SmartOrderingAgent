# SmartOrderingAgent 数据重建与部署教程

这份教程用于在一台新电脑上重新创建本项目需要的数据，并启动完整系统。

推荐方式不是直接复制 MySQL、Redis、Milvus 的运行时文件，而是使用项目中的数据源和同步脚本重新构建：

1. 使用 `menu.sql` 初始化 MySQL。
2. 使用 `agent/redis_data_sync.py` 重建 FAQ Redis 数据。
3. 使用 `agent/milvus_data_sync.py` 重建 Milvus 菜品向量数据。
4. 启动 FastAPI 后端。
5. 启动 Vue 前端。


## 一、准备软件环境

请先确保电脑上安装了以下软件：

- Python 3.12
- Node.js 和 npm
- MySQL 8.x
- Redis
- Milvus

项目使用的主要端口：

| 服务 | 默认地址 |
| --- | --- |
| MySQL | `127.0.0.1:3306` |
| Redis | `localhost:6379` |
| Milvus | `http://127.0.0.1:19530` |
| FastAPI | `http://127.0.0.1:8000` |
| Vue 前端 | `http://localhost:3000` |


## 二、下载 Python 依赖

进入项目根目录：

```powershell
cd F:\SmartOrderingAgent
```

如果使用 `uv`：

```powershell
uv sync
```

如果不使用 `uv`，可以创建普通虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

后面的命令默认使用项目虚拟环境：

```text
F:\SmartOrderingAgent\.venv\Scripts\python.exe
```


## 三、准备环境变量

项目根目录中的 `.env` 保存运行配置。

不要把真实 `.env` 上传到 GitHub。建议仓库中只保留一个
`.env.example`，新电脑使用时复制成 `.env`：

```powershell
Copy-Item .env.example .env
```

`.env.example` 可以写成：

```env
# DeepSeek 配置
LLM_BASE_URL=
LLM_API_KEY=

# MySQL 配置
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=menu

# Milvus 配置
MILVUS_HOST=http://127.0.0.1:19530
MILVUS_TOKEN=

# Redis 配置
REDIS_URL=redis://localhost:6379/0
```

注意事项：

- `MYSQL_PASSWORD` 改成自己的 MySQL 密码。
- `LLM_API_KEY` 需要填写可用的 DeepSeek API Key。
- `MILVUS_TOKEN` 为空是否可用，取决于本地 Milvus 的认证配置。
- 不要把真实密码和 API Key 提交到 GitHub。


## 四、重建 MySQL 数据

### 1. 创建数据库

先登录 MySQL：

```powershell
mysql -h 127.0.0.1 -P 3306 -u root -p
```

创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS menu
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### 2. 导入项目 SQL

在 MySQL 命令行中执行：

```sql
source F:/SmartOrderingAgent/menu.sql;
```

也可以使用 Navicat、DataGrip 或 MySQL Workbench 打开 `menu.sql` 并执行。

导入完成后检查：

```sql
USE menu;

SHOW TABLES;

SELECT * FROM menu_items;

SELECT * FROM reservation_order;
```

应该能看到：

- `menu_items`：菜品表
- `reservation_order`：预订表
- `menu_items` 中有 5 条初始菜品

注意：`menu.sql` 目前包含菜品数据，但默认不包含现有预订记录。
如果需要保留预订记录，要使用后面的 MySQL 备份方法。


## 五、重建 Redis FAQ 数据

### 1. 启动 Redis

确认 Redis 正在运行：

```powershell
redis-cli ping
```

如果返回：

```text
PONG
```

说明 Redis 正常。

### 2. 执行 FAQ 同步脚本

```powershell
cd F:\SmartOrderingAgent
.\.venv\Scripts\python.exe .\agent\redis_data_sync.py
```

脚本会把 FAQ 写入 Redis：

```text
faq:items:address
faq:items:phone
faq:items:work_time
faq:all_items
```

其中每条 FAQ 使用 Hash 保存 `question` 和 `answer`，
`faq:all_items` 使用 Set 保存所有 FAQ key。

### 3. 检查 Redis 数据

```powershell
redis-cli SMEMBERS faq:all_items
redis-cli HGETALL faq:items:address
```

如果能看到问题和答案，说明 Redis 重建成功。


## 六、准备 BGE-M3 模型

Milvus 使用 `BAAI/bge-m3` 生成文本向量。

模型体积约为 4GB 以上，不建议上传到 GitHub 普通仓库。

推荐的目录是：

```text
F:\SmartOrderingAgent\models\bge-m3
```

可以使用 Hugging Face CLI 下载：

```powershell
huggingface-cli download BAAI/bge-m3 --local-dir F:\SmartOrderingAgent\models\bge-m3
```

如果没有 `huggingface-cli`，先安装：

```powershell
pip install huggingface_hub
```

也可以从 ModelScope 或其他可信来源下载相同模型，然后放到：

```text
F:\SmartOrderingAgent\models\bge-m3
```

注意：`agent/milvus_data_sync.py` 目前包含绝对路径：

```python
model=r"F:\SmartOrderingAgent\models\bge-m3"
```

如果项目放到其他目录，需要修改这个路径，或者改成基于项目根目录的方式。


## 七、重建 Milvus 数据

### 1. 启动 Milvus

确认 Milvus 服务已经启动，并能访问：

```text
http://127.0.0.1:19530
```

### 2. 同步菜单向量

```powershell
cd F:\SmartOrderingAgent
.\.venv\Scripts\python.exe .\agent\milvus_data_sync.py
```

脚本执行流程：

1. 从 MySQL 的 `menu_items` 表读取菜品。
2. 把每道菜转换成一段中文文本。
3. 使用 BGE-M3 生成 1024 维向量。
4. 如果已有 `menu_items` collection，会先删除。
5. 创建新的 `menu_items` collection。
6. 创建 HNSW + L2 向量索引。
7. 把向量和文本插入 Milvus。

注意：

- 该脚本每次执行都会删除并重建 collection。
- 重建前请确认 Milvus 中没有需要保留的额外数据。
- 只有 MySQL 菜品数据正确，Milvus 才能生成正确结果。


## 八、检查数据库服务

在执行这一步前，确认三个服务都能连接。

### MySQL

```powershell
mysql -h 127.0.0.1 -P 3306 -u root -p -e "SELECT COUNT(*) FROM menu.menu_items;"
```

### Redis

```powershell
redis-cli ping
redis-cli SCARD faq:all_items
```

### Milvus

可以通过项目中的搜索引擎进行验证：

```powershell
cd F:\SmartOrderingAgent
.\.venv\Scripts\python.exe -c "from agent.langchain_assitant import user_flavor_search; print(user_flavor_search('推荐不辣的菜'))"
```

如果返回菜品文本，说明 Milvus 向量检索正常。


## 九、启动 FastAPI 后端

从项目根目录启动：

```powershell
cd F:\SmartOrderingAgent
.\.venv\Scripts\python.exe run.py
```

也可以直接使用 Uvicorn：

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

启动成功后会看到类似：

```text
Uvicorn running on http://0.0.0.0:8000
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

应该能看到接口：

```text
POST /chat
GET  /faq/suggest
GET  /reservation/list
GET  /menu/list
```


## 十、启动 Vue 前端

打开另一个 PowerShell 窗口：

```powershell
cd F:\SmartOrderingAgent\ui
npm install
npm run dev
```

启动成功后，前端地址为：

```text
http://localhost:3000
```

前端通过 Vite 代理把 `/api` 请求转发到后端：

```text
http://127.0.0.1:8000
```


## 十一、启动后验证接口

### 1. 检查菜单接口

```powershell
Invoke-RestMethod http://127.0.0.1:8000/menu/list
```

应该返回菜品列表。

### 2. 检查 FAQ 接口

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/faq/suggest?query=地址&limit=2"
```

应该返回地址和营业时间等 FAQ 建议。

### 3. 检查预订列表

```powershell
Invoke-RestMethod http://127.0.0.1:8000/reservation/list
```

应该返回预订列表。

### 4. 检查 Agent 聊天

在浏览器中打开前端页面，输入：

```text
推荐几个不辣的菜
```

如果 DeepSeek、MCP、Milvus 和 MySQL 都配置正确，Agent 会调用工具并流式返回回答。


## 十二、如果需要保存当前真实数据

前面介绍的是推荐的重建方式。

如果你需要把当前 MySQL、Redis、Milvus 的精确状态一起备份，
可以按照下面的方式操作。

### 1. 备份 MySQL

```powershell
New-Item -ItemType Directory -Force F:\SmartOrderingAgent\data\mysql

mysqldump `
  -h 127.0.0.1 `
  -P 3306 `
  -u root `
  -p `
  --single-transaction `
  --routines `
  --triggers `
  --events `
  --databases menu `
  --result-file=F:\SmartOrderingAgent\data\mysql\menu_full.sql
```

恢复时导入 `menu_full.sql`。

### 2. 备份 Redis

```powershell
New-Item -ItemType Directory -Force F:\SmartOrderingAgent\data\redis

redis-cli SAVE
redis-cli --rdb F:\SmartOrderingAgent\data\redis\dump.rdb
```

恢复时需要把 `dump.rdb` 放回 Redis 配置的持久化目录，然后重启 Redis。

如果 FAQ 数据完全来自 `redis_data_sync.py`，则不需要备份 RDB。

### 3. 备份 Milvus

Milvus 的底层数据由 etcd、MinIO 等多个组件组成，
不建议直接复制容器目录。

精确备份建议使用官方 `milvus-backup` 工具备份 `menu_items`
collection。备份文件较大时，应上传到 GitHub Releases，而不是直接提交到仓库。

对于本项目，最简单的方式是：

```text
保留 MySQL 菜品数据
  -> 准备 BGE-M3 模型
  -> 重新运行 milvus_data_sync.py
```

### 4. 备份 SQLite Agent 记忆

`checkpoint.db` 保存 Agent 对话历史，可能包含个人数据。

一般不建议上传。如果需要备份，可以使用：

```powershell
New-Item -ItemType Directory -Force F:\SmartOrderingAgent\data\sqlite

sqlite3 F:\SmartOrderingAgent\checkpoint.db ".backup 'F:\SmartOrderingAgent\data\sqlite\checkpoint_backup.db'"
```


## 十三、打包上传到 GitHub

推荐仓库只包含：

```text
源代码
menu.sql
redis_data_sync.py
milvus_data_sync.py
.env.example
README.md
数据重建教程
```

建议在 `.gitignore` 中加入：

```gitignore
.env
.venv/
__pycache__/
*.pyc

ui/node_modules/
ui/dist/

models/

checkpoint.db
checkpoint.db-shm
checkpoint.db-wal

*.rdb
*.aof
```

尤其是 `models` 目录，当前体积超过 4GB，
上传到 GitHub 普通仓库会失败或造成仓库异常庞大。

如果确实需要打包数据，可以把小规模备份放到：

```text
data/
├─ mysql/
│  └─ menu_full.sql
├─ redis/
│  └─ dump.rdb
└─ sqlite/
   └─ checkpoint_backup.db
```

打包命令：

```powershell
Compress-Archive `
  -Path F:\SmartOrderingAgent\data\* `
  -DestinationPath F:\SmartOrderingAgent\smartorderingagent-data.zip
```

大小建议：

- 小于几十 MB：可以放进 GitHub 仓库。
- 较大：放到 GitHub Releases。
- 超过 100MB 的单个文件：不能直接上传到普通 GitHub 仓库。
- Milvus 大型备份和 BGE-M3 模型：优先使用 Releases 或 Git LFS。


## 十四、完整重建顺序

```text
1. 安装 Python、Node.js、MySQL、Redis、Milvus
2. 安装 Python 依赖
3. 创建 .env
4. 创建 menu 数据库
5. 导入 menu.sql
6. 启动 Redis
7. 执行 redis_data_sync.py
8. 下载 BGE-M3 到 models/bge-m3
9. 启动 Milvus
10. 执行 milvus_data_sync.py
11. 启动 run.py
12. 在 ui 目录执行 npm install
13. 执行 npm run dev
14. 访问 http://localhost:3000
```


## 十五、常见问题

### 1. 8000 端口被占用

检查占用进程：

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

找到 PID 后停止旧进程，再重新启动 `run.py`。

### 2. 找不到 agent 包

不要直接在错误的目录运行脚本。

推荐从项目根目录执行：

```powershell
cd F:\SmartOrderingAgent
.\.venv\Scripts\python.exe -m api.main
```

或者运行：

```powershell
.\.venv\Scripts\python.exe run.py
```

### 3. Redis 没有 FAQ

重新执行：

```powershell
.\.venv\Scripts\python.exe .\agent\redis_data_sync.py
```

然后检查：

```powershell
redis-cli SMEMBERS faq:all_items
```

### 4. Milvus 搜索没有结果

依次检查：

1. MySQL `menu_items` 是否有数据。
2. `models/bge-m3` 是否存在。
3. Milvus 是否启动。
4. `menu_items` collection 是否创建成功。
5. 是否重新运行了 `milvus_data_sync.py`。

### 5. Agent 不回复

检查：

1. DeepSeek API Key 是否有效。
2. `.env` 是否被正确加载。
3. 后端是否能访问外部 MCP 地址。
4. `checkpoint.db` 是否可写。
5. 查看后端控制台中的完整错误信息。


## 十六、最终建议

对于这个项目，最推荐的上传方式是：

```text
GitHub 仓库：
  只放代码、SQL、同步脚本、配置示例和教程

本地或 Releases：
  放 BGE-M3 模型、大型 Milvus 备份、Redis RDB、
  MySQL 大体量导出和 Agent 对话数据库
```

这样仓库不会过大，配置和隐私也更安全，其他人在新电脑上也能按照本教程重建完整环境。
