# coding=utf-8
"""
    @project: MaxKB
    @Author：fastreat
    @file： permissions.py
    @date：2026/10/9 21:00
    @desc: 业务模块权限
"""
from common.constants.permission_constants import PermissionConstants, RoleConstants

# 与「业务」菜单保持一致的权限集合
BUSINESS_PERMISSIONS = (
    PermissionConstants.APPLICATION_READ.get_workspace_permission(),
    PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
    RoleConstants.USER.get_workspace_role(),
    RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
)
