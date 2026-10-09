# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： business.py
    @date：2026/10/9 21:00
    @desc: 业务服务公共接口定义
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, inline_serializer
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin


def workspace_parameter():
    return OpenApiParameter(
        name="workspace_id",
        description=_("Workspace ID"),
        type=OpenApiTypes.STR,
        location=OpenApiParameter.PATH,
        required=True,
    )


def region_parameter(required: bool = True):
    return OpenApiParameter(
        name="region",
        description=_("Region code, such as uk / ca"),
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=required,
    )


class BusinessRegionsAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [workspace_parameter()]

    @staticmethod
    def get_response():
        return inline_serializer(
            name="BusinessRegionsResponse",
            fields={
                'code': serializers.IntegerField(help_text=_('Response code')),
                'message': serializers.CharField(help_text=_('Response message')),
                'data': inline_serializer(name="BusinessRegions", fields={
                    'regions': serializers.ListField(child=serializers.CharField(),
                                                     help_text=_('Available region list')),
                    'default_region': serializers.CharField(help_text=_('Default region')),
                }),
            },
        )
