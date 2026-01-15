<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div
      class="modal-content w-full bg-background text-foreground relative border border-color shadow-xl rounded-lg mx-4"
    >
      <div class="modal-header">
        <h3 class="text-lg font-bold font-mono">{{ title }}</h3>
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
      <div class="modal-content-padding">
        <p>{{ message }}</p>
        <div class="modal-actions">
          <button @click="$emit('close')" :class="buttonClass">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-content {
  max-width: 480px;
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

.modal-content-padding {
  padding: 0 1.5rem 1.5rem;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
</style>

<script setup>
import { computed } from "vue";

const props = defineProps({
  isOpen: Boolean,
  title: String,
  message: String,
  variant: {
    type: String,
    default: "default",
    validator: (value) => ["default", "destructive"].includes(value),
  },
});

defineEmits(["close"]);

const buttonClass = computed(() => {
  return props.variant === "destructive"
    ? "btn btn-destructive"
    : "btn btn-primary";
});
</script>
