<script setup>
import { computed } from "vue";

const props = defineProps({
  class: {
    type: String,
    default: "",
  },
  rounded: {
    type: Boolean,
    default: true,
  },
});
</script>

<template>
  <div :class="['skeleton', { 'skeleton-rounded': props.rounded }, props.class]" v-bind="$attrs"></div>
</template>

<style scoped>
.skeleton {
  background-color: var(--accent);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-rounded {
  border-radius: 0.375rem;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
