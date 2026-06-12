import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/Home.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue') },
  { path: '/flights', name: 'Flights', component: () => import('@/views/FlightSearch.vue') },
  { path: '/orders', name: 'Orders', component: () => import('@/views/Orders.vue'), meta: { requiresAuth: true } },
  { path: '/waitlist', name: 'Waitlist', component: () => import('@/views/Waitlist.vue'), meta: { requiresAuth: true } },
  { path: '/orders/:id', name: 'OrderDetail', component: () => import('@/views/OrderDetail.vue'), meta: { requiresAuth: true } },
  { path: '/orders/:id/ticket', name: 'Ticket', component: () => import('@/views/Ticket.vue'), meta: { requiresAuth: true } },
  { path: '/itineraries', name: 'Itineraries', component: () => import('@/views/Itineraries.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('@/views/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/passengers', name: 'Passengers', component: () => import('@/views/Passengers.vue'), meta: { requiresAuth: true } },
  { path: '/messages', name: 'Messages', component: () => import('@/views/Messages.vue'), meta: { requiresAuth: true } },
  { path: '/coupons', name: 'Coupons', component: () => import('@/views/Coupons.vue'), meta: { requiresAuth: true } },
  { path: '/assistant', name: 'TravelAssistant', component: () => import('@/views/TravelAssistant.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: () => import('@/views/AdminDashboard.vue'), meta: { requiresAuth: true, requiresStaff: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresStaff && !userStore.user?.is_staff) {
    next('/')
  } else {
    next()
  }
})

export default router
