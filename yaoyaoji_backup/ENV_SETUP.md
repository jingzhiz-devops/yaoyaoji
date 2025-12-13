# AI医生模块环境配置说明

## 🔐 安全配置完成

已将 DeepSeek API Key 从代码中移除，改为从环境变量获取，提高了安全性。

## 📝 修改内容

### 1. 删除硬编码的 API Key
- 文件：`yaoyaoji_backup/app/routers/ai_doctor.py`
- 已删除第 15-16 行的硬编码配置
- 代码现在完全依赖环境变量

### 2. 配置文件说明
- **`.env`**: 实际环境变量文件（已添加到 .gitignore，不会被提交）
- **`.env.example`**: 环境变量模板文件（可以提交到 Git）

### 3. .gitignore 更新
已添加 `.env` 相关文件到忽略列表，确保敏感信息不会被提交到 Git。

## 🚀 使用方法

### 首次部署
1. 复制环境变量模板：
   ```bash
   cd yaoyaoji_backup
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入真实的配置：
   ```bash
   # 修改 DeepSeek API Key
   DEEPSEEK_API_KEY=sk-your-actual-api-key-here
   
   # 修改数据库密码
   MYSQL_PASSWORD=your_actual_password
   
   # 修改 JWT Secret Key
   SECRET_KEY=your-actual-secret-key
   ```

### 获取 DeepSeek API Key
访问：https://platform.deepseek.com/api_keys

## ⚠️ 安全注意事项

1. **永远不要提交 `.env` 文件到 Git**
2. **不要在代码中硬编码任何密钥**
3. **定期更换 API Key**
4. **生产环境使用更强的 SECRET_KEY**

## 🔍 验证配置

启动应用前，确保 `.env` 文件存在并包含正确的配置：
```bash
cd yaoyaoji_backup
cat .env  # 检查配置文件
python -m app.main  # 启动应用
```

## 📦 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek AI 服务的 API 密钥 | `sk-xxxxx...` |
| `DEEPSEEK_BASE_URL` | DeepSeek API 基础地址 | `https://api.deepseek.com` |
| `DATABASE_URL` | 数据库连接字符串 | `mysql+pymysql://...` |
| `SECRET_KEY` | JWT 签名密钥 | 随机字符串 |
