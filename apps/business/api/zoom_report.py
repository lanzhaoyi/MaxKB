# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： zoom_report.py
    @date：2026/10/9 19:00
    @desc: Zoom 监控报告接口定义
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, inline_serializer
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin


def _prompt_output_fields():
    fields = {}
    for index in range(1, 6):
        fields[f'prompt{index}Output'] = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                                               help_text=_('Prompt output'))
        fields[f'prompt{index}OutputStatus'] = serializers.IntegerField(
            required=False, help_text=_('0: initial, 1: generating, 2: success, 3: failed'))
    return fields


class ZoomReportAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description=_("Workspace ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ]


class ZoomReportListAPI(ZoomReportAPI):
    @staticmethod
    def get_response():
        item_fields = {
            'id': serializers.IntegerField(help_text=_('Report ID')),
            'serverId': serializers.IntegerField(help_text=_('Server ID')),
            'bizId': serializers.CharField(help_text=_('Business ID')),
            'bizDt': serializers.CharField(help_text=_('Business date')),
            'modelName': serializers.CharField(help_text=_('Model name')),
            'totalSessionCount': serializers.IntegerField(help_text=_('Total session count')),
        }
        item_fields.update(_prompt_output_fields())
        item_fields.update({
            'apptDataStatus': serializers.IntegerField(
                help_text=_('Zoom file download status, 0: initial, 1: generating, 2: success, 3: failed')),
            'apptSourceData': serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                                    help_text=_('Zoom file source data')),
            'apptTargetData': serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                                    help_text=_('Zoom file downloaded data')),
            'createTime': serializers.CharField(help_text=_('Create time')),
            'updateTime': serializers.CharField(help_text=_('Update time')),
        })
        return inline_serializer(
            name="ZoomReportListResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': serializers.ListField(
                    help_text=_('Zoom monitoring report list'),
                    child=inline_serializer(name="ZoomReportItem", fields=item_fields),
                ),
            },
        )


class ZoomReportResetAPI(ZoomReportAPI):
    @staticmethod
    def get_parameters():
        return ZoomReportAPI.get_parameters() + [
            OpenApiParameter(
                name="report_id",
                description=_("Report ID"),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ]
