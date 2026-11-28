<script setup>
import {ref,computed,onMounted} from 'vue'
import {useRoute} from 'vue-router'
import {api} from '../api'
import {productStates} from '../domain'
import ProductCard from '../components/ProductCard.vue'
const route=useRoute(),mine=route.path==='/mine',favorite=route.path==='/favorites'
const title=mine?'我的发布':favorite?'我的收藏':'全部商品'
const items=ref([]),page=ref(1),total=ref(0),keyword=ref(''),category=ref(''),busy=ref(false),error=ref('')
const pages=computed(()=>Math.max(1,Math.ceil(total.value/12)))
async function load(reset=false){if(reset)page.value=1;busy.value=true;error.value='';try{const query=new URLSearchParams({page:page.value,page_size:12});if(keyword.value)query.set('keyword',keyword.value);if(category.value)query.set('category_id',category.value);const data=await api(favorite?'/favorites':`${mine?'/products/mine':'/products'}?${query}`);items.value=favorite?data:data.items;total.value=favorite?data.length:data.total}catch(e){error.value=e.message}finally{busy.value=false}}
const statusFilter = ref('')
const visibleItems = computed(() => statusFilter.value === '' ? items.value : items.value.filter(product => product.status === statusFilter.value))
const removingId = ref(null)
const favoriteError = ref('')

async function removeFavorite(productId) {
  if (removingId.value !== null) return
  removingId.value = productId
  favoriteError.value = ''
  try {
    await api('/favorites/' + productId, { method: 'DELETE' })
    items.value = items.value.filter(product => product.id !== productId)
    total.value = items.value.length
  } catch (error) {
    favoriteError.value = error.message
  } finally {
    removingId.value = null
  }
}

const categories = ref([])
const dictionaryError = ref('')
const dictionaryLoading = ref(false)

async function loadDictionary() {
  dictionaryLoading.value = true
  dictionaryError.value = ''
  try {
    categories.value = await api('/categories')
  } catch (e) {
    dictionaryError.value = e.message
  } finally {
    dictionaryLoading.value = false
  }
}
onMounted(() => {
  load()
  if (!mine && !favorite) loadDictionary()
})
</script>
<template><section class="hero" v-if="!mine&&!favorite"><div><span class="intro-tag">校园集市</span><h1>发现身边的好物</h1><div class="hero-tags"><span>教材书籍</span><span>数码电子</span><span>生活日用</span></div></div><RouterLink to="/publish" class="primary">＋ 发布闲置</RouterLink></section>
<div class="section-heading"><div><h2>{{title}}</h2></div><RouterLink v-if="mine" class="primary" to="/publish">＋ 发布商品</RouterLink><span v-else class="muted">{{total}} 件好物</span></div>
<form v-if="!mine&&!favorite" class="filters" @submit.prevent="load(true)"><label class="search-field"><span class="sr-only">搜索商品</span><input v-model.trim="keyword" maxlength="50" placeholder="搜索你需要的好物，如教材、耳机…"></label><label><span class="sr-only">商品分类</span><select v-model="category" :disabled="dictionaryLoading || !!dictionaryError"><option value="">全部分类</option><option v-for="item in categories" :key="item.id" :value="item.id">{{item.name}}</option></select></label><button class="primary" :disabled="busy">搜索</button><button type="button" @click="keyword='';category='';load(true)" :disabled="busy">重置</button></form>
<label v-if="mine" class="list-filter">
  当前页商品状态
  <select v-model="statusFilter">
    <option value="">全部状态</option>
    <option v-for="(label, id) in productStates" :key="id" :value="Number(id)">{{ label }}</option>
  </select>
</label>
<p v-if="favoriteError" class="error" role="alert">{{ favoriteError }}</p>
<p v-if="dictionaryError" class="error" role="alert">选项加载失败：{{ dictionaryError }} <button @click="loadDictionary">重试</button></p>
<div v-if="busy" class="empty" role="status">正在寻找好物…</div><div v-else-if="error" class="empty"><p class="error" role="alert">{{error}}</p><button @click="load()">重新加载</button></div><div v-else-if="!visibleItems.length" class="empty"><span class="empty-icon">◇</span><h3>{{mine?(statusFilter === '' ? '还没有发布商品' : '当前页没有符合该状态的商品'):favorite?'还没有收藏好物':'暂时没有找到商品'}}</h3><p>换个关键词试试，或发布你的第一件闲置。</p><RouterLink to="/publish" class="text-button">去发布 →</RouterLink></div><div v-else class="product-grid"><ProductCard v-for="product in visibleItems" :key="product.id" :product="product">
  <template v-if="favorite" #actions>
    <button type="button" :disabled="removingId !== null" @click="removeFavorite(product.id)">{{ removingId === product.id ? '正在取消…' : '取消收藏' }}</button>
  </template>
</ProductCard></div><div class="pagination" v-if="!favorite&&total"><button :disabled="page===1||busy" @click="page--;load()">上一页</button><span>{{page}} / {{pages}}</span><button :disabled="page>=pages||busy" @click="page++;load()">下一页</button></div></template>
