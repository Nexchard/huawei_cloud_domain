import os
import mysql.connector
from datetime import datetime
from src.logger import logger

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'huaweicloud_monitor')
        self.connection = None
        self.connect()

    def connect(self):
        """连接到数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise e

    def save_resource(self, domain_data, batch_number):
        """保存域名数据到domains表"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            
            sql = """
                INSERT INTO domains (
                    account_name, resource_name, resource_id, service_type,
                    region, expire_time, project_name, remaining_days,
                    batch_number
                ) VALUES (
                    %(account_name)s, %(resource_name)s, %(resource_id)s,
                    %(service_type)s, %(region)s, %(expire_time)s,
                    %(project_name)s, %(remaining_days)s, %(batch_number)s
                )
                ON DUPLICATE KEY UPDATE
                    expire_time = VALUES(expire_time),
                    remaining_days = VALUES(remaining_days)
            """
            
            # 添加batch_number到domain_data
            domain_data['batch_number'] = batch_number
            
            # 转换日期格式
            if domain_data.get('expire_time'):
                try:
                    date_str = domain_data['expire_time']
                    if isinstance(date_str, str):
                        # 尝试解析不同的日期格式
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            except ValueError:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                        domain_data['expire_time'] = date_obj
                except Exception as e:
                    logger.error(f"日期转换失败 expire_time: {date_str}, {str(e)}")
                    domain_data['expire_time'] = None
            
            cursor.execute(sql, domain_data)
            self.connection.commit()
            cursor.close()
            logger.info(f"成功保存域名数据: {domain_data['account_name']} - {domain_data['resource_name']}")
            return True
        except Exception as e:
            logger.error(f"保存域名数据失败: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
        
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close() 