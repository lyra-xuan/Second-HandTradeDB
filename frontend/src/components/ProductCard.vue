<script setup>
import {ref} from 'vue'
import {money,productStates,safeImage} from '../domain'
defineProps({product:Object})
const failed=ref(false)
</script>
<template><RouterLink :to="`/products/${product.id}`" class="product-card"><div class="cover"><img v-if="safeImage(product.cover_image)&&!failed" :src="safeImage(product.cover_image)" :alt="product.title" loading="lazy" @error="failed=true"><div v-else class="cover-placeholder"><span>{{product.category_name?.slice(0,2)||'好物'}}</span><small>等待发现的校园好物</small></div><span class="badge">{{productStates[product.status]}}</span></div><div class="card-body"><small>{{product.category_name}} · {{product.condition_name}}</small><h3>{{product.title}}</h3><div class="card-bottom"><strong>¥ {{money(product.price)}}</strong><span>{{product.view_count}} 次浏览</span></div><p>{{product.place_name||'交易地点待商议'}}</p></div></RouterLink></template>
