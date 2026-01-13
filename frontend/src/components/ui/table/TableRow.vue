<template>
  <tr class="hover:bg-muted/50 border-b border-color transition-colors data-[state=selected]:bg-muted">
    <slot />
  </tr>
</template>

<style scoped>
tr {
  border-color: var(--border);
}
</style>
