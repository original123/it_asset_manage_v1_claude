# IT 资产管理平台

## 快速开始

### 环境配置

1. **后端配置**
   ```bash
   cd backend
   cp .env.example .env
   # 编辑 .env 文件，修改敏感信息（SECRET_KEY、JWT_SECRET_KEY、数据库密码等）
   ```

2. **前端配置**
   ```bash
   cd frontend
   npm install
   ```

### 运行项目

**后端：**
```bash
cd backend
python run.py
```

**前端：**
```bash
cd frontend
npm run dev
```

## ⚠️ 安全提示

- **切勿**将 `.env` 文件提交到 Git
- **切勿**将敏感密钥上传到公共仓库
- 生产环境必须使用强密码和随机生成的密钥

## 项目结构

```
.
├── backend/          # Flask 后端
│   ├── app/         # 应用主目录
│   ├── .env.example # 环境变量模板
│   └── run.py       # 启动文件
└── frontend/        # Vue.js 前端
    └── src/         # 源代码
```
