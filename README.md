# 多智能体交互系统

这是一个基于Python实现的多智能体交互系统，支持不同功能的智能体之间通过网络进行交互，并包含注册发现模块。

## 系统架构

系统主要包含以下模块：

1. 智能体模块
   - 基础智能体（BaseAgent）
   - 搜索智能体（SearchAgent）
   - 论文智能体（PaperAgent）

2. 注册发现模块
   - 智能体注册
   - 心跳检测
   - 智能体发现

3. 网络通信模块
   - HTTP请求处理
   - 错误重试
   - 超时控制

4. 工具调用模块
   - 工具注册
   - 参数验证
   - 结果格式化

## 目录结构

```
multi_agent_system/
├── agents/                 # 智能体实现
│   ├── base/              # 基础类
│   ├── search/            # 搜索智能体
│   └── paper/             # 论文智能体
├── core/                  # 核心功能
│   ├── discovery/         # 注册发现
│   ├── network/          # 网络通信
│   └── tools/            # 工具调用
├── main.py               # 主程序
├── requirements.txt      # 依赖项
└── .env.example         # 环境变量示例
```

## 安装

1. 克隆项目：
```bash
git clone <repository_url>
cd multi_agent_system
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
```
编辑 `.env` 文件，填入必要的配置信息（如 Serper API 密钥）。

## 运行

启动系统：
```bash
python main.py
```

系统将启动以下服务：
- 发现服务：http://localhost:8000
- 搜索智能体：http://localhost:8001
- 论文智能体：http://localhost:8002

## API 接口

### 发现服务

- `POST /register` - 注册新智能体
- `DELETE /unregister/{agent_id}` - 注销智能体
- `PUT /heartbeat/{agent_id}` - 更新智能体心跳
- `GET /agents` - 获取所有活跃智能体
- `GET /agent/{agent_id}` - 获取特定智能体信息

### 搜索智能体

- `POST /message` - 处理消息
- `POST /query` - 执行搜索查询

### 论文智能体

- `POST /message` - 处理消息
- `POST /query` - 执行论文搜索

## 智能体通信

智能体之间通过消息传递进行通信。消息格式：

```json
{
  "sender_id": "agent-id",
  "content": "消息内容",
  "message_type": "消息类型",
  "metadata": {
    "额外信息": "值"
  }
}
```

## 工具使用

系统支持以下工具：

1. web_search - 网络搜索工具
   - 参数：query (搜索查询)

2. paper_search - 论文搜索工具
   - 参数：
     - query (搜索查询)
     - max_results (最大结果数，默认5)

## 注意事项

1. 确保所有必要的环境变量都已正确配置
2. 智能体需要定期发送心跳以保持活跃状态
3. 网络请求包含自动重试和超时机制
4. 工具调用前会进行参数验证

## 扩展开发

要添加新的智能体：

1. 在 `agents` 目录下创建新的智能体模块
2. 继承 `BaseAgent` 类
3. 实现必要的方法（handle_message, process_query）
4. 在 `main.py` 中添加新智能体的启动配置

## 许可证

MIT License
