# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： urls.py
    @date：2026/10/9 19:00
    @desc:
"""
from django.urls import path

from . import views

app_name = "business"

# @formatter:off
# fmt: off
urlpatterns = [
    path('workspace/<str:workspace_id>/business/zoom/report/list',
         views.ZoomReportView.List.as_view(), name='zoom_report_list'),
    path('workspace/<str:workspace_id>/business/zoom/report/<int:report_id>/reset',
         views.ZoomReportView.Reset.as_view(), name='zoom_report_reset'),
    path('workspace/<str:workspace_id>/business/prompt/regions',
         views.PromptView.Regions.as_view(), name='prompt_regions'),
    path('workspace/<str:workspace_id>/business/prompt/assistant-types',
         views.PromptView.AssistantTypes.as_view(), name='prompt_assistant_types'),
    path('workspace/<str:workspace_id>/business/prompt/nodes',
         views.PromptView.Nodes.as_view(), name='prompt_nodes'),
    path('workspace/<str:workspace_id>/business/prompt/history',
         views.PromptView.History.as_view(), name='prompt_history'),
    path('workspace/<str:workspace_id>/business/prompt',
         views.PromptView.Operate.as_view(), name='prompt_create'),
    path('workspace/<str:workspace_id>/business/prompt/<int:prompt_id>',
         views.PromptView.Delete.as_view(), name='prompt_delete'),
]
