# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： prompt.py
    @date：2026/10/9 20:00
    @desc: 提示词管理
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from business.api.prompt import PromptAssistantTypesAPI, PromptCreateAPI, PromptDeleteAPI, PromptHistoryAPI, \
    PromptNodesAPI, PromptRegionsAPI
from business.client import FastreatAiClient, REGION_PATTERN
from business.serializers.prompt import PromptCreateSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.exception.app_exception import AppApiException
from common.result import DefaultResultSerializer

# 与「业务」菜单保持一致的权限集合
BUSINESS_PERMISSIONS = (
    PermissionConstants.APPLICATION_READ.get_workspace_permission(),
    PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
    RoleConstants.USER.get_workspace_role(),
    RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
)


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


class PromptView(APIView):
    authentication_classes = [TokenAuth]

    class Regions(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Prompt available region list'),
            summary=_('Prompt available region list'),
            operation_id='business_prompt_regions',
            parameters=PromptRegionsAPI.get_parameters(),
            responses=PromptRegionsAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str):
            return result.success({
                'regions': FastreatAiClient.get_regions(),
                'default_region': FastreatAiClient.get_default_region(),
            })

    class AssistantTypes(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Prompt assistant type list'),
            summary=_('Prompt assistant type list'),
            operation_id='business_prompt_assistant_types',
            parameters=PromptAssistantTypesAPI.get_parameters(),
            responses=PromptAssistantTypesAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str):
            return result.success(FastreatAiClient.get_prompt_assistant_types(get_region(request)))

    class Nodes(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Prompt node list'),
            summary=_('Prompt node list'),
            operation_id='business_prompt_nodes',
            parameters=PromptNodesAPI.get_parameters(),
            responses=PromptNodesAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str):
            return result.success(FastreatAiClient.get_prompt_nodes(
                get_query_param(request, 'assistant_type'), get_region(request)))

    class History(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Prompt history list'),
            summary=_('Prompt history list'),
            operation_id='business_prompt_history',
            parameters=PromptHistoryAPI.get_parameters(),
            responses=PromptHistoryAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str):
            prompt_type = request.query_params.get('prompt_type')
            return result.success(FastreatAiClient.get_prompt_history(
                get_query_param(request, 'assistant_type'),
                get_query_param(request, 'node_name'),
                int(prompt_type) if prompt_type is not None and prompt_type.strip() != '' else None,
                get_region(request)))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Create prompt'),
            summary=_('Create prompt'),
            operation_id='business_prompt_create',
            parameters=PromptCreateAPI.get_parameters(),
            request=PromptCreateAPI.get_request(),
            responses=DefaultResultSerializer,
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def post(self, request: Request, workspace_id: str):
            serializer = PromptCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            FastreatAiClient.create_prompt(serializer.to_java_payload(),
                                           serializer.validated_data.get('region'))
            return result.success(True)

    class Delete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete prompt'),
            summary=_('Delete prompt'),
            operation_id='business_prompt_delete',
            parameters=PromptDeleteAPI.get_parameters(),
            responses=DefaultResultSerializer,
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def delete(self, request: Request, workspace_id: str, prompt_id: int):
            FastreatAiClient.delete_prompt(prompt_id, get_region(request))
            return result.success(True)
