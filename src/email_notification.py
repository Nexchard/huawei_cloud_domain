import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()

class EmailNotification:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', '465'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_from = os.getenv('SMTP_FROM')
        self.smtp_to = os.getenv('SMTP_TO', '').split(',')
        self.enabled = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
        self.alert_days = int(os.getenv('RESOURCE_ALERT_DAYS', '65'))

    def format_all_accounts_message(self, accounts_data):
        """格式化所有账号的资源、余额和账单信息为HTML邮件内容"""
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #1a73e8;
                    border-bottom: 2px solid #1a73e8;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #202124;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #1a73e8;
                    margin-top: 20px;
                }}
                .account {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .balance {{
                    background: #e8f0fe;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }}
                .stored-card {{
                    background: white;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 4px;
                    border-left: 4px solid #4caf50;
                }}
                .balance h3 {{
                    margin-top: 0;
                }}
                .service {{
                    margin-bottom: 20px;
                }}
                .resource {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid #1a73e8;
                }}
                .resource p {{
                    margin: 5px 0;
                }}
                .warning {{
                    border-left: 4px solid #f44336;
                }}
                .warning .days {{
                    color: #f44336;
                    font-weight: bold;
                }}
                .medium .days {{
                    color: #fb8c00;
                    font-weight: bold;
                }}
                .info {{
                    color: #1a73e8;
                    font-weight: bold;
                }}
                .meta-info {{
                    color: #5f6368;
                    font-size: 0.9em;
                    margin-bottom: 20px;
                }}
                .bill {{
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }}
                .bill-project {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid #2196f3;
                }}
                .bill-record {{
                    margin: 10px 0;
                    padding: 10px;
                    background: #f5f5f5;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <h1>📢华为云资源和账单监控报告</h1>
        """
        
        # 1. 余额汇总
        html += "<h2>💳 账户余额汇总</h2>"
        html += "<div class='balance'>"
        for account_data in accounts_data:
            account_name = account_data['account_name']
            balance = account_data.get('balance')
            stored_cards = account_data.get('stored_cards')
            
            if balance or stored_cards:
                html += f"<h3>{account_name}</h3>"
                if balance:
                    html += f"<p><strong>现金余额：</strong>{balance['total_amount']} {balance['currency']}</p>"
                
                if stored_cards and stored_cards.get('cards'):
                    for card in stored_cards['cards']:
                        html += f"""
                        <div class='stored-card'>
                            <p><strong>{card['card_name']}</strong></p>
                            <p>余额：{card['balance']} CNY</p>
                            <p>面值：{card['face_value']} CNY</p>
                            <p>有效期至：{card['expire_time'].replace('T', ' ').replace('Z', '')}</p>
                        </div>
                        """
        html += "</div>"
        
        # 2. 账单汇总
        has_bills = False
        html += "<h2>💰 按需计费账单汇总</h2>"
        for account_data in accounts_data:
            account_name = account_data['account_name']
            bills = account_data.get('bills')
            if bills and bills.get('records'):
                has_bills = True
                html += f"<div class='bill'>"
                html += f"<h3>账号：{account_name}</h3>"
                html += f"<p><strong>总金额：</strong>{bills['total_amount']} {bills['currency']}</p>"
                
                # 按项目分组展示
                projects = {}
                for record in bills['records']:
                    project = record['project_name'] or 'default'
                    if project not in projects:
                        projects[project] = []
                    projects[project].append(record)
                
                for project, records in projects.items():
                    html += f"<div class='bill-project'>"
                    html += f"<h4>项目：{project}</h4>"
                    for record in records:
                        html += f"<div class='bill-record'>"
                        html += f"<p><strong>服务类型：</strong>{record['service_type']}</p>"
                        html += f"<p><strong>区域：</strong>{record['region']}</p>"
                        html += f"<p><strong>金额：</strong>{record['amount']} {bills['currency']}</p>"
                        html += "</div>"
                    html += "</div>"
                html += "</div>"
        
        # 3. 资源到期提醒
        has_alert = False
        html += "<h2>⚠️ 资源到期提醒</h2>"
        for account_data in accounts_data:
            account_name = account_data['account_name']
            account_has_alert = False
            account_html = f"<div class='account'>"
            account_html += f"<h2>账号：{account_name}</h2>"
            
            # 添加资源信息
            if account_data.get('resources'):
                account_html += "<h3>资源信息</h3>"
                resources_html = ""
                
                for service_type, resources in account_data['resources'].items():
                    service_html = f"<div class='service'>"
                    service_html += f"<h4>{service_type}</h4>"
                    service_has_resources = False
                    
                    for resource in resources:
                        expire_time = resource['expire_time'].replace('T', ' ').replace('Z', '')
                        remaining_days = resource['remaining_days']
                        
                        if remaining_days <= self.alert_days:
                            has_alert = True
                            account_has_alert = True
                            service_has_resources = True
                            
                            if remaining_days <= 15:
                                resource_class = "warning"
                            elif remaining_days <= 30:
                                resource_class = "info"
                            else:
                                resource_class = "medium"
                                
                            service_html += f"""
                            <div class='resource {resource_class}'>
                                <p><strong>名称：</strong>{resource['name']}</p>
                                <p><strong>区域：</strong>{resource['region']}</p>
                                <p><strong>到期时间：</strong>{expire_time}</p>
                                <p><strong>剩余天数：</strong><span class='days'>{remaining_days}天</span></p>
                            """
                            if resource['project']:
                                service_html += f"<p><strong>企业项目：</strong>{resource['project']}</p>"
                            service_html += "</div>"
                    
                    service_html += "</div>"
                    if service_has_resources:
                        resources_html += service_html
                
                # 只有当账号有告警资源时才添加到HTML中
                if account_has_alert:
                    account_html += resources_html
                    html += account_html + "</div>"
        
        html += """
            </body>
        </html>
        """
        
        return html if (has_bills or has_alert) else None

    def send_email(self, subject, html_content):
        """发送HTML格式的邮件，包含附件"""
        if not self.enabled:
            logger.info("邮件通知未启用")
            return False
            
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.smtp_from, self.smtp_to]):
            logger.warning("邮件配置不完整")
            return False
            
        if not html_content:
            logger.info("没有需要告警的内容")
            return False
            
        try:
            # 生成当前日期
            current_date = datetime.now().strftime('%Y-%m-%d')
            file_date = datetime.now().strftime('%Y%m%d')
            
            # 修改邮件标题格式
            email_subject = f"华为云域名到期提醒 ({current_date})"
            
            # 创建邮件对象
            msg = MIMEMultipart('mixed')  # 修改为mixed类型以支持附件
            msg['Subject'] = email_subject
            msg['From'] = self.smtp_from
            msg['To'] = ', '.join(self.smtp_to)
            
            # 添加HTML正文
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 创建HTML附件
            attachment = MIMEText(html_content, 'html', 'utf-8')
            attachment.add_header('Content-Disposition', 'attachment', 
                                filename=f'华为云域名到期提醒-{file_date}.html')
            msg.attach(attachment)
            
            # 发送邮件
            logger.info(f"正在发送邮件到 {', '.join(self.smtp_to)}...")
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info("邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False

    def format_domain_message(self, all_account_domains):
        """格式化域名信息为HTML邮件内容"""
        if not self.enabled:
            return None
        
        alert_days = int(os.getenv('RESOURCE_ALERT_DAYS', '65'))
        
        # 筛选出需要告警的域名
        alert_domains = []
        for account_data in all_account_domains:
            account_name = account_data["account_name"]
            domains = account_data["domains"]
            
            if not domains:
                continue
            
            for domain in domains:
                expire_date = domain.get('expire_date')
                if expire_date:
                    try:
                        expire_datetime = datetime.strptime(expire_date, '%Y-%m-%d')
                        remaining_days = (expire_datetime - datetime.now()).days
                        if remaining_days <= alert_days:
                            alert_domains.append({
                                "account_name": account_name,
                                "domain_name": domain['domain_name'],
                                "expire_date": expire_date,
                                "remaining_days": remaining_days
                            })
                    except Exception as e:
                        logger.error(f"计算域名剩余天数失败: {str(e)}")
        
        if not alert_domains:
            logger.info(f"没有需要告警的域名")
            return None
        
        # 按剩余天数排序
        alert_domains.sort(key=lambda x: x['remaining_days'])
        
        html_content = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .account { margin: 20px 0; }
                .domain-list { margin-left: 20px; }
                .domain-item { 
                    margin: 10px 0;
                    padding: 10px;
                    border-radius: 5px;
                }
                .critical { 
                    background-color: #ffebee;
                    border-left: 4px solid #f44336;
                }
                .warning { 
                    background-color: #fff3e0;
                    border-left: 4px solid #ff9800;
                }
                .notice { 
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                }
                .title {
                    color: #1a73e8;
                    border-bottom: 2px solid #1a73e8;
                    padding-bottom: 10px;
                }
                .account-name {
                    color: #202124;
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 20px 0 10px 0;
                }
            </style>
        </head>
        <body>
            <h1 class="title">华为云域名到期提醒</h1>
        """
        
        current_account = None
        for domain in alert_domains:
            if current_account != domain['account_name']:
                current_account = domain['account_name']
                html_content += f'<h2 class="account-name">账号: {current_account}</h2>'
            
            remaining_days = domain['remaining_days']
            if remaining_days <= 15:
                status_class = "critical"
                icon = "🚨"
            elif remaining_days <= 30:
                status_class = "warning"
                icon = "⚠️"
            else:
                status_class = "notice"
                icon = "ℹ️"
            
            html_content += f"""
            <div class="domain-item {status_class}">
                <h3>{icon} {domain['domain_name']}</h3>
                <p>到期时间: {domain['expire_date']}</p>
                <p>剩余天数: {remaining_days}天</p>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        return html_content 