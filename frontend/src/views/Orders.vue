<script setup>
import {ref,onMounted} from 'vue'
import {api,auth} from '../api'
import {money,date,orderStates,orderActions,places} from '../domain'
const role=ref('buyer'),items=ref([]),error=ref(''),loading=ref(false),busy=ref(false)
const labels={confirm:'确认订单',complete:'确认完成',cancel:'取消订单'}
async function load(){loading.value=true;error.value='';try{items.value=await api(`/orders?role=${role.value}`)}catch(e){error.value=e.message}finally{loading.value=false}}
async function act(order,type){if(!window.confirm(type==='complete'?'确认已完成线下面交？该操作将结束订单。':`确定${labels[type]}？`))return;busy.value=true;error.value='';try{await api(`/orders/${order.id}/${type}`,{method:'POST'});await load()}catch(e){error.value=e.message}finally{busy.value=false}}
onMounted(load)
</script>
<template><div class="section-heading"><div><h1>交易订单</h1></div></div><div class="tabs"><button :class="{selected:role==='buyer'}" :disabled="loading||busy" @click="role='buyer';load()">我买到的</button><button :class="{selected:role==='seller'}" :disabled="loading||busy" @click="role='seller';load()">我卖出的</button></div><p v-if="error" role="alert" class="error">{{error}} <button @click="load">重试</button></p><div v-if="loading" class="empty">正在读取订单…</div><div v-else-if="!items.length&&!error" class="empty">还没有订单，去集市发现好物吧。</div><div v-else class="order-list"><article v-for="order in items" :key="order.id" class="panel order-card"><div class="order-top"><small>订单 #{{order.id}} · {{date(order.created_at)}}</small><span class="pill">{{orderStates[order.status]}}</span></div><RouterLink :to="`/products/${order.product_id}`"><h3>{{order.product_title}}</h3></RouterLink><strong class="price">¥ {{money(order.product_price)}}</strong><p class="muted">买家：{{order.buyer_nickname}}　 /　卖家：{{order.seller_nickname}}</p><p>地点：{{places[order.place_id-1]||'双方商议'}}　联系方式：{{order.contact||'未填写'}}</p><div class="actions"><button v-for="type in orderActions(order,auth.user?.id)" :key="type" :class="{primary:type!=='cancel'}" :disabled="busy" @click="act(order,type)">{{labels[type]}}</button></div></article></div></template>
