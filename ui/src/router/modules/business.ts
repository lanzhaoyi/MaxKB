import { PermissionConst, RoleConst } from '@/utils/permission/data'
const businessRouter = {
  path: '/business',
  name: 'business',
  meta: {
    title: 'views.business.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermissionWorkspaceManageRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermission,
    ],
    icon: 'app-business',
    iconActive: 'app-business-active',
    group: 'workspace',
    order: 1.5,
  },
  redirect: '/business',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/business',
      name: 'business-index',
      meta: { title: 'views.business.title', activeMenu: '/business', sameRoute: 'business' },
      component: () => import('@/views/fastreat/business/index.vue'),
    },
  ],
}

export default businessRouter
