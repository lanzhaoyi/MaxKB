# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： zammad.py
    @date：2026/10/9 21:00
    @desc: Zammad 分析接口定义
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, inline_serializer
from rest_framework import serializers

from business.api.business import region_parameter, workspace_parameter
from common.mixins.api_mixin import APIMixin


def _page_parameters():
    return [
        OpenApiParameter(
            name="page_no",
            description=_("Current page"),
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
        OpenApiParameter(
            name="page_size",
            description=_("Page size"),
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ]


def _task_id_parameter():
    return OpenApiParameter(
        name="task_id",
        description=_("Analysis task ID"),
        type=OpenApiTypes.INT,
        location=OpenApiParameter.PATH,
        required=True,
    )


class ZammadAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [workspace_parameter()]


class ZammadDataQueryAPI(ZammadAPI):
    @staticmethod
    def get_request():
        return inline_serializer(
            name="ZammadDataQueryRequest",
            fields={
                'data_type': serializers.ChoiceField(
                    choices=['ticket_level', 'message_level', 'agent_level', 'combined_level'],
                    help_text=_('Data type')),
                'region': serializers.CharField(help_text=_('Region code')),
                'created_at_start': serializers.CharField(required=False, allow_blank=True,
                                                         help_text=_('Create time start')),
                'created_at_end': serializers.CharField(required=False, allow_blank=True,
                                                       help_text=_('Create time end')),
                'page_no': serializers.IntegerField(required=False, help_text=_('Current page')),
                'page_size': serializers.IntegerField(required=False, help_text=_('Page size')),
                'ticket_page_no': serializers.IntegerField(required=False, help_text=_('Ticket current page')),
                'ticket_page_size': serializers.IntegerField(required=False, help_text=_('Ticket page size')),
                'message_page_no': serializers.IntegerField(required=False, help_text=_('Message current page')),
                'message_page_size': serializers.IntegerField(required=False, help_text=_('Message page size')),
                'agent_page_no': serializers.IntegerField(required=False, help_text=_('Agent current page')),
                'agent_page_size': serializers.IntegerField(required=False, help_text=_('Agent page size')),
            },
        )

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ZammadDataQueryResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': serializers.DictField(
                    help_text=_('Single dimension returns {records, total, page, size}; '
                                'combined_level returns {ticketPage, messagePage, agentPage}')),
            },
        )


class ZammadTaskListAPI(ZammadAPI):
    @staticmethod
    def get_parameters():
        return ZammadAPI.get_parameters() + _page_parameters() + [
            OpenApiParameter(
                name="data_type",
                description=_("Data type, empty means all"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="status",
                description=_("Task status, 0: pending, 1: running, 2: finished, 3: failed"),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            region_parameter(),
        ]

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ZammadTaskListResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': inline_serializer(name="ZammadTaskPage", fields={
                    'total': serializers.IntegerField(help_text=_('Total count')),
                    'page': serializers.IntegerField(help_text=_('Current page')),
                    'size': serializers.IntegerField(help_text=_('Page size')),
                    'records': serializers.ListField(
                        help_text=_('Analysis task list'),
                        child=inline_serializer(name="ZammadTaskItem", fields={
                            'id': serializers.IntegerField(help_text=_('Task ID')),
                            'dataType': serializers.CharField(help_text=_('Data type')),
                            'filterJson': serializers.CharField(help_text=_('Filter conditions')),
                            'promptText': serializers.CharField(help_text=_('Analysis prompt')),
                            'modelName': serializers.CharField(required=False, allow_blank=True,
                                                               help_text=_('Model name')),
                            'analysisTime': serializers.CharField(required=False, allow_null=True,
                                                                  help_text=_('Analysis time')),
                            'status': serializers.IntegerField(help_text=_('Task status')),
                            'statusText': serializers.CharField(help_text=_('Task status text')),
                            'failReason': serializers.CharField(required=False, allow_blank=True,
                                                                help_text=_('Failure reason')),
                            'hasResult': serializers.BooleanField(help_text=_('Has analysis result')),
                            'createTime': serializers.CharField(help_text=_('Create time')),
                        }),
                    ),
                }),
            },
        )


class ZammadTaskCreateAPI(ZammadAPI):
    @staticmethod
    def get_request():
        return inline_serializer(
            name="ZammadTaskCreateRequest",
            fields={
                'data_type': serializers.ChoiceField(
                    choices=['ticket_level', 'message_level', 'agent_level', 'combined_level'],
                    help_text=_('Data type')),
                'region': serializers.CharField(help_text=_('Region code')),
                'created_at_start': serializers.CharField(required=False, allow_blank=True,
                                                         help_text=_('Create time start')),
                'created_at_end': serializers.CharField(required=False, allow_blank=True,
                                                       help_text=_('Create time end')),
                'prompt_text': serializers.CharField(help_text=_('Analysis prompt')),
                'sample_size': serializers.IntegerField(required=False, help_text=_('Sample size, 1-1000')),
            },
        )


class ZammadTaskDataAPI(ZammadAPI):
    @staticmethod
    def get_parameters():
        return ZammadAPI.get_parameters() + [_task_id_parameter()] + _page_parameters() + [region_parameter()]

    @staticmethod
    def get_response():
        return ZammadDataQueryAPI.get_response()


class ZammadTaskResultAPI(ZammadAPI):
    @staticmethod
    def get_parameters():
        return ZammadAPI.get_parameters() + [_task_id_parameter(), region_parameter()]

    @staticmethod
    def get_response():
        return inline_serializer(
            name="ZammadTaskResultResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': inline_serializer(name="ZammadTaskResult", fields={
                    'id': serializers.IntegerField(help_text=_('Task ID')),
                    'dataType': serializers.CharField(help_text=_('Data type')),
                    'filterJson': serializers.CharField(help_text=_('Filter conditions')),
                    'promptText': serializers.CharField(help_text=_('Analysis prompt')),
                    'modelName': serializers.CharField(required=False, allow_blank=True,
                                                       help_text=_('Model name')),
                    'analysisTime': serializers.CharField(required=False, allow_null=True,
                                                          help_text=_('Analysis time')),
                    'htmlResult': serializers.CharField(help_text=_('Analysis result in HTML')),
                }),
            },
        )


class ZammadTaskRetryAPI(ZammadAPI):
    @staticmethod
    def get_parameters():
        return ZammadAPI.get_parameters() + [_task_id_parameter(), region_parameter()] + [
            OpenApiParameter(
                name="prompt_text",
                description=_("Retry prompt, keep the original prompt when empty"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="sample_size",
                description=_("Sample size, 1-1000"),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ]
