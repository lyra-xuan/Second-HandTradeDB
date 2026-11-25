<script setup>
import ConfirmDialog from '../components/ConfirmDialog.vue'
import {ref,onMounted,computed,watch} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {api,auth} from '../api'
import {money,date,productStates,safeImage} from '../domain'
const route=useRoute(),router=useRouter(),product=ref(null),error=ref(''),busy=ref(false),loading=ref(true),imageIndex=ref(0),failed=ref(false),contact=ref(''),place=ref(''),notice=ref('')
const own=computed(()=>product.value?.seller.id===auth.user?.id)
async function load(){loading.value=true;error.value='';try{product.value=await api(`/products/${route.params.id}`);contact.value=auth.user?.contact||''}catch(e){error.value=e.message}finally{loading.value=false}}
const pendingAction = ref(null)
const confirmations = {
  reserve: { title: '确认预订这件商品？', description: '请与卖家沟通面交。', confirmLabel: '确认预订' },
  delist: { title: '确认下架这件商品？', confirmLabel: '确认下架' },
  reshelf: { title: '确认重新上架？', confirmLabel: '确认上架' },
}

function confirmAction() {
  const type = pendingAction.value
  pendingAction.value = null
  if (type) action(type)
}

async function action(type){if(busy.value)return;busy.value=true;error.value='';notice.value='';try{
if(type==='favorite'){await api(`/favorites/${product.value.id}`,{method:product.value.is_favorite?'DELETE':'POST'});product.value.is_favorite=!product.value.is_favorite}
else if(type==='reserve'){await api('/orders',{method:'POST',body:{product_id:product.value.id,place_id:place.value?Number(place.value):null,contact:contact.value||null}});router.push('/orders')}
else{await api(`/products/${product.value.id}/${type}`,{method:'POST'});await load();notice.value='操作成功'}
}catch(e){error.value=e.message}finally{busy.value=false}}
const places = ref([])
const dictionaryError = ref('')
const dictionaryLoading = ref(false)

async function loadDictionary() {
  dictionaryLoading.value = true
  dictionaryError.value = ''
  try {
    places.value = await api('/places')
  } catch (e) {
    dictionaryError.value = e.message
  } finally {
    dictionaryLoading.value = false
  }
}
const canReserve = computed(() => Boolean(auth.user) && !own.value && product.value?.status === 1)
watch(canReserve, available => {
  if (available) loadDictionary()
})
onMounted(load)
</script>
<template><RouterLink to="/" class="back-link">← 返回好物集市</RouterLink><div v-if="loading" class="empty">正在加载商品…</div><p v-if="error" class="error" role="alert">{{error}} <button v-if="!product" @click="load">重试</button></p><p v-if="notice" class="success">{{notice}}</p><section v-if="product" class="detail-grid"><div class="panel"><div class="detail-image"><img v-if="safeImage(product.images[imageIndex])&&!failed" :src="safeImage(product.images[imageIndex])" :alt="product.title" @error="failed=true"><div v-else class="cover-placeholder"><span>{{product.category_name}}</span><small>暂无可用图片</small></div></div><div class="thumbs"><button v-for="(_,i) in product.images" :key="i" :class="{selected:imageIndex===i}" @click="imageIndex=i;failed=false">图片 {{i+1}}</button></div></div><div class="panel detail-copy"><p class="eyebrow">{{product.category_name}} / {{product.condition_name}}</p><span class="pill">{{productStates[product.status]}}</span><h1>{{product.title}}</h1><p class="detail-price">¥ {{money(product.price)}}</p><p class="description">{{product.description||'卖家暂未填写描述。'}}</p><dl><dt>发布者</dt><dd>{{product.seller.nickname}}</dd><dt>交易地点</dt><dd>{{product.place_name||'双方商议'}}</dd><dt>卖家联系方式</dt><dd>{{product.seller.contact||'暂未填写'}}</dd><dt>发布时间</dt><dd>{{date(product.created_at)}}</dd><dt>浏览次数</dt><dd>{{product.view_count}}</dd></dl><div v-if="canReserve"><label>面交地点<select v-model="place" :disabled="dictionaryLoading || !!dictionaryError"><option value="">与卖家商议</option><option v-for="item in places" :key="item.id" :value="item.id">{{item.name}}</option></select></label><p v-if="dictionaryError" class="error" role="alert">选项加载失败：{{ dictionaryError }} <button @click="loadDictionary">重试</button></p><label>你的联系方式<input v-model.trim="contact" maxlength="100" placeholder="便于卖家与你联系"></label></div><div class="actions"><button v-if="canReserve" class="primary" :disabled="busy||!auth.user" @click="pendingAction = 'reserve'">预订这件好物</button><button v-if="product.status !== 4" :disabled="busy" @click="action('favorite')">{{product.is_favorite?'♥ 已收藏 · 取消':'♡ 收藏商品'}}</button><RouterLink v-if="own&&product.status!==4" :to="`/products/${product.id}/edit`" class="button">编辑商品</RouterLink><button v-if="(own||auth.user?.is_admin)&&product.status!==4" :disabled="busy" @click="pendingAction = 'delist'">下架</button><button v-if="auth.user?.is_admin&&product.status===4" :disabled="busy" @click="pendingAction = 'reshelf'">重新上架</button></div></div></section>
  <ConfirmDialog
    v-if="pendingAction"
    v-bind="confirmations[pendingAction]"
    @cancel="pendingAction = null"
    @confirm="confirmAction"
  />
</template>
