import {createApp} from 'vue'
import {createRouter, createWebHashHistory} from 'vue-router'
import App from './App.vue'
import Auth from './views/Auth.vue'
import Market from './views/Market.vue'
import Detail from './views/Detail.vue'
import ProductForm from './views/ProductForm.vue'
import Orders from './views/Orders.vue'
import Profile from './views/Profile.vue'
import Stats from './views/Stats.vue'
import Admin from './views/Admin.vue'
import {auth,api} from './api'
import './style.css'
const router=createRouter({history:createWebHashHistory(),routes:[
  {path:'/login',component:Auth,meta:{public:true}}, {path:'/',component:Market},
  {path:'/mine',component:Market},{path:'/favorites',component:Market},
  {path:'/publish',component:ProductForm},{path:'/products/:id/edit',component:ProductForm},
  {path:'/products/:id',component:Detail},{path:'/orders',component:Orders}, {path:'/orders/:id',component:Orders},
  {path:'/profile',component:Profile},{path:'/stats',component:Stats},
  {path:'/admin',component:Admin,meta:{admin:true}},
  {path:'/:pathMatch(.*)*',redirect:'/'}
]})
router.beforeEach(async to=>{
  if(to.meta.public) return true
  if(!auth.token) return {path:'/login',query:{redirect:to.fullPath}}
  if(!auth.user) { try {auth.user=await api('/auth/me')} catch { if(!auth.token) return '/login' } }
  if (to.meta.admin && !auth.user?.is_admin) return '/'
})
window.addEventListener('auth-expired',()=>router.replace('/login'))
createApp(App).use(router).mount('#app')
