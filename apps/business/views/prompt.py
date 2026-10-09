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
    PromptNodesAPI
from business.client import FastreatAiClient
from business.permissions import BUSINESS_PERMISSIONS
from business.serializers.prompt import PromptCreateSerializer
from business.views.base import get_query_param, get_region
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.result import DefaultResultSerializer


class PromptView(APIView):
    authentication_classes = [TokenAuth]

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
