# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： prompt.py
    @date：2026/10/9 20:00
    @desc: 提示词管理序列化器
"""
from django.core import validators
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class PromptCreateSerializer(serializers.Serializer):
    """
    新增提示词
    """
    assistant_type = serializers.CharField(required=True, max_length=128, label=_('Assistant type'))
    node_name = serializers.CharField(required=True, max_length=128, label=_('Node name'))
    prompt_type = serializers.IntegerField(required=True, min_value=0, max_value=1,
                                           label=_('Prompt type, 0: system, 1: user'))
    region = serializers.CharField(required=True, max_length=16, label=_('Region'))
    identity_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=128,
                                        label=_('Identity ID'))
    version = serializers.CharField(required=True, max_length=32, label=_('Version'),
                                    validators=[validators.RegexValidator(
                                        regex=r'^\d+\.\d+\.\d+$',
                                        message=_('The version format is invalid, please use the format like 1.0.0'))])
    content = serializers.CharField(required=True, label=_('Prompt content'), trim_whitespace=False)
    summary = serializers.CharField(required=True, max_length=50, label=_('Summary'))

    def to_java_payload(self) -> dict:
        """
        转换为 fastreat-ai 业务服务的请求体
        """
        return {
            'assistantType': self.validated_data.get('assistant_type'),
            'nodeName': self.validated_data.get('node_name'),
            'promptType': self.validated_data.get('prompt_type'),
            'identityId': self.validated_data.get('identity_id') or None,
            'version': self.validated_data.get('version'),
            'content': self.validated_data.get('content'),
            'summary': self.validated_data.get('summary'),
        }
