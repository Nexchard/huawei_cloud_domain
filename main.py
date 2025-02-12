import logging
import os
from src.notification import WeworkNotification
from src.email_notification import EmailNotification
from src.logger import logger
from dotenv import load_dotenv
from src.yunzhijia_notification import YunzhijiaNotification
from src.domain_query import DomainQuery, format_domain_data
from src.db import Database
from datetime import datetime

# 加载环境变量
load_dotenv()

def main():
    # 检查是否启用数据库
    enable_database = os.getenv('ENABLE_DATABASE', 'false').lower() == 'true'
    
    if enable_database:
        db = Database()
        logger.info("数据库功能已启用")
    else:
        db = None
        logger.info("数据库功能未启用")
    
    # 初始化通知系统
    wework = WeworkNotification()
    email = EmailNotification()
    yunzhijia = YunzhijiaNotification()
    
    # 记录通知系统状态
    logger.info(f"企业微信通知状态: {'启用' if wework.enabled else '未启用'}")
    logger.info(f"邮件通知状态: {'启用' if email.enabled else '未启用'}")
    logger.info(f"云之家通知状态: {'启用' if yunzhijia.enabled else '未启用'}")
    
    # 获取所有华为云账号配置
    accounts = []
    index = 1
    while True:
        account_name = os.getenv(f'ACCOUNT{index}_NAME')
        domain_name = os.getenv(f'ACCOUNT{index}_DOMAIN_NAME')
        username = os.getenv(f'ACCOUNT{index}_USERNAME')
        password = os.getenv(f'ACCOUNT{index}_PASSWORD')
        
        if not domain_name or not username or not password:
            break
        
        # 如果没有配置ACCOUNT{index}_NAME，则使用domain_name作为默认值
        if not account_name:
            account_name = domain_name
        
        accounts.append({
            "account_name": account_name,
            "domain_name": domain_name,
            "username": username,
            "password": password
        })
        index += 1
    
    logger.info(f"共发现 {len(accounts)} 个华为云账号配置")
    
    # 生成批次号
    batch_number = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # 存储所有账号的域名数据
    all_account_domains = []
    
    # 查询每个账号的域名信息
    for account in accounts:
        account_name = account["account_name"]
        domain_name = account["domain_name"]
        username = account["username"]
        password = account["password"]
        
        logger.info(f"开始查询账号 {account_name} 的域名信息")
        
        # 初始化域名查询客户端
        domain_client = DomainQuery(domain_name, username, password)
        
        # 查询域名信息
        domain_result = domain_client.get_all_domains()
        
        if domain_result["success"]:
            domains = domain_result["data"]["domains"]
            logger.info(f"账号 {account_name} 查询到 {len(domains)} 个域名")
            
            # 保存到数据库
            if db:
                logger.info(f"开始保存账号 {account_name} 的域名数据到数据库...")
                success_count = 0
                total_count = len(domains)
                valid_count = 0
                for domain in domains:
                    formatted_domain = format_domain_data(domain, account_name, domain_name)
                    # 只处理未过期的域名
                    if formatted_domain:
                        valid_count += 1
                        if db.save_resource(formatted_domain, batch_number):
                            success_count += 1
                        else:
                            logger.error(f"保存域名数据失败: {account_name} - {domain.get('domain_name', '')}")
                logger.info(f"账号 {account_name} 的域名数据保存完成，成功：{success_count}/{valid_count}（总域名数：{total_count}）")
            
            # 收集账号数据用于通知
            valid_domains = []
            for domain in domains:
                formatted_domain = format_domain_data(domain, account_name, domain_name)
                if formatted_domain:  # 只收集未过期的域名
                    valid_domains.append(domain)
            
            if valid_domains:  # 只有当有未过期的域名时才添加到通知列表
                all_account_domains.append({
                    "account_name": account_name,
                    "domains": valid_domains
                })
        else:
            logger.error(f"查询账号 {account_name} 域名失败: {domain_result.get('message', '未知错误')}")
    
    # 发送通知
    if all_account_domains:
        if wework.enabled:
            logger.info("开始发送企业微信域名通知...")
            wework.send_domain_notification(all_account_domains)
        
        if email.enabled:
            logger.info("开始发送邮件域名通知...")
            email_content = email.format_domain_message(all_account_domains)
            if email_content:
                if email.send_email(None, email_content):
                    logger.info("邮件域名通知发送成功")
                else:
                    logger.error("邮件域名通知发送失败")
        
        if yunzhijia.enabled:
            logger.info("开始发送云之家域名通知...")
            yunzhijia.send_domain_notification(all_account_domains)
    
    # 关闭数据库连接
    if db:
        db.close()

if __name__ == "__main__":
    main() 