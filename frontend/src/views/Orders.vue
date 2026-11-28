<script setup>
import ConfirmDialog from '../components/ConfirmDialog.vue'
import {computed,ref,onMounted} from 'vue'
import {useRoute} from 'vue-router'
import {api,auth} from '../api'
import {money,date,orderStates,orderActions} from '../domain'
const route = useRoute()
const role=ref(route.query.role === 'seller' ? 'seller' : 'buyer'),items=ref([]),error=ref(''),loading=ref(false),busy=ref(false)
const orderId = route.params.id
const statusFilter = ref('')
const visibleOrders = computed(() => statusFilter.value === '' ? items.value : items.value.filter(order => order.status === statusFilter.value))
const labels={confirm:'确认订单',complete:'确认完成',cancel:'取消订单'}
async function load(){loading.value=true;error.value='';try{items.value = orderId ? [await api("/orders/" + orderId)] : await api(`/orders?role=${role.value}`)}catch(e){items.value=[];error.value=e.message}finally{loading.value=false}}
const pendingAction = ref(null)
const confirmationTitles = {
  confirm: '确认接受这笔订单？',
  complete: '确认已完成线下面交？',
  cancel: '确认取消这笔订单？',
}

function confirmAction() {
  const pending = pendingAction.value
  pendingAction.value = null
  if (pending) act(pending.order, pending.type)
}

async function act(order,type){if(busy.value)return;busy.value=true;error.value='';try{await api(`/orders/${order.id}/${type}`,{method:'POST'});await load()}catch(e){error.value=e.message}finally{busy.value=false}}
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
function placeName(id) {
  if (id == null) return '双方商议'
  if (dictionaryLoading.value) return '加载中…'
  if (dictionaryError.value) return '暂不可用'
  return places.value.find(item => item.id === id)?.name ?? '地点已不可用'
}

onMounted(() => {
  load()
  loadDictionary()
})
</script>
<template><div class="section-heading"><div><h1>{{ orderId ? "订单详情" : "交易订单" }}</h1></div><RouterLink v-if="orderId" class="button" :to="{ path: '/orders', query: { role } }">返回订单</RouterLink></div><div v-if="!orderId" class="tabs"><button :class="{selected:role==='buyer'}" :disabled="loading||busy" @click="role='buyer';load()">我买到的</button><button :class="{selected:role==='seller'}" :disabled="loading||busy" @click="role='seller';load()">我卖出的</button></div>
  <label v-if="!orderId" class="list-filter">订单状态<select v-model="statusFilter"><option value="">全部状态</option><option v-for="(label, id) in orderStates" :key="id" :value="Number(id)">{{ label }}</option></select></label><p v-if="error" role="alert" class="error">{{error}} <button @click="load">重试</button></p><p v-if="dictionaryError" class="error" role="alert">选项加载失败：{{ dictionaryError }} <button @click="loadDictionary">重试</button></p><div v-if="loading" class="empty">正在读取订单…</div><div v-else-if="!visibleOrders.length&&!error" class="empty">{{ statusFilter === "" ? "暂无订单" : "没有符合该状态的订单" }}</div><div v-else class="order-list"><article v-for="order in visibleOrders" :key="order.id" class="panel order-card"><div class="order-top"><small>订单 #{{order.id}} · {{date(order.created_at)}}</small><span class="pill">{{orderStates[order.status]}}</span></div><RouterLink :to="`/products/${order.product_id}`"><h3>{{order.product_title}}</h3></RouterLink><strong class="price">¥ {{money(order.product_price)}}</strong><p class="muted">买家：{{order.buyer_nickname}}　 /　卖家：{{order.seller_nickname}}</p><p>地点：{{placeName(order.place_id)}}　联系方式：{{order.contact||'未填写'}}</p><p v-if="orderId && order.finished_at">结束时间：{{ date(order.finished_at) }}</p><div class="actions"><RouterLink v-if="!orderId" class="button" :to="{ path: '/orders/' + order.id, query: { role } }">查看详情</RouterLink><button v-for="type in orderActions(order,auth.user?.id)" :key="type" :class="{primary:type!=='cancel'}" :disabled="busy" @click="pendingAction = { order, type }">{{labels[type]}}</button></div></article></div>
  <ConfirmDialog
    v-if="pendingAction"
    :title="confirmationTitles[pendingAction.type]"
    :description="pendingAction.type === 'complete' ? '该操作将结束订单。' : ''"
    :confirm-label="labels[pendingAction.type]"
    @cancel="pendingAction = null"
    @confirm="confirmAction"
  />
</template>
