<script setup>
import {ref,reactive,onMounted} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {api,upload,auth} from '../api'
import {safeImage} from '../domain'
const route=useRoute(),router=useRouter(),editing=Boolean(route.params.id),busy=ref(false),loading=ref(true),ready=ref(false),error=ref(''),urls=ref('')
const form=reactive({title:'',description:'',price:'',category_id:'',condition_id:'',place_id:''})
const categories = ref([])
const conditions = ref([])
const places = ref([])
const fileInput = ref(null)
const uploading = ref(false)

// 已选图片的本地预览 URL（仅用于缩略图展示），与 urls 文本框保持同步
const previews = ref([])

function syncUrlsFromPreviews() {
  urls.value = previews.value.map(p => p.url).join('\n')
}

function pickFiles() { fileInput.value?.click() }

async function onFilesChange(e) {
  const files = Array.from(e.target.files || [])
  if (!files.length) return
  const remaining = 9 - previews.value.length
  if (remaining <= 0) { error.value = '最多只能上传 9 张图片'; return }
  const batch = files.slice(0, remaining)
  uploading.value = true
  error.value = ''
  try {
    const result = await upload('/uploads', batch)
    const newItems = batch.map((f, i) => ({ url: result.urls[i], preview: URL.createObjectURL(f) }))
    previews.value.push(...newItems)
    syncUrlsFromPreviews()
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

function removePreview(idx) {
  const p = previews.value[idx]
  if (p?.preview) URL.revokeObjectURL(p.preview)
  previews.value.splice(idx, 1)
  syncUrlsFromPreviews()
}

async function loadForm() {
  loading.value = true
  error.value = ''
  try {
    const [categoryOptions, conditionOptions, placeOptions, product] = await Promise.all([
      api('/categories'),
      api('/conditions'),
      api('/places'),
      editing ? api('/products/' + route.params.id) : null,
    ])
    categories.value = categoryOptions
    conditions.value = conditionOptions
    places.value = placeOptions
    if (product) {
      if (product.seller.id !== auth.user?.id) throw new Error('只能编辑自己发布的商品')
      if (product.status === 4) throw new Error('已下架商品不可编辑')
      Object.assign(form, {
        title: product.title,
        description: product.description || '',
        price: product.price,
        category_id: product.category_id,
        condition_id: product.condition_id,
        place_id: product.place_id ?? '',
      })
      urls.value = product.images.join('\n')
      previews.value = product.images.map(u => ({ url: u, preview: safeImage(u) || null }))
    }
    ready.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadForm)
async function submit(){busy.value=true;error.value='';try{const images=urls.value.split('\n').map(x=>x.trim()).filter(Boolean);if(images.length>9)throw new Error('最多填写 9 张图片地址');if(images.some(x=>!safeImage(x)||x.length>255))throw new Error('图片地址须为 http(s) 或站内路径，且不超过 255 字符');const body={...form,price:Number(form.price),category_id:Number(form.category_id),condition_id:Number(form.condition_id),place_id:form.place_id?Number(form.place_id):null,images};const result=await api(editing?`/products/${route.params.id}`:'/products',{method:editing?'PUT':'POST',body});router.push(`/products/${editing?route.params.id:result.id}`)}catch(e){error.value=e.message}finally{busy.value=false}}
</script>
<template><div class="section-heading"><div><h1>{{editing?'编辑商品':'发布我的闲置'}}</h1></div></div><p v-if="loading" class="empty">加载中…</p><p v-if="error" class="error" role="alert">{{error}} <button v-if="!ready" @click="loadForm">重试</button></p><form v-if="ready" class="panel form-panel" @submit.prevent="submit"><label>商品标题<input v-model.trim="form.title" required maxlength="100" placeholder="例如：九成新高等数学教材"></label><div class="form-grid"><label>价格（元）<input v-model="form.price" type="number" required min="0.01" max="99999.99" step="0.01"></label><label>商品分类<select v-model="form.category_id" required><option disabled value="">请选择</option><option v-for="item in categories" :key="item.id" :value="item.id">{{item.name}}</option></select></label><label>成色<select v-model="form.condition_id" required><option disabled value="">请选择</option><option v-for="item in conditions" :key="item.id" :value="item.id">{{item.name}}</option></select></label><label>交易地点<select v-model="form.place_id"><option value="">双方商议</option><option v-for="item in places" :key="item.id" :value="item.id">{{item.name}}</option></select></label></div><label>商品描述<textarea v-model="form.description" rows="5" maxlength="2000" placeholder="使用情况、购买时间、瑕疵与配件…"></textarea></label><label>商品图片（选填，最多 9 张）<input ref="fileInput" type="file" accept="image/png,image/jpeg,image/webp,image/gif" multiple style="display:none" @change="onFilesChange"><div style="margin-top:.5rem"><button type="button" class="button" :disabled="uploading || previews.length>=9" @click="pickFiles">{{uploading?'上传中…':'选择本地图片上传'}}</button><span class="muted" style="margin-left:.5rem">{{previews.length}}/9 张，单张 ≤5MB</span></div></label><div v-if="previews.length" class="preview-grid"><div v-for="(p,i) in previews" :key="i" class="preview-item"><img :src="p.preview" alt=""><button type="button" class="preview-remove" @click="removePreview(i)" title="删除">×</button></div></div><label>图片地址（也可手填，每行一个，最多 9 张）<textarea v-model="urls" rows="3" placeholder="https://… 或 /static/…"></textarea></label><div class="actions"><button class="primary" :disabled="busy">{{busy?'保存中…':editing?'保存修改':'发布商品'}}</button><RouterLink class="button" to="/mine">取消</RouterLink></div></form></template>
