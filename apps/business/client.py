# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： client.py
    @date：2026/10/9 19:00
    @desc: fastreat-ai 业务服务接口客户端
"""
import base64
import hashlib
import hmac
import json
import os
import re
import time

import requests
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from common.exception.app_exception import AppApiException

# fastreat-ai 业务服务默认地址
DEFAULT_BASE_URL = 'https://ai.fastreat.com/uk/api'

# 业务服务默认请求超时时间（秒）
DEFAULT_REQUEST_TIMEOUT = 30

# 业务服务成功响应码
SUCCESS_CODE = '0'

# 平台 JWT 签名密钥，需与 fastreat-ai 服务端 TempJwtUtil.SECRET 保持一致
PLATFORM_JWT_SECRET = 'fastreat-temp-secret-key-2026'

# 提示词管理可用的区域，可通过环境变量 MAXKB_FASTREAT_AI_REGIONS 覆盖
DEFAULT_REGIONS = 'ca,uk'

# 默认区域，可通过环境变量 MAXKB_FASTREAT_AI_DEFAULT_REGION 覆盖
DEFAULT_REGION = 'uk'

# 区域编码格式
REGION_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,16}$')


class FastreatAiClient:
    """
    fastreat-ai 业务服务客户端（Zoom 监控报告、Zammad 数据分析、提示词管理等）
    """

    @staticmethod
    def get_base_url(region: str = None) -> str:
        """
        fastreat-ai 业务服务地址
        优先取区域专属配置 MAXKB_FASTREAT_AI_BASE_URL_<REGION>，其次取通用配置 MAXKB_FASTREAT_AI_BASE_URL
        :param region: 区域编码，如 uk / ca
        """
        keys = []
        if region is not None and REGION_PATTERN.match(region):
            keys.append(f'MAXKB_FASTREAT_AI_BASE_URL_{region.upper()}')
        keys.append('MAXKB_FASTREAT_AI_BASE_URL')
        for key in keys:
            value = os.environ.get(key)
            if value is not None and value.strip() != '':
                return value.strip().rstrip('/')
        return DEFAULT_BASE_URL

    @staticmethod
    def get_request_timeout() -> int:
        """
        业务服务请求超时时间（秒），可通过环境变量 MAXKB_FASTREAT_AI_REQUEST_TIMEOUT 覆盖
        """
        return int(os.environ.get('MAXKB_FASTREAT_AI_REQUEST_TIMEOUT', str(DEFAULT_REQUEST_TIMEOUT)))

    @staticmethod
    def get_regions() -> list:
        """
        提示词管理可用的区域列表，可通过环境变量 MAXKB_FASTREAT_AI_REGIONS 覆盖（英文逗号分隔）
        """
        regions = [region.strip() for region in os.environ.get('MAXKB_FASTREAT_AI_REGIONS', DEFAULT_REGIONS).split(',')]
        return [region for region in regions if REGION_PATTERN.match(region)]

    @staticmethod
    def get_default_region() -> str:
        """
        提示词管理默认区域，可通过环境变量 MAXKB_FASTREAT_AI_DEFAULT_REGION 覆盖
        """
        region = os.environ.get('MAXKB_FASTREAT_AI_DEFAULT_REGION', DEFAULT_REGION)
        regions = FastreatAiClient.get_regions()
        if region in regions:
            return region
        return regions[0] if len(regions) > 0 else region

    @staticmethod
    def get_service_token(region: str = None) -> str:
        """
        获取业务服务级 token（fastreat-ai 中 t_ai_auth 表的 server_token）
        优先取区域专属配置 MAXKB_FASTREAT_AI_SERVICE_TOKEN_<REGION>，其次取通用配置 MAXKB_FASTREAT_AI_SERVICE_TOKEN
        :param region: 区域编码，如 uk / ca
        """
        keys = []
        if region is not None and REGION_PATTERN.match(region):
            keys.append(f'MAXKB_FASTREAT_AI_SERVICE_TOKEN_{region.upper()}')
        keys.append('MAXKB_FASTREAT_AI_SERVICE_TOKEN')
        for key in keys:
            token = os.environ.get(key)
            if token is not None and token.strip() != '':
                return token.strip()
        raise AppApiException(500, str(_('The prompt service token is not configured'))
                              + f': {"/".join(keys)}')

    @staticmethod
    def build_platform_jwt(service_token: str, ip: str = 'unknown') -> str:
        """
        使用平台固定密钥签发 HS256 平台 JWT，业务服务 @RequireAuth(STRICT) 接口要求该凭证
        :param service_token: 服务级 token
        :param ip: 客户端ip
        :return: 平台 JWT
        """
        header = {'typ': 'JWT', 'alg': 'HS256'}
        payload = {'ip': ip, 'xAuthToken': service_token, 'timestamp': int(time.time() * 1000)}
        segments = [FastreatAiClient._base64_url_encode(json.dumps(part, separators=(',', ':')).encode('utf-8'))
                    for part in (header, payload)]
        signature = hmac.new(PLATFORM_JWT_SECRET.encode('utf-8'),
                             '.'.join(segments).encode('ascii'), hashlib.sha256).digest()
        segments.append(FastreatAiClient._base64_url_encode(signature))
        return '.'.join(segments)

    @staticmethod
    def _base64_url_encode(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')

    @staticmethod
    def _request(method: str, path: str, params: dict = None, json_body: dict = None,
                 region: str = None, authorized: bool = False):
        """
        请求业务服务
        :param method: 请求方法
        :param path: 请求路径
        :param params: 查询参数
        :param json_body: 请求体
        :param region: 区域编码，用于选择区域专属的服务地址与 token
        :param authorized: 是否需要平台 JWT 鉴权（@RequireAuth(STRICT) 接口）
        """
        url = f'{FastreatAiClient.get_base_url(region)}/{path.lstrip("/")}'
        headers = None
        if authorized:
            headers = {'Authorization': FastreatAiClient.build_platform_jwt(
                FastreatAiClient.get_service_token(region))}
        try:
            response = requests.request(method, url, params=params, json=json_body, headers=headers,
                                        timeout=FastreatAiClient.get_request_timeout())
        except requests.RequestException as e:
            raise AppApiException(500, str(_('Failed to connect to the business service')) + f': {e}')
        if response.status_code != status.HTTP_200_OK:
            raise AppApiException(500,
                                  str(_('The business service responded abnormally'))
                                  + f': HTTP {response.status_code}')
        try:
            body = response.json()
        except ValueError:
            raise AppApiException(500, _('The business service responded abnormally'))
        if not isinstance(body, dict) or str(body.get('code')) != SUCCESS_CODE:
            message = body.get('message') if isinstance(body, dict) else None
            raise AppApiException(500, message if message else _('The business service responded abnormally'))
        return body.get('data')

    @staticmethod
    def get_zoom_report_list() -> list:
        """
        Zoom 监控分析报告列表
        :return: 报告列表
        """
        data = FastreatAiClient._request('GET', '/zoom/analyze/report/list')
        return data if isinstance(data, list) else []

    @staticmethod
    def reset_zoom_report(report_id: int):
        """
        重置 Zoom 监控分析报告，将提示词1~5的生成状态重置为初始
        :param report_id: 报告id
        """
        FastreatAiClient._request('POST', f'/zoom/analyze/report/{report_id}/reset')

    @staticmethod
    def get_model_name() -> str:
        """
        分析任务使用的部署模型名，可通过环境变量 MAXKB_FASTREAT_AI_MODEL_NAME 配置
        未配置时返回空字符串，调用方不传该字段，由业务服务使用默认模型
        """
        return os.environ.get('MAXKB_FASTREAT_AI_MODEL_NAME', '').strip()

    @staticmethod
    def query_zammad_data(data: dict, region: str) -> dict:
        """
        查询 Zammad 分析数据
        :param data: 查询条件（dataType/createdAtStart/createdAtEnd/分页参数）
        :param region: 区域编码
        :return: 单维度为分页对象，多维度为各维度分页对象集合
        """
        result = FastreatAiClient._request('POST', '/zammad/data/query', json_body=data,
                                           region=region, authorized=True)
        return result if isinstance(result, dict) else {}

    @staticmethod
    def create_zammad_task(data: dict, region: str):
        """
        创建 Zammad 分析任务
        :param data: 任务数据（dataType/createdAtStart/createdAtEnd/promptText/modelName/sampleSize）
        :param region: 区域编码
        :return: 任务id
        """
        return FastreatAiClient._request('POST', '/zammad/analysis/task', json_body=data,
                                         region=region, authorized=True)

    @staticmethod
    def get_zammad_task_list(page_no: int, page_size: int, data_type: str, status: int, region: str) -> dict:
        """
        Zammad 分析任务列表
        :param page_no: 当前页
        :param page_size: 每页条数
        :param data_type: 数据类型，为空查询全部
        :param status: 任务状态，为-1或空查询全部
        :param region: 区域编码
        :return: 分页对象
        """
        params = {}
        if data_type is not None and data_type != '':
            params['dataType'] = data_type
        if status is not None and status >= 0:
            params['status'] = status
        result = FastreatAiClient._request('GET', f'/zammad/analysis/tasks/{page_no}/{page_size}',
                                           params=params, region=region, authorized=True)
        return result if isinstance(result, dict) else {}

    @staticmethod
    def get_zammad_task_data(task_id: int, page_no: int, page_size: int, region: str) -> dict:
        """
        按任务回查 Zammad 数据明细
        :param task_id: 任务id
        :param page_no: 当前页
        :param page_size: 每页条数
        :param region: 区域编码
        :return: 单维度为分页对象，多维度为各维度分页对象集合
        """
        result = FastreatAiClient._request('GET',
                                           f'/zammad/analysis/task/{task_id}/data/{page_no}/{page_size}',
                                           region=region, authorized=True)
        return result if isinstance(result, dict) else {}

    @staticmethod
    def get_zammad_task_result(task_id: int, region: str) -> dict:
        """
        Zammad 分析结果
        :param task_id: 任务id
        :param region: 区域编码
        :return: 分析结果对象
        """
        result = FastreatAiClient._request('GET', f'/zammad/analysis/task/{task_id}/result',
                                           region=region, authorized=True)
        return result if isinstance(result, dict) else {}

    @staticmethod
    def retry_zammad_task(task_id: int, params: dict, region: str):
        """
        重试失败的 Zammad 分析任务
        :param task_id: 任务id
        :param params: 重试参数（sampleSize/promptText/modelName）
        :param region: 区域编码
        :return: 任务id
        """
        return FastreatAiClient._request('POST', f'/zammad/analysis/task/{task_id}/retry', params=params,
                                         region=region, authorized=True)

    @staticmethod
    def get_prompt_assistant_types(region: str) -> list:
        """
        提示词助手类型列表
        :param region: 区域编码
        :return: 助手类型列表
        """
        data = FastreatAiClient._request('GET', '/prompt/assistant-types', params={'region': region},
                                         region=region, authorized=True)
        return data if isinstance(data, list) else []

    @staticmethod
    def get_prompt_nodes(assistant_type: str, region: str) -> list:
        """
        提示词节点配置列表
        :param assistant_type: 助手类型
        :param region: 区域编码
        :return: 节点列表
        """
        data = FastreatAiClient._request('GET', '/prompt/nodes',
                                         params={'assistantType': assistant_type, 'region': region},
                                         region=region, authorized=True)
        return data if isinstance(data, list) else []

    @staticmethod
    def get_prompt_history(assistant_type: str, node_name: str, prompt_type: int, region: str) -> list:
        """
        提示词历史记录列表
        :param assistant_type: 助手类型
        :param node_name: 节点名称
        :param prompt_type: 提示词类型 0=系统 1=用户，为空时查询全部
        :param region: 区域编码
        :return: 历史记录列表
        """
        params = {'assistantType': assistant_type, 'nodeName': node_name}
        if prompt_type is not None:
            params['promptType'] = prompt_type
        data = FastreatAiClient._request('GET', '/prompt/history', params=params,
                                         region=region, authorized=True)
        return data if isinstance(data, list) else []

    @staticmethod
    def create_prompt(data: dict, region: str):
        """
        新增提示词
        :param data: 提示词数据（assistantType/nodeName/promptType/identityId/version/content/summary）
        :param region: 区域编码
        """
        FastreatAiClient._request('POST', '/prompt', json_body=data, region=region, authorized=True)

    @staticmethod
    def delete_prompt(prompt_id: int, region: str):
        """
        删除提示词
        :param prompt_id: 提示词id
        :param region: 区域编码
        """
        FastreatAiClient._request('DELETE', f'/prompt/{prompt_id}', region=region, authorized=True)
