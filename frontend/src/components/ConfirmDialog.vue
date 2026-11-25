<script setup>
import { onMounted, ref } from 'vue'

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  confirmLabel: { type: String, default: '确认' },
})
const emit = defineEmits(['confirm', 'cancel'])
const dialog = ref(null)

onMounted(() => dialog.value.showModal())

function finish(result) {
  dialog.value.close()
  emit(result)
}
</script>

<template>
  <dialog
    ref="dialog"
    class="confirm-dialog"
    aria-labelledby="confirm-title"
    :aria-describedby="description ? 'confirm-description' : undefined"
    @cancel.prevent="finish('cancel')"
  >
    <h2 id="confirm-title">{{ title }}</h2>
    <p v-if="description" id="confirm-description">{{ description }}</p>
    <div class="actions">
      <button type="button" autofocus @click="finish('cancel')">取消</button>
      <button type="button" class="primary" @click="finish('confirm')">{{ confirmLabel }}</button>
    </div>
  </dialog>
</template>

<style scoped>
.confirm-dialog {
  width: min(420px, calc(100% - 32px));
  max-width: none;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: #fff;
  color: #24324b;
  box-shadow: 0 16px 48px #23396c30;
  color-scheme: light;
}
.confirm-dialog::backdrop { background: #23345738; }
h2 { font-size: 19px; margin-bottom: 0; }
p { color: var(--muted); margin: 8px 0 0; }
.actions { justify-content: flex-end; margin-top: 24px; }
</style>
