# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： base.py
    @date：2026/10/9 21:00
    @desc: 业务模块公共视图与参数校验
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from business.api.business import BusinessRegionsAPI
from business.client import FastreatAiClient, REGION_PATTERN
from business.permissions import BUSINESS_PERMISSIONS
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.exception.app_exception import AppApiException


def get_region(request: Request) -> str:
    """
    获取并校验区域编码
    """
    region = request.query_params.get('region')
    if region is None or REGION_PATTERN.match(region) is None:
        raise AppApiException(500, _('Region is required'))
    return region


def get_query_param(request: Request, name: str) -> str:
    """
    获取必填查询参数
    """
    value = request.query_params.get(name)
    if value is None or value.strip() == '':
        raise AppApiException(500, _('Required parameter is missing') + f': {name}')
    return value.strip()


class BusinessView(APIView):
    authentication_classes = [TokenAuth]

    class Regions(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Business service available region list'),
            summary=_('Business service available region list'),
            operation_id='business_regions',
            parameters=BusinessRegionsAPI.get_parameters(),
            responses=BusinessRegionsAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str):
            return result.success({
                'regions': FastreatAiClient.get_regions(),
                'default_region': FastreatAiClient.get_default_region(),
            })
