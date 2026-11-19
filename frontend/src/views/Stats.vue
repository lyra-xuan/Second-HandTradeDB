<script setup>
import {ref,computed,onMounted} from 'vue'
import {api} from '../api'
import {money} from '../domain'
const overview=ref(null),categories=ref([]),error=ref(''),loading=ref(false)
const max=computed(()=>Math.max(1,...categories.value.map(x=>x.on_sale_count)))
async function load(){loading.value=true;error.value='';try{const [o,c]=await Promise.all([api('/stats/overview'),api('/stats/categories')]);overview.value=o;categories.value=c.items}catch(e){error.value=e.message}finally{loading.value=false}}
onMounted(load)
</script>
<template><div class="section-heading"><div><h1>校园数据</h1></div><button @click="load" :disabled="loading">刷新数据 ↻</button></div><p v-if="error" class="error" role="alert">{{error}}</p><div v-if="loading" class="empty">正在汇总校园数据…</div><template v-else-if="overview"><div class="stats-grid"><article class="panel metric" v-for="item in [['校园用户',overview.user_count],['发布商品',overview.product_total],['在售好物',overview.product_on_sale],['完成交易',overview.order_finished],['累计成交额','¥ '+money(overview.trade_amount)],['订单成交率',overview.finish_rate||'暂无订单']]" :key="item[0]"><span>{{item[0]}}</span><strong>{{item[1]}}</strong></article></div><section class="panel chart"><h2>在售商品分类分布</h2><div v-for="item in categories" :key="item.category_id" class="bar-row"><span>{{item.category_name}}</span><div class="bar-track"><div class="bar" :style="{width:`${item.on_sale_count/max*100}%`}"></div></div><b>{{item.on_sale_count}} 件</b></div><p v-if="!categories.length" class="muted">暂无分类数据</p></section></template></template>
