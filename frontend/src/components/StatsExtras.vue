<script setup>
import { onMounted, reactive } from 'vue'
import { api } from '../api'
import { money } from '../domain'

const sections = reactive([
  { key: 'ranking', title: '热门商品榜', path: '/stats/ranking?limit=10', items: [], error: '', loading: false },
  { key: 'sellers', title: '活跃卖家榜', path: '/stats/sellers?limit=5', items: [], error: '', loading: false },
  { key: 'sales', title: '分类成交分析', path: '/stats/category-sales', items: [], error: '', loading: false },
])
const columns = {
  ranking: [['title', '商品'], ['price', '价格'], ['view_count', '浏览量'], ['favorite_count', '收藏量']],
  sellers: [['nickname', '卖家'], ['on_sale_count', '在售商品'], ['total_views', '累计浏览量'], ['finished_orders', '完成订单']],
  sales: [['category_name', '分类'], ['deal_count', '成交笔数'], ['total_amount', '成交总额'], ['avg_price', '平均成交价']],
}
const currencyFields = new Set(['price', 'total_amount', 'avg_price'])

async function load(section) {
  if (section.loading) return
  section.loading = true
  section.error = ''
  try {
    section.items = (await api(section.path)).items
  } catch (error) {
    section.error = error.message
  } finally {
    section.loading = false
  }
}

function refresh() {
  return Promise.all(sections.map(load))
}
onMounted(refresh)
defineExpose({ refresh })
</script>

<template>
  <section v-for="section in sections" :key="section.key" class="panel chart">
    <h2>{{ section.title }}</h2>
    <p v-if="section.loading" class="muted" role="status">正在加载{{ section.title }}…</p>
    <p v-else-if="section.error" class="error" role="alert">
      {{ section.error }} <button type="button" @click="load(section)">重试</button>
    </p>
    <div v-else-if="section.items.length" class="table-scroll">
      <table class="data-table" :aria-label="section.title">
        <thead>
          <tr>
            <th v-if="section.key !== 'sales'" scope="col">排名</th>
            <th v-for="[field, label] in columns[section.key]" :key="field" scope="col">{{ label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in section.items" :key="item.product_id ?? item.seller_id ?? item.category_name">
            <td v-if="section.key !== 'sales'">{{ index + 1 }}</td>
            <td v-for="[field] in columns[section.key]" :key="field">
              <RouterLink v-if="field === 'title'" :to="'/products/' + item.product_id">{{ item.title }}</RouterLink>
              <template v-else>{{ currencyFields.has(field) ? '¥ ' + money(item[field]) : item[field] }}</template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="muted">暂无数据</p>
  </section>
</template>
