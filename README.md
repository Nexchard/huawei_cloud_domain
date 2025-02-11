# 华为云域名到期监控系统

## 项目简介
该系统用于监控多个华为云账号下的域名到期情况，通过企业微信机器人、云之家机器人和邮件三种通知方式及时提醒域名即将到期，帮助企业有效管理域名资产，避免因域名到期造成的业务中断。

## 主要功能
- **多账号管理**：支持同时监控多个华为云账号下的域名
- **多级告警**：
  - 紧急告警 (🚨)：剩余天数 ≤ 15天
  - 警告提醒 (⚠️)：剩余天数 ≤ 30天
  - 普通提醒 (ℹ️)：剩余天数 ≤ 自定义天数
- **多渠道通知**：
  - 企业微信机器人（支持Markdown格式）
  - 云之家机器人（纯文本格式）
  - 邮件通知（HTML格式，自动生成附件）
- **数据持久化**：
  - 支持MySQL数据库存储
  - 记录批次号便于追踪
  - 自动更新域名到期信息

## 系统要求
- Python 3.8+
- MySQL 5.7+ (可选，如需启用数据库功能)

## 安装部署

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
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
# 设置域名到期前多少天开始告警
RESOURCE_ALERT_DAYS=65
```

## 通知样式示例

### 企业微信通知
```markdown
# 华为云域名到期提醒

### 账号: account1
- 🚨 **example1.com**
  - 到期时间: 2024-02-01
  - 剩余天数: 10天

- ⚠️ **example2.com**
  - 到期时间: 2024-02-15
  - 剩余天数: 25天
```

### 云之家通知
```text
华为云域名到期提醒
=== 账号: account1 ===
[紧急] example1.com
到期时间: 2024-02-01
剩余天数: 10天

[警告] example2.com
到期时间: 2024-02-15
剩余天数: 25天
```

### 邮件通知
- 主题：华为云域名到期提醒 (2024-02-11)
- 内容：HTML格式，包含样式
- 自动生成同名附件

## 数据库表结构
```sql
CREATE TABLE IF NOT EXISTS domains (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_name VARCHAR(255) NOT NULL COMMENT '账号名称',
    resource_name VARCHAR(255) NOT NULL COMMENT '资源名称',
    resource_id VARCHAR(255) NOT NULL COMMENT '资源ID',
    service_type VARCHAR(50) COMMENT '服务类型',
    region VARCHAR(50) COMMENT '区域',
    expire_time DATETIME COMMENT '到期时间',
    project_name VARCHAR(255) COMMENT '项目名称',
    remaining_days INT COMMENT '剩余天数',
    batch_number VARCHAR(50) COMMENT '批次号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_account_resource (account_name, resource_name),
    INDEX idx_batch (batch_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='域名信息表';
```

## 运行方式

### 直接运行
```bash
python main.py
```

### 定时任务（推荐）
建议通过crontab设置定时任务，例如每天早上9点执行：
```bash
0 9 * * * cd /path/to/project && python main.py
```

## 日志说明
- 日志文件位于 `logs` 目录
- 按天生成日志文件
- 记录域名查询、数据保存和通知发送的详细信息

## 常见问题

### 1. 域名查询失败
- 检查华为云账号信息是否正确
- 确认IAM用户权限是否足够
- 查看日志了解具体错误信息

### 2. 通知发送失败
- 检查对应通知渠道的配置是否正确
- 验证机器人Webhook地址的有效性
- 确认SMTP服务器配置是否正确

### 3. 数据库操作失败
- 确认数据库服务是否正常运行
- 验证数据库连接信息是否正确
- 检查用户权限是否足够

## 项目结构
```
project/
├── main.py                 # 主程序入口
├── .env                    # 环境变量配置文件
├── .env.example           # 环境变量配置示例
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明文档
└── src/                  # 源代码目录
    ├── config.py         # 配置管理
    ├── db.py            # 数据库操作
    ├── logger.py        # 日志管理
    ├── domain_query.py  # 域名查询
    ├── notification.py  # 企业微信通知
    ├── email_notification.py     # 邮件通知
    └── yunzhijia_notification.py # 云之家通知
``` 