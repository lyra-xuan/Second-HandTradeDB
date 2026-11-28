<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
})

const plot = { left: 38, top: 22, right: 620, bottom: 222 }
const series = [
  { key: 'new_products', label: '新增商品', color: '#3659e3', dash: undefined },
  { key: 'finished_orders', label: '完成订单', color: '#007c93', dash: '7 4' },
]
const step = computed(() => Math.max(1, Math.ceil(Math.max(
  0, ...props.items.flatMap(item => [item.new_products, item.finished_orders]),
) / 4)))
const ticks = computed(() => Array.from({ length: 5 }, (_, index) => step.value * index))
const dateIndexes = computed(() => {
  const last = props.items.length - 1
  return last <= 0 ? [0] : [...new Set(Array.from({ length: 5 }, (_, index) => Math.round(last * index / 4)))]
})

function x(index) {
  const width = plot.right - plot.left
  if (props.items.length === 1) return plot.left + width / 2
  return plot.left + index * width / (props.items.length - 1)
}
function y(value) {
  return plot.bottom - value * (plot.bottom - plot.top) / (step.value * 4)
}
function points(key) {
  return props.items.map((item, index) => x(index) + ',' + y(item[key])).join(' ')
}
</script>

<template>
  <div class="trend-legend" aria-hidden="true">
    <span v-for="item in series" :key="item.key">
      <i :style="{ borderColor: item.color, borderTopStyle: item.dash ? 'dashed' : 'solid' }"></i>
      {{ item.label }}
    </span>
  </div>

  <svg class="trend-plot" viewBox="0 0 650 256" role="img" aria-labelledby="stats-trend-title">
    <title id="stats-trend-title">每日新增商品和完成订单走势，具体数值可在每日数据中查看</title>
    <g v-for="tick in ticks" :key="tick">
      <line :x1="plot.left" :x2="plot.right" :y1="y(tick)" :y2="y(tick)" stroke="#e5eaf3" />
      <text :x="plot.left - 7" :y="y(tick) + 4" text-anchor="end">{{ tick }}</text>
    </g>
    <text
      v-for="index in dateIndexes"
      :key="index"
      :x="x(index)"
      :y="plot.bottom + 21"
      text-anchor="middle"
    >{{ items[index].stat_date }}</text>

    <g v-for="item in series" :key="item.key">
      <polyline
        :points="points(item.key)"
        fill="none"
        :stroke="item.color"
        :stroke-dasharray="item.dash"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        vector-effect="non-scaling-stroke"
      />
      <circle
        v-for="(point, index) in items"
        :key="point.stat_date"
        :cx="x(index)"
        :cy="y(point[item.key])"
        r="3"
        :fill="item.color"
      ><title>{{ point.stat_date }} · {{ item.label }} {{ point[item.key] }}</title></circle>
    </g>
  </svg>

  <details class="trend-data">
    <summary>查看每日数据</summary>
    <table>
      <thead><tr><th scope="col">日期</th><th scope="col">新增商品</th><th scope="col">完成订单</th></tr></thead>
      <tbody>
        <tr v-for="item in items" :key="item.stat_date">
          <th scope="row">{{ item.stat_date }}</th><td>{{ item.new_products }}</td><td>{{ item.finished_orders }}</td>
        </tr>
      </tbody>
    </table>
  </details>
</template>

<style scoped>
.trend-legend { display: flex; gap: 20px; flex-wrap: wrap; color: #465675; font-size: 13px; }
.trend-legend span { display: inline-flex; align-items: center; gap: 7px; }
.trend-legend i { width: 22px; border-top-width: 3px; }
.trend-plot { display: block; width: 100%; max-width: 940px; margin: 12px auto 0; }
.trend-plot text { fill: #536580; font-size: 14px; }
.trend-data { font-size: 13px; }
summary { cursor: pointer; color: #294cc8; }
table { width: 100%; margin-top: 12px; border-collapse: collapse; text-align: center; font-variant-numeric: tabular-nums; }
th, td { padding: 6px 8px; border-bottom: 1px solid var(--line); }
thead { background: #f5f7fb; }
</style>
