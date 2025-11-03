# Railway 部署指南

## 项目概述
这是一个股票数据分析Web应用，包含龙虎榜、i问财、量化分析、韭研公社等多个功能模块。

## 部署前准备

### 1. 项目结构检查
确保项目包含以下关键文件：
- `src/app.py` - Flask应用主文件
- `requirements.txt` - Python依赖包列表
- `Procfile` - Railway启动配置
- `runtime.txt` - Python版本配置
- `railway.json` - Railway构建配置

### 2. 依赖检查
项目依赖的主要Python包：
- Flask 3.1.2
- Flask-SQLAlchemy 3.1.1
- requests 2.32.5
- pandas 2.3.3
- SQLite数据库

## Railway 部署步骤

### 第一步：创建Railway账户
1. 访问 [Railway官网](https://railway.app)
2. 使用GitHub账户注册
3. 完成账户验证

### 第二步：连接GitHub仓库
1. 在Railway控制台点击"New Project"
2. 选择"Deploy from GitHub repo"
3. 授权Railway访问你的GitHub账户
4. 选择包含本项目的仓库

### 第三步：自动部署
1. Railway会自动检测项目类型（Python）
2. 根据`railway.json`配置进行构建
3. 自动安装依赖包
4. 启动应用服务

### 第四步：环境变量配置（可选）
如果需要自定义配置，可以在Railway项目设置中添加环境变量：
- `DEBUG`: 设置为`False`（生产环境）
- `HOST`: 默认为`0.0.0.0`
- `PORT`: Railway自动分配

## 部署后访问

### 获取访问地址
1. 部署完成后，Railway会提供一个唯一的访问域名
2. 格式通常为：`https://your-project-name.up.railway.app`

### 首次访问
1. 访问提供的域名
2. 应用会自动创建SQLite数据库
3. 可以正常使用所有功能

## 数据管理

### 数据导入
1. 访问 `https://your-domain/import_today_data` 导入最新数据
2. 或访问各功能页面的数据导入链接

### 数据库位置
- 生产环境：SQLite数据库位于 `/tmp/stock.db`
- 本地开发：SQLite数据库位于 `stock.db`

## 故障排除

### 常见问题

#### 1. 部署失败
- 检查`requirements.txt`格式是否正确
- 确认Python版本兼容性（当前配置为3.11.0）
- 查看Railway构建日志中的错误信息

#### 2. 应用无法启动
- 检查`Procfile`中的启动命令
- 确认端口配置正确
- 查看应用日志排查错误

#### 3. 数据库问题
- 确认SQLite数据库文件权限
- 检查数据库连接字符串

#### 4. 静态资源加载失败
- 确认模板文件路径正确
- 检查静态文件引用路径

### 日志查看
在Railway控制台可以查看：
- 构建日志（Build Logs）
- 部署日志（Deploy Logs）
- 应用日志（Application Logs）

## 维护和更新

### 代码更新
1. 推送代码到GitHub主分支
2. Railway会自动检测并重新部署
3. 部署过程通常需要1-3分钟

### 数据备份
- 定期导出重要数据
- Railway提供数据库备份功能（付费版）
- 建议定期下载数据备份

## 免费额度说明

Railway提供每月5美元的免费额度，包括：
- 计算资源：512MB内存
- 存储空间：1GB磁盘空间
- 网络流量：不限
- 部署数量：不限

对于中小型应用，免费额度通常足够使用。

## 国内访问优化

### 网络性能
- Railway使用全球CDN加速
- 国内访问延迟相对较低
- 建议使用Chrome或Edge浏览器

### 替代方案
如果Railway在国内访问不理想，可以考虑：
1. Netlify（国内CDN优化）
2. 腾讯云CloudBase（国内服务器）
3. 阿里云函数计算

## 安全建议

### 生产环境安全
1. 设置`DEBUG=False`
2. 避免暴露敏感信息
3. 定期更新依赖包
4. 监控应用日志

### 数据安全
1. 不要在生产环境存储敏感数据
2. 定期备份重要数据
3. 使用环境变量存储配置信息

## 联系方式

如有部署问题，请查看：
- Railway官方文档：https://docs.railway.app
- 项目GitHub仓库Issues
- 应用日志中的错误信息

---
*最后更新：2024年*