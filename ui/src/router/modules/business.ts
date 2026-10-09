import { PermissionConst, RoleConst } from '@/utils/permission/data'

const businessPermission = [
  RoleConst.USER.getWorkspaceRole,
  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
  PermissionConst.APPLICATION_READ.getWorkspacePermissionWorkspaceManageRole,
  PermissionConst.APPLICATION_READ.getWorkspacePermission,
]

const businessRouter = {
  path: '/business',
  name: 'business',
  meta: {
    title: 'views.business.title',
    menu: true,
    permission: businessPermission,
    icon: 'app-business',
    iconActive: 'app-business-active',
    group: 'workspace',
    order: 1.5,
  },
  redirect: '/business/prompt',
  component: () => import('@/layout/layout-template/MainLayout.vue'),
  children: [
    {
      path: '/business/prompt',
      name: 'businessPrompt',
      meta: {
        title: 'views.business.prompt.title',
        activeMenu: '/business',
        parentPath: '/business',
        parentName: 'business',
        permission: businessPermission,
      },
      component: () => import('@/views/fastreat/business/prompt/index.vue'),
    },
    {
      path: '/business/zammad',
      name: 'businessZammad',
      meta: {
        title: 'views.business.zammad.title',
        activeMenu: '/business',
        parentPath: '/business',
        parentName: 'business',
        permission: businessPermission,
      },
      component: () => import('@/views/fastreat/business/zammad/index.vue'),
    },
    {
      path: '/business/zoom',
      name: 'businessZoom',
      meta: {
        title: 'views.business.zoom.title',
        activeMenu: '/business',
        parentPath: '/business',
        parentName: 'business',
        permission: businessPermission,
      },
      component: () => import('@/views/fastreat/business/zoom/index.vue'),
    },
  ],
}

export default businessRouter
