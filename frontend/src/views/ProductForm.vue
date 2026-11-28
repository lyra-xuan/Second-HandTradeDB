<script setup>
import {computed,ref,reactive,onMounted} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {api,upload,auth} from '../api'
import {imageUploadError,safeImage} from '../domain'
const route=useRoute(),router=useRouter(),editing=Boolean(route.params.id),busy=ref(false),loading=ref(true),ready=ref(false),error=ref(''),urls=ref('')
const form=reactive({title:'',description:'',price:'',category_id:'',condition_id:'',place_id:''})
const categories = ref([])
const conditions = ref([])
const places = ref([])
const fileInput = ref(null)
const uploading = ref(false)

const images = computed(() => urls.value.split('\n').map(url => url.trim()).filter(Boolean))

function pickFiles() {
  fileInput.value?.click()
}

async function onFilesChange(event) {
  const input = event.target
  const files = Array.from(input.files || [])
  input.value = ''
  if (!files.length || uploading.value || busy.value) return
  if (images.value.length + files.length > 9) {
    error.value = '商品图片最多 9 张，请减少选中的图片'
    return
  }
  error.value = imageUploadError(files)
  if (error.value) return

  uploading.value = true
  try {
    const result = await upload('/uploads', files)
    if (result.urls?.length !== files.length || result.urls.some(url => !safeImage(url))) {
      throw new Error('上传返回的图片地址不完整')
    }
    urls.value = [...images.value, ...result.urls].join('\n')
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
  }
}

function removePreview(index) {
  if (uploading.value || busy.value) return
  urls.value = images.value.filter((_, i) => i !== index).join('\n')
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
    }
    ready.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadForm)
async function submit(){if(busy.value||uploading.value)return;busy.value=true;error.value='';try{const selectedImages=images.value;if(selectedImages.length>9)throw new Error('最多填写 9 张图片地址');if(selectedImages.some(x=>!safeImage(x)||x.length>255))throw new Error('图片地址须为 http(s) 或站内路径，且不超过 255 字符');const body={...form,price:Number(form.price),category_id:Number(form.category_id),condition_id:Number(form.condition_id),place_id:form.place_id?Number(form.place_id):null,images:selectedImages};const result=await api(editing?`/products/${route.params.id}`:'/products',{method:editing?'PUT':'POST',body});router.push(`/products/${editing?route.params.id:result.id}`)}catch(e){error.value=e.message}finally{busy.value=false}}
</script>
<template><div class="section-heading"><div><h1>{{editing?'编辑商品':'发布我的闲置'}}</h1></div></div><p v-if="loading" class="empty">加载中…</p><p v-if="error" class="error" role="alert">{{error}} <button v-if="!ready" @click="loadForm">重试</button></p><form v-if="ready" class="panel form-panel" @submit.prevent="submit"><label>商品标题<input v-model.trim="form.title" required maxlength="100" placeholder="例如：九成新高等数学教材"></label><div class="form-grid"><label>价格（元）<input v-model="form.price" type="number" required min="0.01" max="99999.99" step="0.01"></label><label>商品分类<select v-model="form.category_id" required><option disabled value="">请选择</option><option v-for="item in categories" :key="item.id" :value="item.id">{{item.name}}</option></select></label><label>成色<select v-model="form.condition_id" required><option disabled value="">请选择</option><option v-for="item in conditions" :key="item.id" :value="item.id">{{item.name}}</option></select></label><label>交易地点<select v-model="form.place_id"><option value="">双方商议</option><option v-for="item in places" :key="item.id" :value="item.id">{{item.name}}</option></select></label></div><label>商品描述<textarea v-model="form.description" rows="5" maxlength="2000" placeholder="使用情况、购买时间、瑕疵与配件…"></textarea></label><label>商品图片（选填，最多 9 张）<input ref="fileInput" type="file" accept="image/png,image/jpeg,image/webp,image/gif" multiple style="display:none" @change="onFilesChange"><div style="margin-top:.5rem"><button type="button" class="button" :disabled="uploading || busy || images.length>=9" @click="pickFiles">{{uploading?'上传中…':'选择本地图片上传'}}</button><span class="muted" style="margin-left:.5rem">{{images.length}}/9 张，单张 ≤5MB</span></div></label><div v-if="images.length" class="preview-grid"><div v-for="(url,i) in images" :key="i" class="preview-item"><img v-if="safeImage(url)" :src="safeImage(url)" alt=""><button type="button" class="preview-remove" @click="removePreview(i)" :disabled="uploading || busy" :aria-label="'移除图片 ' + (i + 1)">×</button></div></div><label>图片地址（也可手填，每行一个，最多 9 张）<textarea v-model="urls" :disabled="uploading || busy" rows="3" placeholder="https://… 或 /static/…"></textarea></label><div class="actions"><button class="primary" :disabled="busy || uploading">{{busy?'保存中…':editing?'保存修改':'发布商品'}}</button><RouterLink class="button" to="/mine">取消</RouterLink></div></form></template>
