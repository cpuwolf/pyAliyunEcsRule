# 阿里云 ECS 安全组规则自动更新工具

这个工具可以自动获取您当前的家庭公网 IP 地址，并将其更新到阿里云 ECS 安全组规则中作为源地址。

## 功能特性

- 自动获取当前公网 IP 地址（支持多个 IP 查询服务，提高可靠性）
- 自动更新阿里云 ECS 安全组规则
- 支持删除旧规则并添加新规则
- 使用阿里云 ECS V2.0 Python SDK

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或者直接安装：

```bash
pip install alibabacloud-ecs20140526 alibabacloud-tea-openapi alibabacloud-tea-util requests
```

### 2. 配置环境变量

在运行脚本之前，需要设置以下环境变量：

**Windows (CMD):**
```cmd
set ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
set ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

**Windows (PowerShell):**
```powershell
$env:ALIBABA_CLOUD_ACCESS_KEY_ID="your_access_key_id"
$env:ALIBABA_CLOUD_ACCESS_KEY_SECRET="your_access_key_secret"
```

**Linux/macOS:**
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

或者创建 `.env` 文件（需要安装 python-dotenv）：
```
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

## Docker 使用

### 构建镜像

```bash
docker build -t pyaliyun-ecs-rule .
```

### 运行容器

#### 使用环境变量参数

```bash
docker run --rm \
  -e ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id \
  -e ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret \
  pyaliyun-ecs-rule \
  --region-id cn-hangzhou \
  --security-group-id sg-xxxxxxxxxxxxx \
  --port-range 22/22
```

#### 使用环境变量文件

首先创建 `.env` 文件：
```
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

然后运行：
```bash
docker run --rm \
  --env-file .env \
  pyaliyun-ecs-rule \
  --region-id cn-hangzhou \
  --security-group-id sg-xxxxxxxxxxxxx \
  --port-range 22/22
```

#### 完整参数示例

```bash
docker run --rm \
  -e ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id \
  -e ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret \
  pyaliyun-ecs-rule \
  --region-id cn-hangzhou \
  --security-group-id sg-xxxxxxxxxxxxx \
  --ip-protocol tcp \
  --port-range 22/22 \
  --description "SSH access from home" \
  --endpoint ecs.cn-hangzhou.aliyuncs.com
```

## 使用方法

### 基本用法

```bash
python update_security_group.py \
    --region-id cn-hangzhou \
    --security-group-id sg-xxxxxxxxxxxxx \
    --port-range 22/22
```

### 完整参数示例

```bash
python update_security_group.py \
    --region-id cn-hangzhou \
    --security-group-id sg-xxxxxxxxxxxxx \
    --ip-protocol tcp \
    --port-range 22/22 \
    --description "SSH access from home" \
    --endpoint ecs.cn-hangzhou.aliyuncs.com
```

### 参数说明

- `--region-id` (必需): 阿里云区域 ID，例如 `cn-hangzhou`, `cn-beijing` 等
- `--security-group-id` (必需): 安全组 ID，格式如 `sg-xxxxxxxxxxxxx`
- `--port-range` (必需): 端口范围，例如 `22/22` (SSH), `80/80` (HTTP), `443/443` (HTTPS)
- `--ip-protocol` (可选): IP 协议，默认为 `tcp`，可选值: `tcp`, `udp`, `icmp`
- `--description` (可选): 规则描述，默认为 `Auto-updated from home IP`
- `--endpoint` (可选): 端点地址，如果不指定会根据 region-id 自动生成

### 使用示例

#### 更新 SSH 访问规则（端口 22）

```bash
python update_security_group.py \
    --region-id cn-hangzhou \
    --security-group-id sg-1234567890abcdef \
    --port-range 22/22 \
    --description "SSH access from home"
```

#### 更新 HTTP 访问规则（端口 80）

```bash
python update_security_group.py \
    --region-id cn-hangzhou \
    --security-group-id sg-1234567890abcdef \
    --port-range 80/80 \
    --description "HTTP access from home"
```

#### 更新 HTTPS 访问规则（端口 443）

```bash
python update_security_group.py \
    --region-id cn-hangzhou \
    --security-group-id sg-1234567890abcdef \
    --port-range 443/443 \
    --description "HTTPS access from home"
```

## 工作原理

1. **获取公网 IP**: 脚本会尝试从多个 IP 查询服务获取您的当前公网 IP 地址
2. **查询现有规则**: 查询安全组中匹配的现有规则
3. **删除旧规则**: 删除匹配的旧规则（如果有）
4. **添加新规则**: 使用新的 IP 地址添加安全组规则

## 注意事项

1. **权限要求**: 确保您的 AccessKey 具有修改安全组规则的权限。建议使用 RAM 用户并授予最小权限：
   - `AliyunECSFullAccess` 或
   - 自定义权限策略，包含 `ecs:AuthorizeSecurityGroup` 和 `ecs:RevokeSecurityGroup`

2. **安全建议**:
   - 不要将 AccessKey 硬编码在代码中
   - 使用环境变量或配置文件管理凭证
   - 定期轮换 AccessKey
   - 使用 RAM 用户而非主账号的 AccessKey

3. **IP 地址格式**: 脚本会自动将 IP 地址格式化为 CIDR 格式（例如 `1.2.3.4/32`）

4. **规则匹配**: 脚本会查找并删除与指定协议、端口范围和网络类型匹配的所有规则，然后添加新规则

## 故障排除

### 无法获取公网 IP

- 检查网络连接
- 确保可以访问外部 IP 查询服务

### 权限错误

- 检查 AccessKey 是否正确
- 确认 AccessKey 具有修改安全组的权限
- 检查安全组 ID 是否正确

### 区域错误

- 确认 region-id 参数正确
- 检查安全组是否属于指定的区域

## 许可证

本项目使用 GNU General Public License v3.0 许可证。

## 参考链接

- [阿里云 ECS Python SDK 文档](https://help.aliyun.com/zh/ecs/developer-reference/example-on-how-to-use-ecs-sdk-for-python)
- [阿里云 ECS API 参考](https://help.aliyun.com/document_detail/25484.html)



