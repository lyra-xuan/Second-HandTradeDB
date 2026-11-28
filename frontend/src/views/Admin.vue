<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, auth } from '../api'
import { date } from '../domain'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const router = useRouter()
const userId = ref('')
const productId = ref(null)
const pending = ref(null)
const saving = ref(false)
const statusError = ref('')
const notice = ref('')
const logs = ref([])
const page = ref(1)
const total = ref(0)
const pageSize = 20
const loading = ref(false)
const logError = ref('')
const actions = { auto_user_status: '用户状态变更（自动审计）' }

async function loadLogs(nextPage) {
  if (loading.value) return
  loading.value = true
  logError.value = ''
  try {
    const result = await api('/admin/logs?page=' + nextPage + '&page_size=' + pageSize)
    logs.value = result.items
    total.value = result.total
    page.value = result.page
  } catch (error) {
    logError.value = error.message
  } finally {
    loading.value = false
  }
}

function requestChange(status) {
  if (saving.value) return
  notice.value = ''
  statusError.value = ''
  const id = Number(userId.value)
  if (!Number.isSafeInteger(id) || id < 1) {
    statusError.value = '请输入有效的用户 ID'
    return
  }
  if (id === auth.user?.id) {
    statusError.value = '不能修改自己的账号状态'
    return
  }
  pending.value = { id, status }
}

async function changeStatus() {
  const change = pending.value
  pending.value = null
  if (!change || saving.value) return
  saving.value = true
  try {
    await api('/admin/users/' + change.id + '/status', {
      method: 'PATCH',
      body: { status: change.status },
    })
    notice.value = '用户 #' + change.id + (change.status === 0 ? ' 已封禁' : ' 已解封')
    await loadLogs(1)
  } catch (error) {
    statusError.value = error.message
  } finally {
    saving.value = false
  }
}

function openProduct() {
  if (Number.isSafeInteger(productId.value) && productId.value > 0) {
    router.push('/products/' + productId.value)
  }
}

onMounted(() => loadLogs(1))
</script>

<template>
  <header class="section-heading"><h1>管理中心</h1></header>
  <section class="panel form-panel">
    <h2>用户状态</h2>
    <label for="managed-user-id">用户 ID</label>
    <input id="managed-user-id" v-model="userId" type="number" min="1" step="1" :disabled="saving">
    <p v-if="statusError" class="error" role="alert">{{ statusError }}</p>
    <p v-if="notice" class="success" role="status">{{ notice }}</p>
    <div class="actions admin-actions">
      <button type="button" :disabled="saving || loading" @click="requestChange(0)">封禁</button>
      <button type="button" class="primary" :disabled="saving || loading" @click="requestChange(1)">解封</button>
    </div>
  </section>

  <form class="panel form-panel admin-product" @submit.prevent="openProduct">
    <h2>商品管理</h2>
    <label>商品 ID<input v-model.number="productId" type="number" min="1" max="9007199254740991" step="1" required></label>
    <button type="submit">打开商品详情</button>
  </form>

  <section class="panel admin-logs">
    <header class="section-heading">
      <h2>操作日志</h2>
      <button type="button" :disabled="loading || saving" @click="loadLogs(page)">刷新日志</button>
    </header>
    <p v-if="loading" class="muted" role="status">正在读取日志…</p>
    <p v-if="logError" class="error" role="alert">{{ logError }}</p>
    <div v-if="logs.length" class="table-scroll">
      <table class="data-table">
        <thead><tr><th scope="col">时间</th><th scope="col">操作</th><th scope="col">操作者</th><th scope="col">目标</th><th scope="col">详情</th></tr></thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ date(log.created_at) }}</td>
            <td>{{ actions[log.action] || log.action }}</td>
            <td>{{ log.admin_id == null ? '系统' : '#' + log.admin_id }}</td>
            <td>{{ log.target_type === 'user' ? '用户' : log.target_type }} #{{ log.target_id }}</td>
            <td>{{ log.detail || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else-if="!loading && !logError" class="muted">暂无操作日志</p>
    <div v-if="total > pageSize" class="pagination">
      <button type="button" :disabled="page <= 1 || loading || saving" @click="loadLogs(page - 1)">上一页</button>
      <span>{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
      <button type="button" :disabled="page * pageSize >= total || loading || saving" @click="loadLogs(page + 1)">下一页</button>
    </div>
  </section>

  <ConfirmDialog
    v-if="pending"
    :title="(pending.status === 0 ? '封禁' : '解封') + '用户 #' + pending.id + '？'"
    :confirm-label="pending.status === 0 ? '确认封禁' : '确认解封'"
    @cancel="pending = null"
    @confirm="changeStatus"
  />
</template>

<style scoped>
.admin-actions { margin-top: 16px; }
.admin-logs, .admin-product { margin-top: 20px; }
.admin-logs header { margin-top: 0; }
.admin-logs h2 { margin: 0; }
</style>
