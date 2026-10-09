# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： zammad.py
    @date：2026/10/9 21:00
    @desc: Zammad 分析序列化器
"""
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# Zammad 分析维度：ticket 级 / message 级 / agent 级 / 多维度
ZAMMAD_DATA_TYPES = ('ticket_level', 'message_level', 'agent_level', 'combined_level')

# 采样条数范围，与业务服务 resolveSampleSize 保持一致
SAMPLE_SIZE_MIN = 1
SAMPLE_SIZE_MAX = 1000


class ZammadDataQuerySerializer(serializers.Serializer):
    """
    Zammad 数据查询
    """
    data_type = serializers.ChoiceField(required=True, choices=ZAMMAD_DATA_TYPES, label=_('Data type'))
    region = serializers.CharField(required=True, max_length=16, label=_('Region'))
    created_at_start = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=32,
                                             label=_('Create time start'))
    created_at_end = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=32,
                                           label=_('Create time end'))
    page_no = serializers.IntegerField(required=False, min_value=1, default=1, label=_('Current page'))
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=200, default=10,
                                         label=_('Page size'))
    ticket_page_no = serializers.IntegerField(required=False, min_value=1, label=_('Ticket current page'))
    ticket_page_size = serializers.IntegerField(required=False, min_value=1, max_value=200,
                                                label=_('Ticket page size'))
    message_page_no = serializers.IntegerField(required=False, min_value=1, label=_('Message current page'))
    message_page_size = serializers.IntegerField(required=False, min_value=1, max_value=200,
                                                 label=_('Message page size'))
    agent_page_no = serializers.IntegerField(required=False, min_value=1, label=_('Agent current page'))
    agent_page_size = serializers.IntegerField(required=False, min_value=1, max_value=200,
                                               label=_('Agent page size'))

    def to_java_payload(self) -> dict:
        """
        转换为 fastreat-ai 业务服务的请求体
        """
        data = self.validated_data
        payload = {
            'dataType': data.get('data_type'),
            'createdAtStart': data.get('created_at_start') or '',
            'createdAtEnd': data.get('created_at_end') or '',
            'pageNo': data.get('page_no'),
            'pageSize': data.get('page_size'),
        }
        optional = {
            'ticketPageNo': 'ticket_page_no', 'ticketPageSize': 'ticket_page_size',
            'messagePageNo': 'message_page_no', 'messagePageSize': 'message_page_size',
            'agentPageNo': 'agent_page_no', 'agentPageSize': 'agent_page_size',
        }
        for java_field, field in optional.items():
            if data.get(field) is not None:
                payload[java_field] = data.get(field)
        return payload


class ZammadTaskCreateSerializer(serializers.Serializer):
    """
    创建 Zammad 分析任务
    """
    data_type = serializers.ChoiceField(required=True, choices=ZAMMAD_DATA_TYPES, label=_('Data type'))
    region = serializers.CharField(required=True, max_length=16, label=_('Region'))
    created_at_start = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=32,
                                             label=_('Create time start'))
    created_at_end = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=32,
                                           label=_('Create time end'))
    prompt_text = serializers.CharField(required=True, trim_whitespace=False, label=_('Analysis prompt'))
    sample_size = serializers.IntegerField(required=False, min_value=SAMPLE_SIZE_MIN, max_value=SAMPLE_SIZE_MAX,
                                           label=_('Sample size'))

    def to_java_payload(self, model_name: str = None) -> dict:
        """
        转换为 fastreat-ai 业务服务的请求体，modelName 为空时不传该字段
        """
        data = self.validated_data
        payload = {
            'dataType': data.get('data_type'),
            'createdAtStart': data.get('created_at_start') or '',
            'createdAtEnd': data.get('created_at_end') or '',
            'promptText': data.get('prompt_text'),
        }
        if model_name is not None and model_name != '':
            payload['modelName'] = model_name
        if data.get('sample_size') is not None:
            payload['sampleSize'] = data.get('sample_size')
        return payload


class ZammadTaskRetrySerializer(serializers.Serializer):
    """
    重试失败的 Zammad 分析任务
    """
    prompt_text = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                        trim_whitespace=False, label=_('Analysis prompt'))
    sample_size = serializers.IntegerField(required=False, min_value=SAMPLE_SIZE_MIN, max_value=SAMPLE_SIZE_MAX,
                                           label=_('Sample size'))

    def to_java_params(self, model_name: str = None) -> dict:
        """
        转换为 fastreat-ai 业务服务的查询参数，空值不传
        """
        params = {}
        if self.validated_data.get('prompt_text'):
            params['promptText'] = self.validated_data.get('prompt_text')
        if self.validated_data.get('sample_size') is not None:
            params['sampleSize'] = self.validated_data.get('sample_size')
        if model_name is not None and model_name != '':
            params['modelName'] = model_name
        return params
