import requests
import logging
from datetime import datetime
from src.logger import logger

class DomainQuery:
    def __init__(self, domain_name, username, password):
        self.domain_name = domain_name
        self.username = username
        self.password = password
        self.token = None
        self.domain_endpoint = "https://domain.myhuaweicloud.com"
        self.iam_endpoint = "https://iam.myhuaweicloud.com"
    
    def get_token(self):
        """获取IAM token"""
        try:
            url = f"{self.iam_endpoint}/v3/auth/tokens"
            data = {
                "auth": {
                    "identity": {
                        "methods": ["password"],
                        "password": {
                            "user": {
                                "name": self.username,
                                "password": self.password,
                                "domain": {
                                    "name": self.domain_name
                                }
                            }
                        }
                    },
                    "scope": {
                        "domain": {
                            "name": self.domain_name
                        }
                    }
                }
            }
            
            response = requests.post(url, json=data)
            if response.status_code == 201:
                self.token = response.headers.get('X-Subject-Token')
                return True
            else:
                logger.error(f"获取token失败: {response.text}")
                return False
        except Exception as e:
            logger.error(f"获取token异常: {str(e)}")
            return False
    
    def query_domains(self, offset=0, limit=200):
        """查询域名列表"""
        try:
            if not self.token and not self.get_token():
                return {"success": False, "data": None, "message": "获取token失败"}
            
            url = f"{self.domain_endpoint}/v2/domains"
            headers = {
                "X-Auth-Token": self.token
            }
            params = {
                "offset": offset,
                "limit": limit
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": {
                        "domains": data.get("domains", []),
                        "total": data.get("total", 0)
                    }
                }
            else:
                logger.error(f"查询域名失败: {response.text}")
                return {"success": False, "data": None, "message": f"查询域名失败: {response.text}"}
        except Exception as e:
            logger.error(f"查询域名异常: {str(e)}")
            return {"success": False, "data": None, "message": str(e)}
    
    def get_all_domains(self):
        """获取所有域名信息"""
        all_domains = []
        offset = 0
        limit = 200
        
        while True:
            result = self.query_domains(offset, limit)
            if not result["success"]:
                return result
            
            domains = result["data"]["domains"]
            total = result["data"]["total"]
            all_domains.extend(domains)
            
            if len(all_domains) >= total:
                break
            
            offset += limit
        
        return {
            "success": True,
            "data": {
                "domains": all_domains,
                "total": len(all_domains)
            }
        }

def format_domain_data(domain_data, account_name, domain_name):
    """格式化域名数据用于数据库存储
    Args:
        domain_data: 域名数据
        account_name: 账号显示名称
        domain_name: IAM用户所属账号名（用于获取token）
    """
    expire_date = domain_data.get('expire_date')
    if expire_date:
        try:
            expire_datetime = datetime.strptime(expire_date, '%Y-%m-%d')
            remaining_days = (expire_datetime - datetime.now()).days
            # 如果域名已过期（剩余天数小于等于0），返回None
            if remaining_days <= 0:
                return None
        except Exception as e:
            logger.error(f"计算剩余天数失败: {str(e)}")
            remaining_days = None
    else:
        remaining_days = None
    
    return {
        'account_name': account_name,  # 使用新的account_name
        'resource_name': domain_data.get('domain_name'),
        'resource_id': domain_data.get('domain_name'),  # 域名作为资源ID
        'service_type': 'domain',  # 固定为domain类型
        'region': 'global',  # 域名是全局资源
        'expire_time': expire_date,
        'project_name': domain_data.get('project_name', 'default'),
        'remaining_days': remaining_days
    } 