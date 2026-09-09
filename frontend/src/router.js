import { createRouter, createWebHistory } from 'vue-router'

import { auth } from './auth'

const DashboardView = () => import('./views/DashboardView.vue')
const AdminReviewsView = () => import('./views/AdminReviewsView.vue')
const CommunityEditorView = () => import('./views/CommunityEditorView.vue')
const CommunityPostView = () => import('./views/CommunityPostView.vue')
const CommunityView = () => import('./views/CommunityView.vue')
const JourneyView = () => import('./views/JourneyView.vue')
const LegalView = () => import('./views/LegalView.vue')
const InsightsView = () => import('./views/InsightsView.vue')
const MutualHelpView = () => import('./views/MutualHelpView.vue')
const NotificationsView = () => import('./views/NotificationsView.vue')
const LearnView = () => import('./views/LearnView.vue')
const LoginView = () => import('./views/LoginView.vue')
const PlanDetailView = () => import('./views/PlanDetailView.vue')
const PlanEditorView = () => import('./views/PlanEditorView.vue')
const PlansView = () => import('./views/PlansView.vue')
const ProfileView = () => import('./views/ProfileView.vue')
const RegisterView = () => import('./views/RegisterView.vue')
const ReviewCenterView = () => import('./views/ReviewCenterView.vue')
const TeamView = () => import('./views/TeamView.vue')

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: (to, from, savedPosition) => savedPosition || (to.path === from.path ? false : { top: 0 }),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', component: LoginView, meta: { guest: true } },
    { path: '/register', component: RegisterView, meta: { guest: true } },
    { path: '/privacy', component: LegalView },
    { path: '/community-guidelines', component: LegalView },
    { path: '/dashboard', component: DashboardView, meta: { auth: true } },
    { path: '/profile', component: ProfileView, meta: { auth: true } },
    { path: '/admin/reviews', component: AdminReviewsView, meta: { auth: true, admin: true } },
    { path: '/community', component: CommunityView, meta: { auth: true } },
    { path: '/community/new', component: CommunityEditorView, meta: { auth: true } },
    { path: '/community/posts/:id/edit', component: CommunityEditorView, meta: { auth: true } },
    { path: '/community/posts/:id', component: CommunityPostView, meta: { auth: true } },
    { path: '/plans/:slug/community', component: CommunityView, meta: { auth: true } },
    { path: '/plans/:slug/community/new', component: CommunityEditorView, meta: { auth: true } },
    { path: '/plans', component: PlansView, meta: { auth: true } },
    { path: '/plans/new', component: PlanEditorView, meta: { auth: true } },
    { path: '/plans/:slug/edit', component: PlanEditorView, meta: { auth: true } },
    { path: '/plans/:slug', component: PlanDetailView, meta: { auth: true } },
    { path: '/journey', component: JourneyView, meta: { auth: true } },
    { path: '/insights', component: InsightsView, meta: { auth: true } },
    { path: '/review', component: ReviewCenterView, meta: { auth: true } },
    { path: '/mutual-help', component: MutualHelpView, meta: { auth: true } },
    { path: '/team', component: TeamView, meta: { auth: true } },
    { path: '/notifications', component: NotificationsView, meta: { auth: true } },
    { path: '/learn/:enrollmentId/:dayNumber', component: LearnView, meta: { auth: true } },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
})

router.beforeEach(async (to) => {
  if (!auth.ready) await auth.restore()
  if (to.meta.auth && !auth.loggedIn) return { path: '/login', query: { next: to.fullPath } }
  if (to.meta.admin && !auth.user?.is_staff) return '/dashboard'
  if (to.meta.guest && auth.loggedIn) return '/dashboard'
})

export default router
