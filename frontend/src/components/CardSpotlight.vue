<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  radius: {
    type: Number,
    default: 350,
  },
  color: {
    type: String,
    default: "#262626",
  },
  gradientColor: {
    type: String,
    default: "white",
  },
});

const mouseX = ref(0);
const mouseY = ref(0);
const isHovering = ref(false);

function handleMouseMove(event) {
  const { currentTarget, clientX, clientY } = event;
  const { left, top } = currentTarget.getBoundingClientRect();
  mouseX.value = clientX - left;
  mouseY.value = clientY - top;
}

function handleMouseEnter() {
  isHovering.value = true;
}

function handleMouseLeave() {
  isHovering.value = false;
}

const spotlightStyle = computed(() => {
  return {
    backgroundColor: props.color,
    maskImage: `radial-gradient(${props.radius}px circle at ${mouseX.value}px ${mouseY.value}px, ${props.gradientColor}, transparent 80%)`,
    WebkitMaskImage: `radial-gradient(${props.radius}px circle at ${mouseX.value}px ${mouseY.value}px, ${props.gradientColor}, transparent 80%)`,
  };
});
</script>

<template>
  <div
    class="card-spotlight group"
    @mousemove="handleMouseMove"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <div
      class="spotlight-overlay"
      :class="{ 'opacity-100': isHovering, 'opacity-0': !isHovering }"
      :style="spotlightStyle"
    ></div>
    <slot></slot>
  </div>
</template>

<style scoped>
.card-spotlight {
  position: relative;
  border-radius: inherit;
}

.spotlight-overlay {
  pointer-events: none;
  position: absolute;
  inset: 0;
  z-index: 0;
  transition: opacity 300ms ease;
  border-radius: inherit;
}

.opacity-100 {
  opacity: 1;
}

.opacity-0 {
  opacity: 0;
}
</style>
