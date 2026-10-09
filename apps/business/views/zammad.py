# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： zammad.py
    @date：2026/10/9 21:00
    @desc: Zammad 分析
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from business.api.zammad import ZammadDataQueryAPI, ZammadTaskCreateAPI, ZammadTaskDataAPI, ZammadTaskListAPI, \
    ZammadTaskResultAPI, ZammadTaskRetryAPI
from business.client import FastreatAiClient
from business.permissions import BUSINESS_PERMISSIONS
from business.serializers.zammad import ZammadDataQuerySerializer, ZammadTaskCreateSerializer, \
    ZammadTaskRetrySerializer
from business.views.base import get_region
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.result import DefaultResultSerializer


class ZammadView(APIView):
    authentication_classes = [TokenAuth]

    class Data(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Query Zammad data'),
            summary=_('Query Zammad data'),
            operation_id='business_zammad_data_query',
            parameters=ZammadDataQueryAPI.get_parameters(),
            request=ZammadDataQueryAPI.get_request(),
            responses=ZammadDataQueryAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def post(self, request: Request, workspace_id: str):
            serializer = ZammadDataQuerySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return result.success(FastreatAiClient.query_zammad_data(
                serializer.to_java_payload(), serializer.validated_data.get('region')))

    class TaskList(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Zammad analysis task list'),
            summary=_('Zammad analysis task list'),
            operation_id='business_zammad_task_list',
            parameters=ZammadTaskListAPI.get_parameters(),
            responses=ZammadTaskListAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str, page_no: int, page_size: int):
            status = request.query_params.get('status')
            return result.success(FastreatAiClient.get_zammad_task_list(
                page_no,
                page_size,
                request.query_params.get('data_type'),
                int(status) if status is not None and status.strip() != '' else None,
                get_region(request)))

    class Task(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Create Zammad analysis task'),
            summary=_('Create Zammad analysis task'),
            operation_id='business_zammad_task_create',
            parameters=ZammadTaskCreateAPI.get_parameters(),
            request=ZammadTaskCreateAPI.get_request(),
            responses=DefaultResultSerializer,
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def post(self, request: Request, workspace_id: str):
            serializer = ZammadTaskCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task_id = FastreatAiClient.create_zammad_task(
                serializer.to_java_payload(FastreatAiClient.get_model_name()),
                serializer.validated_data.get('region'))
            return result.success(task_id)

    class TaskData(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Query Zammad data by analysis task'),
            summary=_('Query Zammad data by analysis task'),
            operation_id='business_zammad_task_data',
            parameters=ZammadTaskDataAPI.get_parameters(),
            responses=ZammadTaskDataAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str, task_id: int, page_no: int, page_size: int):
            return result.success(FastreatAiClient.get_zammad_task_data(
                task_id, page_no, page_size, get_region(request)))

    class TaskResult(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Zammad analysis result'),
            summary=_('Zammad analysis result'),
            operation_id='business_zammad_task_result',
            parameters=ZammadTaskResultAPI.get_parameters(),
            responses=ZammadTaskResultAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def get(self, request: Request, workspace_id: str, task_id: int):
            return result.success(FastreatAiClient.get_zammad_task_result(task_id, get_region(request)))

    class TaskRetry(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Retry failed Zammad analysis task'),
            summary=_('Retry failed Zammad analysis task'),
            operation_id='business_zammad_task_retry',
            parameters=ZammadTaskRetryAPI.get_parameters(),
            responses=DefaultResultSerializer,
            tags=[_('Business')],
        )
        @has_permissions(*BUSINESS_PERMISSIONS)
        def post(self, request: Request, workspace_id: str, task_id: int):
            serializer = ZammadTaskRetrySerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            return result.success(FastreatAiClient.retry_zammad_task(
                task_id,
                serializer.to_java_params(FastreatAiClient.get_model_name()),
                get_region(request)))
