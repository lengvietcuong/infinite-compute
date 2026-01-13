<template>
  <div class="relative w-full">
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="flex h-10 w-full items-center justify-between border border-color bg-transparent px-3 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 appearance-none pr-8"
      :class="className"
      style="line-height: 2rem;"
    >
      <slot />
    </select>
    <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none text-muted-foreground">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4 opacity-50"><path d="m6 9 6 6 6-6"/></svg>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  className: {
    type: String,
    default: ''
  }
})
defineEmits(['update:modelValue'])
</script>
