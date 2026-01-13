<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content w-full bg-background text-foreground relative border border-color shadow-xl rounded-lg mx-4">
      <div class="modal-header">
        <h3 class="text-lg font-bold font-mono">{{ title }}</h3>
        <button @click="$emit('close')" class="btn btn-ghost btn-icon-sm">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.modal-content {
  max-width: 640px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem 0.75rem 1.5rem;
}

.modal-header button {
  color: var(--muted-foreground);
  transition: color var(--transition-base);
}

.modal-header button:hover {
  color: var(--foreground);
}
</style>

<script setup>
defineProps({
  isOpen: Boolean,
  title: String
})
defineEmits(['close'])
</script>
