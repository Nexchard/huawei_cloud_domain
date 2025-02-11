# 华为云域名到期监控系统

## 项目简介
该系统用于监控多个华为云账号下的域名到期情况，通过多种通知渠道（企业微信、云之家、邮件）及时提醒域名即将到期，帮助企业有效管理域名资产，避免因域名到期造成的业务中断。

## 主要功能
- **多账号管理**：支持同时监控多个华为云账号下的域名
- **多渠道通知**：
  - 企业微信机器人通知
  - 云之家机器人通知
  - 邮件通知（支持HTML格式）
- **灵活的告警规则**：
  - 可配置告警提醒天数
  - 分级告警（紧急、警告、提醒）
  - 按账号分组展示
- **数据持久化**：
  - 支持将域名信息保存到MySQL数据库
  - 记录批次号便于追踪
  - 支持历史记录查询

## 系统要求
- Python 3.8+
- MySQL 5.7+ (可选，如需启用数据库功能)

## 安装部署

### 1. 克隆代码
```bash
git clone [repository_url]
cd huawei_cloud_domain
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制 `.env.example` 到 `.env` 并配置以下信息：

#### 华为云账户配置（支持多账号）
```ini
# 账号1配置
ACCOUNT1_DOMAIN_NAME=your_domain_name_1  # IAM用户所属账号名
ACCOUNT1_USERNAME=your_username_1        # IAM用户名
ACCOUNT1_PASSWORD=your_password_1        # IAM用户密码

# 账号2配置（如需）
ACCOUNT2_DOMAIN_NAME=your_domain_name_2
ACCOUNT2_USERNAME=your_username_2
ACCOUNT2_PASSWORD=your_password_2
```

#### 通知渠道配置

##### 企业微信配置
```ini
WEWORK_ENABLED=true
WEWORK_SEND_TO_ALL=false
WEWORK_DEFAULT_BOT=default_bot_name

# 机器人1配置
WECHAT_BOT1_NAME=your_bot_name_1
WECHAT_BOT1_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key_1
WEWORK_BOT1_ENABLED=true
```

##### 云之家配置
```ini
YUNZHIJIA_ENABLED=true
YUNZHIJIA_SEND_TO_ALL=false
YUNZHIJIA_DEFAULT_BOT=your_bot_name

# 机器人1配置
YUNZHIJIA_BOT1_NAME=your_bot_name_1
YUNZHIJIA_BOT1_WEBHOOK=https://www.yunzhijia.com/gateway/robot/webhook/send?yzjtype=0&yzjtoken=your_token_1
YUNZHIJIA_BOT1_ENABLED=true
```

##### 邮件配置
```ini
SMTP_ENABLED=true
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_email_password
SMTP_FROM=your_email@example.com
SMTP_TO=recipient1@example.com,recipient2@example.com
```

#### 数据库配置（可选）
```ini
ENABLE_DATABASE=true
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=huaweicloud_monitor
```

#### 告警规则配置
```ini
# 设置资源到期前多少天开始告警
RESOURCE_ALERT_DAYS=65
```

## 运行方式

### 直接运行
```bash
python main.py
```

### 定时任务（推荐）
建议通过crontab设置定时任务，例如每天早上9点执行：
```bash
0 9 * * * cd /path/to/huawei_cloud_domain && python main.py
```

## 告警规则说明
系统对域名到期时间进行分级告警：
- **紧急** (🚨)：剩余天数 ≤ 15天
- **警告** (⚠️)：剩余天数 ≤ 30天
- **提醒** (ℹ️)：剩余天数 ≤ 65天（可配置）

## 通知样式示例

### 企业微信通知
```markdown
# 华为云域名到期提醒

## ⚠️ 以下域名即将到期（剩余天数 <= 65天）：

### 账号: account1
- 🚨 **example1.com**
  - 到期时间: 2024-02-01
  - 剩余天数: 10天

- ⚠️ **example2.com**
  - 到期时间: 2024-02-15
  - 剩余天数: 25天
```

### 邮件通知
- HTML格式，包含样式
- 支持颜色标识不同级别
- 自动生成附件便于保存

### 云之家通知
```text
华为云域名到期提醒

以下域名即将到期（剩余天数 <= 65天）：

=== 账号: account1 ===
[紧急] example1.com
到期时间: 2024-02-01
剩余天数: 10天

[警告] example2.com
到期时间: 2024-02-15
剩余天数: 25天
```

## 数据库结构
如果启用数据库功能，系统会自动创建所需的表结构：

```sql
CREATE TABLE IF NOT EXISTS domains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(255) NOT NULL,
    domain_name VARCHAR(255) NOT NULL,
    expire_date DATETIME,
    remaining_days INT,
    update_time DATETIME,
    batch_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_domain (account_name, domain_name, batch_number)
);
```

## 常见问题

### 1. 通知失败
- 检查对应通知渠道的配置是否正确
- 验证Webhook地址的有效性
- 确认机器人是否被禁用

### 2. 域名查询失败
- 验证华为云账号信息是否正确
- 检查账号是否有足够的权限
- 查看日志文件了解详细错误信息

### 3. 数据库操作失败
- 确认数据库服务是否正常运行
- 验证数据库连接信息是否正确
- 检查用户权限是否足够

## 日志说明
- 日志文件位于 `logs` 目录
- 按天生成日志文件
- 记录详细的运行信息和错误信息

## 项目结构
```
huawei_cloud_domain/
├── main.py                 # 主程序入口
├── .env                    # 环境变量配置文件
├── .env.example           # 环境变量配置示例
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明文档
├── sql/                  # SQL文件目录
│   └── create_domains_table.sql  # 域名表结构
└── src/                  # 源代码目录
    ├── config.py         # 配置管理
    ├── db.py            # 数据库操作
    ├── logger.py        # 日志管理
    ├── domain_query.py  # 域名查询
    ├── notification.py  # 企业微信通知
    ├── email_notification.py     # 邮件通知
    └── yunzhijia_notification.py # 云之家通知
```

## 维护者
[维护者信息]

## 许可证
[许可证信息] 