<script setup>
import { computed } from "vue";

const props = defineProps({
  class: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <div :class="['skeleton', props.class]" v-bind="$attrs"></div>
</template>

<style scoped>
.skeleton {
  background-color: var(--muted);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  border-radius: 0;
}

.dark .skeleton {
  background-color: var(--muted);
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
