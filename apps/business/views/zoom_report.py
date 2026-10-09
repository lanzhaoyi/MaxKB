# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： zoom_report.py
    @date：2026/10/9 19:00
    @desc: Zoom 监控报告
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from business.api.zoom_report import ZoomReportListAPI, ZoomReportResetAPI
from business.client import FastreatAiClient
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.result import DefaultResultSerializer


class ZoomReportView(APIView):
    authentication_classes = [TokenAuth]

    class List(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Zoom monitoring report list'),
            summary=_('Zoom monitoring report list'),
            operation_id='business_zoom_report_list',
            parameters=ZoomReportListAPI.get_parameters(),
            responses=ZoomReportListAPI.get_response(),
            tags=[_('Business')],
        )
        @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_permission(),
                         PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str):
            return result.success(FastreatAiClient.get_zoom_report_list())

    class Reset(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Reset zoom monitoring report'),
            summary=_('Reset zoom monitoring report'),
            operation_id='business_zoom_report_reset',
            parameters=ZoomReportResetAPI.get_parameters(),
            responses=DefaultResultSerializer,
            tags=[_('Business')],
        )
        @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_permission(),
                         PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def post(self, request: Request, workspace_id: str, report_id: int):
            FastreatAiClient.reset_zoom_report(report_id)
            return result.success(True)
