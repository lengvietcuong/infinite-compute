<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div
      :class="[
        'modal-content',
        'w-full',
        'bg-background',
        'text-foreground',
        'relative',
        'border',
        'border-color',
        'shadow-xl',
        'rounded-lg',
        'mx-4',
        modalSizeClass,
      ]"
    >
      <div class="modal-header">
        <slot name="header">
          <h3 class="text-lg font-bold font-mono">{{ title }}</h3>
        </slot>
        <button @click="$emit('close')" class="btn btn-ghost btn-icon-sm">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <slot />
      </div>
      <div v-if="$slots.footer" class="modal-footer">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-content {
  max-width: 640px;
}

.modal-content.modal-large {
  max-width: 900px;
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

.modal-body {
  padding: 0 1.5rem 1rem 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: 0.75rem 1.5rem 1rem 1.5rem;
  border-top: 1px solid var(--border);
}
</style>

<script setup>
import { computed } from "vue";

const props = defineProps({
  isOpen: Boolean,
  title: String,
  size: {
    type: String,
    default: "default",
    validator: (value) => ["default", "large"].includes(value),
  },
});

defineEmits(["close"]);

const modalSizeClass = computed(() => {
  return props.size === "large" ? "modal-large" : "";
});
</script>
