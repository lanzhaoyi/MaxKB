# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： prompt.py
    @date：2026/10/9 20:00
    @desc: 提示词管理接口定义
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, inline_serializer
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin


def _workspace_parameter():
    return OpenApiParameter(
        name="workspace_id",
        description=_("Workspace ID"),
        type=OpenApiTypes.STR,
        location=OpenApiParameter.PATH,
        required=True,
    )


def _region_parameter():
    return OpenApiParameter(
        name="region",
        description=_("Region code, such as uk / ca"),
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=True,
    )


class PromptAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [_workspace_parameter()]


class PromptRegionsAPI(PromptAPI):
    @staticmethod
    def get_response():
        return inline_serializer(
            name="PromptRegionsResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': inline_serializer(name="PromptRegions", fields={
                    'regions': serializers.ListField(child=serializers.CharField(),
                                                     help_text=_('Available region list')),
                    'default_region': serializers.CharField(help_text=_('Default region')),
                }),
            },
        )


class PromptAssistantTypesAPI(PromptAPI):
    @staticmethod
    def get_parameters():
        return PromptAPI.get_parameters() + [_region_parameter()]

    @staticmethod
    def get_response():
        return inline_serializer(
            name="PromptAssistantTypesResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': serializers.ListField(
                    help_text=_('Assistant type list'),
                    child=inline_serializer(name="PromptAssistantTypeItem", fields={
                        'code': serializers.CharField(help_text=_('Assistant type code')),
                        'description': serializers.CharField(help_text=_('Assistant type description')),
                    }),
                ),
            },
        )


class PromptNodesAPI(PromptAPI):
    @staticmethod
    def get_parameters():
        return PromptAPI.get_parameters() + [
            OpenApiParameter(
                name="assistant_type",
                description=_("Assistant type"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
            _region_parameter(),
        ]

    @staticmethod
    def get_response():
        return inline_serializer(
            name="PromptNodesResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': serializers.ListField(
                    help_text=_('Prompt node list'),
                    child=inline_serializer(name="PromptNodeItem", fields={
                        'code': serializers.CharField(help_text=_('Node code')),
                        'description': serializers.CharField(help_text=_('Node description')),
                        'tag': serializers.CharField(required=False, allow_null=True, help_text=_('Node tag')),
                        'validRoles': serializers.ListField(
                            help_text=_('Valid prompt roles'),
                            child=inline_serializer(name="PromptNodeRoleItem", fields={
                                'code': serializers.IntegerField(help_text=_('Role code, 0: system, 1: user')),
                                'description': serializers.CharField(help_text=_('Role description')),
                            }),
                        ),
                        'environmentVariables': serializers.DictField(
                            child=serializers.ListField(child=serializers.CharField()),
                            help_text=_('Environment variables grouped by role code'),
                        ),
                    }),
                ),
            },
        )


class PromptHistoryAPI(PromptAPI):
    @staticmethod
    def get_parameters():
        return PromptAPI.get_parameters() + [
            OpenApiParameter(
                name="assistant_type",
                description=_("Assistant type"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
            OpenApiParameter(
                name="node_name",
                description=_("Node name"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
            OpenApiParameter(
                name="prompt_type",
                description=_("Prompt type, 0: system, 1: user"),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            _region_parameter(),
        ]

    @staticmethod
    def get_response():
        return inline_serializer(
            name="PromptHistoryResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': serializers.ListField(
                    help_text=_('Prompt history list'),
                    child=inline_serializer(name="PromptHistoryItem", fields={
                        'id': serializers.IntegerField(help_text=_('Prompt ID')),
                        'assistantType': serializers.CharField(help_text=_('Assistant type')),
                        'nodeName': serializers.CharField(help_text=_('Node name')),
                        'promptType': serializers.IntegerField(help_text=_('0: system, 1: user')),
                        'region': serializers.CharField(help_text=_('Region')),
                        'identityId': serializers.CharField(help_text=_('Identity ID')),
                        'version': serializers.CharField(help_text=_('Version')),
                        'content': serializers.CharField(help_text=_('Prompt content')),
                        'summary': serializers.CharField(help_text=_('Summary')),
                        'isActive': serializers.IntegerField(help_text=_('Is active')),
                        'status': serializers.IntegerField(
                            help_text=_('0: system default, 1: latest, 2: expired, 3: specific')),
                        'statusDesc': serializers.CharField(help_text=_('Status description')),
                        'createTime': serializers.CharField(help_text=_('Create time')),
                        'updateTime': serializers.CharField(help_text=_('Update time')),
                    }),
                ),
            },
        )


class PromptCreateAPI(PromptAPI):
    @staticmethod
    def get_request():
        return inline_serializer(
            name="PromptCreateRequest",
            fields={
                'assistant_type': serializers.CharField(help_text=_('Assistant type')),
                'node_name': serializers.CharField(help_text=_('Node name')),
                'prompt_type': serializers.IntegerField(help_text=_('Prompt type, 0: system, 1: user')),
                'region': serializers.CharField(help_text=_('Region code')),
                'identity_id': serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                                     help_text=_('Identity ID, default when empty')),
                'version': serializers.CharField(help_text=_('Semantic version, such as 1.0.0')),
                'content': serializers.CharField(help_text=_('Prompt content')),
                'summary': serializers.CharField(help_text=_('Summary, up to 50 characters')),
            },
        )


class PromptDeleteAPI(PromptAPI):
    @staticmethod
    def get_parameters():
        return PromptAPI.get_parameters() + [
            OpenApiParameter(
                name="prompt_id",
                description=_("Prompt ID"),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            _region_parameter(),
        ]
