/**
 * Vue Router 配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'

// 布局组件
const Layout = () => import('@/layout/index.vue')

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'Odometer' }
      }
    ]
  },
  {
    path: '/service',
    component: Layout,
    redirect: '/service/list',
    meta: { title: 'AI服务', icon: 'MagicStick' },
    children: [
      {
        path: 'generate',
        name: 'ServiceGenerate',
        component: () => import('@/views/service/generate.vue'),
        meta: { title: '生成服务', icon: 'Plus' }
      },
      {
        path: 'list',
        name: 'ServiceList',
        component: () => import('@/views/service/list.vue'),
        meta: { title: '我的服务', icon: 'List' }
      },
      {
        path: 'detail/:id',
        name: 'ServiceDetail',
        component: () => import('@/views/service/detail.vue'),
        meta: { title: '服务详情', hidden: true }
      }
    ]
  },
  {
    path: '/product',
    component: Layout,
    redirect: '/product/list',
    meta: { title: '产品管理', icon: 'Goods' },
    children: [
      {
        path: 'list',
        name: 'ProductList',
        component: () => import('@/views/product/list.vue'),
        meta: { title: '产品列表', icon: 'List' }
      },
      {
        path: 'add',
        name: 'ProductAdd',
        component: () => import('@/views/product/edit.vue'),
        meta: { title: '添加产品', icon: 'Plus' }
      },
      {
        path: 'edit/:id',
        name: 'ProductEdit',
        component: () => import('@/views/product/edit.vue'),
        meta: { title: '编辑产品', hidden: true }
      }
    ]
  },
  {
    path: '/order',
    component: Layout,
    redirect: '/order/list',
    meta: { title: '订单管理', icon: 'Document' },
    children: [
      {
        path: 'list',
        name: 'OrderList',
        component: () => import('@/views/order/list.vue'),
        meta: { title: '订单列表', icon: 'List' }
      },
      {
        path: 'detail/:id',
        name: 'OrderDetail',
        component: () => import('@/views/order/detail.vue'),
        meta: { title: '订单详情', hidden: true }
      }
    ]
  },
  {
    path: '/statistics',
    component: Layout,
    redirect: '/statistics/overview',
    meta: { title: '数据统计', icon: 'DataAnalysis' },
    children: [
      {
        path: 'overview',
        name: 'StatisticsOverview',
        component: () => import('@/views/statistics/overview.vue'),
        meta: { title: '数据概览', icon: 'PieChart' }
      },
      {
        path: 'cost',
        name: 'StatisticsCost',
        component: () => import('@/views/statistics/cost.vue'),
        meta: { title: '成本分析', icon: 'Money' }
      }
    ]
  },
  {
    path: '/customer',
    component: Layout,
    children: [
      {
        path: '',
        name: 'CustomerList',
        component: () => import('@/views/customer/list.vue'),
        meta: { title: '客户管理', icon: 'User' }
      }
    ]
  },
  {
    path: '/traceability',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Traceability',
        component: () => import('@/views/traceability/index.vue'),
        meta: { title: '溯源管理', icon: 'Connection' }
      }
    ]
  },
  {
    path: '/settings',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      }
    ]
  },
  {
    path: '/help',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Help',
        component: () => import('@/views/help/index.vue'),
        meta: { title: '帮助中心', icon: 'QuestionFilled' }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', hidden: true }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

// 路由守卫
router.beforeEach((to, from, next) => {
  NProgress.start()

  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 智农链销` : '智农链销'

  // 检查登录状态
  const token = localStorage.getItem('token')

  if (to.path === '/login') {
    next()
  } else if (!token) {
    next('/login')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
