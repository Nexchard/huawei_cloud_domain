-- 创建域名信息表
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

-- 添加唯一索引，防止重复数据
ALTER TABLE domains ADD UNIQUE INDEX uniq_domain_batch (account_name, resource_name, batch_number);

-- 添加索引优化查询性能
ALTER TABLE domains ADD INDEX idx_expire_time (expire_time);
ALTER TABLE domains ADD INDEX idx_remaining_days (remaining_days);

-- 添加表注释
ALTER TABLE domains COMMENT '华为云域名到期监控表';

-- 初始化说明
/*
此表用于存储华为云域名到期信息，主要字段说明：
- account_name: 华为云账号名称
- resource_name: 域名
- resource_id: 域名（作为资源ID）
- service_type: 固定为'domain'
- region: 固定为'global'
- expire_time: 域名到期时间
- project_name: 项目名称
- remaining_days: 距离到期剩余天数
- batch_number: 数据批次号，格式为：yyyyMMddHHmmss

重要索引说明：
1. 主键索引：id
2. 唯一索引：account_name + resource_name + batch_number
3. 普通索引：
   - idx_account_resource：用于按账号和域名查询
   - idx_batch：用于按批次查询
   - idx_expire_time：用于按到期时间查询
   - idx_remaining_days：用于按剩余天数查询
*/ 