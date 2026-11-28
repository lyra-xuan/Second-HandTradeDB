<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import { money } from '../domain'
import StatsTrendChart from '../components/StatsTrendChart.vue'
import StatsExtras from '../components/StatsExtras.vue'

const overview = ref(null)
const categories = ref([])
const priceRanges = ref([])
const trend = ref([])
const days = ref(30)
const extras = ref(null)

const loading = ref(false)
const trendLoading = ref(false)
const summaryError = ref('')
const pricesError = ref('')
const trendError = ref('')

const categoryMax = computed(() => Math.max(1, ...categories.value.map(item => item.on_sale_count)))
const priceMax = computed(() => Math.max(1, ...priceRanges.value.map(item => item.product_count)))
const metrics = computed(() => {
  const data = overview.value
  if (!data) return []
  return [
    ['校园用户', data.user_count],
    ['发布商品', data.product_total],
    ['在售好物', data.product_on_sale],
    ['完成交易', data.order_finished],
    ['累计成交额', '¥ ' + money(data.trade_amount)],
    ['订单成交率', data.finish_rate || '暂无订单'],
  ]
})

async function loadSummary() {
  summaryError.value = ''
  try {
    const [summary, distribution] = await Promise.all([
      api('/stats/overview'),
      api('/stats/categories'),
    ])
    overview.value = summary
    categories.value = distribution.items
  } catch (error) {
    summaryError.value = error.message
  }
}

async function loadPrices() {
  pricesError.value = ''
  try {
    const data = await api('/stats/price-range')
    priceRanges.value = data.items
  } catch (error) {
    pricesError.value = error.message
  }
}

async function loadTrend() {
  trendLoading.value = true
  trendError.value = ''
  try {
    const data = await api('/stats/trend?days=' + days.value)
    trend.value = data.items
  } catch (error) {
    trendError.value = error.message
  } finally {
    trendLoading.value = false
  }
}

function selectDays(value) {
  if (value === days.value || trendLoading.value) return
  days.value = value
  loadTrend()
}

async function refresh() {
  loading.value = true
  try {
    await Promise.all([loadSummary(), loadPrices(), loadTrend(), extras.value?.refresh()])
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>

<template>
  <header class="section-heading">
    <h1>校园数据</h1>
    <button type="button" :disabled="loading || trendLoading" @click="refresh">刷新数据 ↻</button>
  </header>

  <p v-if="summaryError" class="error" role="alert">概览加载失败：{{ summaryError }}</p>
  <div v-if="metrics.length" class="stats-grid">
    <article v-for="[label, value] in metrics" :key="label" class="panel metric">
      <span>{{ label }}</span>
      <strong>{{ value }}</strong>
    </article>
  </div>

  <div class="stats-charts">
    <section class="panel chart">
      <header class="chart-heading">
        <h2>发布与成交趋势</h2>
        <div class="trend-period" role="group" aria-label="统计范围">
          <button
            v-for="period in [7, 30]"
            :key="period"
            type="button"
            :aria-pressed="days === period"
            :disabled="trendLoading"
            @click="selectDays(period)"
          >近 {{ period }} 天</button>
        </div>
      </header>
      <p v-if="trendLoading" class="muted" role="status">正在加载趋势…</p>
      <p v-else-if="trendError" class="error" role="alert">
        {{ trendError }}
        <button type="button" @click="loadTrend">重试</button>
      </p>
      <StatsTrendChart v-else-if="trend.length" :items="trend" />
      <p v-else class="muted">暂无趋势数据</p>
    </section>

    <div class="distribution-charts">
      <section class="panel chart">
        <h2>在售商品分类分布</h2>
        <div v-for="item in categories" :key="item.category_id" class="bar-row">
          <span>{{ item.category_name }}</span>
          <div class="bar-track" aria-hidden="true">
            <div class="bar" :style="{ width: (item.on_sale_count / categoryMax * 100) + '%' }"></div>
          </div>
          <b>{{ item.on_sale_count }} 件</b>
        </div>
        <p v-if="!categories.length && !summaryError" class="muted" role="status">
          {{ loading ? '正在加载分类…' : '暂无分类数据' }}
        </p>
      </section>

      <section class="panel chart">
        <h2>商品价格区间分布</h2>
        <p class="muted">在售及已预订商品 · 单位：元</p>
        <p v-if="pricesError" class="error" role="alert">{{ pricesError }}</p>
        <div v-for="item in priceRanges" :key="item.price_range" class="bar-row">
          <span>{{ item.price_range }}</span>
          <div class="bar-track" aria-hidden="true">
            <div class="bar" :style="{ width: (item.product_count / priceMax * 100) + '%' }"></div>
          </div>
          <b>{{ item.product_count }} 件</b>
        </div>
        <p v-if="!priceRanges.length && !pricesError" class="muted" role="status">
          {{ loading ? '正在加载价格区间…' : '暂无价格区间数据' }}
        </p>
      </section>
    </div>
    <StatsExtras ref="extras" />
  </div>
</template>

<style scoped>
.stats-charts, .distribution-charts { display: grid; gap: 18px; }
.distribution-charts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.chart-heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
.chart-heading h2 { margin: 0; }
.trend-period { display: flex; gap: 6px; }
.trend-period button { padding: 7px 12px; font-size: 13px; }
.trend-period button[aria-pressed="true"] { background: #edf2ff; color: #294cc8; border-color: #c5d2ff; }
@media (max-width: 900px) {
  .distribution-charts { grid-template-columns: 1fr; }
}
</style>
