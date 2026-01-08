#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云 ECS 安全组规则自动更新脚本
自动获取当前公网 IP 地址并更新到阿里云 ECS 安全组规则中
"""

import os
import sys
import requests
from typing import Optional

from Tea.exceptions import UnretryableException, TeaException
from alibabacloud_tea_openapi.models import Config
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_util import models as util_models
from alibabacloud_ecs20140526 import models as ecs_20140526_models


class SecurityGroupUpdater:
    """安全组规则更新器"""
    
    def __init__(self, region_id: str, endpoint: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            region_id: 阿里云区域 ID，例如 'cn-hangzhou'
            endpoint: 可选的端点地址，默认会根据 region_id 自动生成
        """
        self.region_id = region_id
        if endpoint is None:
            endpoint = f'ecs.{region_id}.aliyuncs.com'
        self.client = self._create_client(endpoint)
    
    @staticmethod
    def _create_client(endpoint: Optional[str] = None) -> Ecs20140526Client:
        """
        创建 ECS 客户端
        
        Args:
            endpoint: 可选的端点地址
            
        Returns:
            ECS 客户端实例
        """
        access_key_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
        access_key_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        
        if not access_key_id or not access_key_secret:
            raise ValueError(
                "请设置环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 "
                "ALIBABA_CLOUD_ACCESS_KEY_SECRET"
            )
        
        config = Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=endpoint
        )
        return Ecs20140526Client(config)
    
    @staticmethod
    def get_public_ip() -> str:
        """
        获取当前公网 IP 地址
        
        Returns:
            公网 IP 地址字符串
            
        Raises:
            Exception: 当无法获取 IP 地址时抛出异常
        """
        # 尝试多个 IP 查询服务，提高可靠性
        ip_services = [
            'https://api.ipify.org',
            'https://ifconfig.me/ip',
            'https://icanhazip.com',
            'https://api.ip.sb/ip'
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # 简单验证 IP 格式
                    if ip and '.' in ip:
                        return ip
            except Exception:
                continue
        
        raise Exception("无法获取公网 IP 地址，请检查网络连接")
    
    def describe_security_group_rules(
        self, 
        security_group_id: str
    ) -> list:
        """
        查询安全组规则
        
        Args:
            security_group_id: 安全组 ID
            
        Returns:
            安全组规则列表
        """
        try:
            request = ecs_20140526_models.DescribeSecurityGroupAttributeRequest(
                region_id=self.region_id,
                security_group_id=security_group_id
            )
            runtime = util_models.RuntimeOptions()
            response = self.client.describe_security_group_attribute_with_options(
                request, runtime
            )
            
            if response.body and response.body.permissions:
                return response.body.permissions.permission
            return []
        except Exception as e:
            print(f"查询安全组规则失败: {e}")
            return []
    
    def revoke_security_group_rule(
        self,
        security_group_id: str,
        ip_protocol: str,
        port_range: str,
        source_cidr_ip: str,
        nic_type: str = 'internet'
    ) -> bool:
        """
        删除安全组规则
        
        Args:
            security_group_id: 安全组 ID
            ip_protocol: IP 协议，例如 'tcp', 'udp', 'icmp'
            port_range: 端口范围，例如 '22/22', '80/80'
            source_cidr_ip: 源 IP 地址段，例如 '1.2.3.4/32'
            nic_type: 网络类型，'internet' 或 'intranet'
            
        Returns:
            是否成功
        """
        try:
            request = ecs_20140526_models.RevokeSecurityGroupRequest(
                region_id=self.region_id,
                security_group_id=security_group_id,
                ip_protocol=ip_protocol,
                port_range=port_range,
                source_cidr_ip=source_cidr_ip,
                nic_type=nic_type
            )
            runtime = util_models.RuntimeOptions()
            response = self.client.revoke_security_group_with_options(
                request, runtime
            )
            return response.status_code == 200
        except Exception as e:
            print(f"删除安全组规则失败: {e}")
            return False
    
    def authorize_security_group_rule(
        self,
        security_group_id: str,
        ip_protocol: str,
        port_range: str,
        source_cidr_ip: str,
        description: str = '',
        nic_type: str = 'internet',
        policy: str = 'Accept'
    ) -> bool:
        """
        添加安全组规则
        
        Args:
            security_group_id: 安全组 ID
            ip_protocol: IP 协议，例如 'tcp', 'udp', 'icmp'
            port_range: 端口范围，例如 '22/22', '80/80'
            source_cidr_ip: 源 IP 地址段，例如 '1.2.3.4/32'
            description: 规则描述
            nic_type: 网络类型，'internet' 或 'intranet'
            policy: 策略，'Accept' 或 'Drop'
            
        Returns:
            是否成功
        """
        try:
            request = ecs_20140526_models.AuthorizeSecurityGroupRequest(
                region_id=self.region_id,
                security_group_id=security_group_id,
                ip_protocol=ip_protocol,
                port_range=port_range,
                source_cidr_ip=source_cidr_ip,
                description=description,
                nic_type=nic_type,
                policy=policy,
                priority="100"
            )
            runtime = util_models.RuntimeOptions()
            response = self.client.authorize_security_group_with_options(
                request, runtime
            )
            return response.status_code == 200
        except Exception as e:
            print(f"添加安全组规则失败: {e}")
            return False
    
    def update_security_group_rule(
        self,
        security_group_id: str,
        ip_protocol: str,
        port_range: str,
        new_source_ip: str,
        description: str = 'Auto-updated from home IP',
        nic_type: str = 'intranet'
    ) -> bool:
        """
        更新安全组规则（先删除旧规则，再添加新规则）
        
        Args:
            security_group_id: 安全组 ID
            ip_protocol: IP 协议，例如 'tcp', 'udp', 'icmp'
            port_range: 端口范围，例如 '22/22', '80/80'
            new_source_ip: 新的源 IP 地址（会自动添加 /32）
            description: 规则描述
            nic_type: 网络类型，'internet' 或 'intranet'
            
        Returns:
            是否成功
        """
        # 确保 IP 地址格式正确
        if '/' not in new_source_ip:
            new_source_ip = f"{new_source_ip}/32"
        
        # 查询现有规则，查找匹配的规则并删除
        existing_rules = self.describe_security_group_rules(security_group_id)
        
        # 查找并删除匹配的旧规则
        deleted_count = 0
        for rule in existing_rules:
            #print(f"规则: {rule.ip_protocol} {rule.port_range} {rule.nic_type} {rule.source_cidr_ip} {rule.description}")
            if (rule.ip_protocol.lower() == ip_protocol.lower() and 
                rule.port_range == port_range and
                rule.source_cidr_ip != new_source_ip and
                rule.description == description):
                # 删除旧规则
                print(f"删除旧规则: {rule.source_cidr_ip}")
                if self.revoke_security_group_rule(
                    security_group_id,
                    ip_protocol,
                    port_range,
                    rule.source_cidr_ip,
                    nic_type
                ):
                    deleted_count += 1
                    print(f"已删除旧规则: {rule.source_cidr_ip}")
        
        # 添加新规则
        if self.authorize_security_group_rule(
            security_group_id,
            ip_protocol,
            port_range,
            new_source_ip,
            description,
            nic_type
        ):
            print(f"已添加新规则: {new_source_ip}")
            return True
        else:
            print("添加新规则失败")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='自动更新阿里云 ECS 安全组规则'
    )
    parser.add_argument(
        '--region-id',
        required=True,
        help='阿里云区域 ID，例如: cn-hangzhou'
    )
    parser.add_argument(
        '--security-group-id',
        required=True,
        help='安全组 ID'
    )
    parser.add_argument(
        '--ip-protocol',
        default='tcp',
        help='IP 协议，默认: tcp'
    )
    parser.add_argument(
        '--port-range',
        required=True,
        help='端口范围，例如: 22/22, 80/80'
    )
    parser.add_argument(
        '--description',
        default='Auto-updated from home IP',
        help='规则描述'
    )
    parser.add_argument(
        '--endpoint',
        help='可选的端点地址'
    )
    
    args = parser.parse_args()
    
    try:
        # 获取公网 IP
        print("正在获取公网 IP 地址...")
        public_ip = SecurityGroupUpdater.get_public_ip()
        print(f"当前公网 IP 地址: {public_ip}")
        
        # 创建更新器
        updater = SecurityGroupUpdater(args.region_id, args.endpoint)
        
        # 更新安全组规则
        print(f"正在更新安全组规则...")
        success = updater.update_security_group_rule(
            args.security_group_id,
            args.ip_protocol,
            args.port_range,
            public_ip,
            args.description
        )
        
        if success:
            print("安全组规则更新成功！")
            return 0
        else:
            print("安全组规则更新失败！")
            return 1
            
    except UnretryableException as e:
        print(f"网络异常: {e}")
        return 1
    except TeaException as e:
        print(f"业务异常: {e}")
        return 1
    except Exception as e:
        print(f"发生错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

