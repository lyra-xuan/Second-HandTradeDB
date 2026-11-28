<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { api, auth, upload } from '../api'
import { imageUploadError, safeImage } from '../domain'

const form = reactive({ nickname: '', avatar: '', contact: '' })
const error = ref('')
const notice = ref('')
const saving = ref(false)
const uploading = ref(false)
const ready = ref(false)
const avatarFailed = ref(false)
const avatarSource = computed(() => safeImage(form.avatar))
watch(avatarSource, () => { avatarFailed.value = false })

async function load() {
  error.value = ''
  try {
    auth.user = await api('/auth/me')
    form.nickname = auth.user.nickname
    form.avatar = auth.user.avatar || ''
    form.contact = auth.user.contact || ''
    ready.value = true
  } catch (e) {
    error.value = e.message
  }
}

async function selectAvatar(event) {
  const input = event.target
  const file = input.files?.[0]
  input.value = ''
  if (!file || uploading.value || saving.value) return
  notice.value = ''
  error.value = imageUploadError([file])
  if (error.value) return

  uploading.value = true
  try {
    const result = await upload('/uploads', [file])
    const url = result.urls?.[0]
    if (!safeImage(url)) throw new Error('上传未返回有效的图片地址')
    form.avatar = url
    notice.value = '头像已上传，点击保存资料后生效'
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
  }
}

async function save() {
  if (saving.value || uploading.value) return
  saving.value = true
  error.value = ''
  notice.value = ''
  try {
    if (form.avatar && !avatarSource.value) throw new Error('头像须为 http(s) 地址或站内图片路径')
    auth.user = await api('/auth/me', {
      method: 'PATCH',
      body: { nickname: form.nickname, avatar: form.avatar || null, contact: form.contact || null },
    })
    notice.value = '个人资料已保存'
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <header class="section-heading"><h1>个人资料</h1></header>
  <p v-if="error" class="error" role="alert">
    {{ error }} <button v-if="!ready" type="button" @click="load">重试</button>
  </p>
  <form v-if="ready" class="panel form-panel" @submit.prevent="save">
    <div class="profile-heading">
      <img v-if="avatarSource && !avatarFailed" class="avatar avatar-image" :src="avatarSource" alt="头像预览" @error="avatarFailed = true">
      <b v-else class="avatar">{{ form.nickname.slice(0, 1) }}</b>
      <div>
        <h2>{{ auth.user.nickname }}</h2>
        <p class="muted">{{ auth.user.is_admin ? '管理员' : '校园用户' }} · {{ auth.user.student_no }}</p>
      </div>
    </div>
    <label>邮箱<input :value="auth.user.email" disabled></label>
    <label>昵称<input v-model.trim="form.nickname" required maxlength="20"></label>
    <label>联系方式<input v-model.trim="form.contact" maxlength="100" placeholder="微信、QQ 或电话"></label>
    <label>选择本地头像
      <input type="file" accept="image/png,image/jpeg,image/webp,image/gif" :disabled="uploading || saving" @change="selectAvatar">
    </label>
    <label>头像地址<input v-model.trim="form.avatar" maxlength="255" placeholder="https://…" :disabled="uploading || saving"></label>
    <p v-if="notice" class="success" role="status">{{ notice }}</p>
    <button class="primary" :disabled="saving || uploading">{{ uploading ? '头像上传中…' : saving ? '保存中…' : '保存资料' }}</button>
  </form>
</template>

<style scoped>
.avatar-image { object-fit: cover; }
</style>
