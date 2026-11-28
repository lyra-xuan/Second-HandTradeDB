<script setup>
import BrandIcon from './components/BrandIcon.vue'
import NavIcon from './components/NavIcon.vue'
import {ref,watch} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {auth,api,clearSession} from './api'
import {safeImage} from './domain'
const route=useRoute(),router=useRouter()
const avatarFailed = ref(false)
watch(() => auth.user?.avatar, () => { avatarFailed.value = false })
async function logout(){try{await api('/auth/logout',{method:'POST'})}finally{clearSession();router.replace('/login')}}
</script>
<template>
  <RouterView v-if="route.meta.public" />
  <div v-else class="app-shell">
    <aside class="sidebar"><RouterLink class="brand" to="/"><BrandIcon /><span>校园二手交易平台</span></RouterLink>
      
      <nav aria-label="主导航">
        <RouterLink to="/"><NavIcon name="shop" /><span>发现好物</span></RouterLink>
        <RouterLink to="/mine"><NavIcon name="publish" /><span>我的发布</span></RouterLink>
        <RouterLink to="/favorites"><NavIcon name="heart" /><span>我的收藏</span></RouterLink>
        <RouterLink to="/orders"><NavIcon name="orders" /><span>交易订单</span></RouterLink>
        <RouterLink to="/stats"><NavIcon name="chart" /><span>校园数据</span></RouterLink>
        <RouterLink v-if="auth.user?.is_admin" to="/admin"><NavIcon name="user" /><span>管理中心</span></RouterLink>
        <RouterLink to="/profile"><NavIcon name="user" /><span>个人资料</span></RouterLink>
      </nav>
      
      <button class="logout" @click="logout().catch(()=>{})">退出登录 ↗</button>
    </aside>
    <main class="workspace"><header class="topbar"><span>校园集市</span><RouterLink to="/profile" class="user-chip"><img v-if="!avatarFailed && safeImage(auth.user?.avatar)" class="user-avatar" :src="safeImage(auth.user.avatar)" alt="" @error="avatarFailed = true"><b v-else>{{auth.user?.nickname?.slice(0,1)||'同'}}</b>{{auth.user?.nickname||'同学'}}</RouterLink></header><div class="content"><RouterView :key="route.fullPath" /></div></main>
  </div>
</template>
