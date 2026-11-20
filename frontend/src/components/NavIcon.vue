<script setup>
defineProps({ name: { type: String, required: true } })
const paths = {
  shop: ['M3 10l2-6h14l2 6', 'M3 10a3 3 0 006 0 3 3 0 006 0 3 3 0 006 0', 'M5 13v7h14v-7', 'M10 20v-5h4v5'],
  publish: ['M8 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2h-3', 'M8 3h8', 'M12 8v8', 'M8 12h8'],
  heart: ['M20.8 4.6a5.5 5.5 0 00-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 00-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 000-7.8Z'],
  orders: ['M8 4H5a1 1 0 00-1 1v15a1 1 0 001 1h14a1 1 0 001-1V5a1 1 0 00-1-1h-3', 'M8 3h8v4H8z', 'M8 12h8', 'M8 16h5'],
  chart: ['M4 3v18h17', 'M8 16v-5', 'M13 16V6', 'M18 16V9'],
  user: ['M16 7a4 4 0 11-8 0 4 4 0 018 0Z', 'M4 21v-2a8 8 0 0116 0v2'],
}
</script>

<template>
  <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
    <path v-for="(path, index) in paths[name]" :key="index" :d="path" />
  </svg>
</template>

<style scoped>
.nav-icon { width: 20px; height: 20px; flex: 0 0 20px; }
</style>
