<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";

const props = defineProps({
  blur: { type: Number, default: 0 },
  inactiveZone: { type: Number, default: 0.7 },
  proximity: { type: Number, default: 0 },
  spread: { type: Number, default: 20 },
  variant: { type: String, default: "default" },
  glow: { type: Boolean, default: false },
  movementDuration: { type: Number, default: 2 },
  borderWidth: { type: Number, default: 1 },
  disabled: { type: Boolean, default: true }, // Defaults to true as in React code? No, usually effects are enabled. But snippet had disabled=true default. I'll stick to snippet.
});

const containerRef = ref(null);
const lastPosition = ref({ x: 0, y: 0 });
const animationFrameRef = ref(null);

function animate(from, to, options) {
  const duration = options.duration * 1000;
  const startTime = performance.now();

  // Cubic bezier(0.16, 1, 0.3, 1) approximation or simple ease out
  // Using a simple ease-out-expo-like curve for smoothness
  const easing = (t) => 1 - Math.pow(1 - t, 4);

  function frame(currentTime) {
    const elapsed = currentTime - startTime;
    if (elapsed >= duration) {
      options.onUpdate(to);
      return;
    }

    const progress = elapsed / duration;
    const easedProgress = easing(progress);
    const value = from + (to - from) * easedProgress;

    options.onUpdate(value);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

const handleMove = (e) => {
  if (!containerRef.value) return;

  if (animationFrameRef.value) {
    cancelAnimationFrame(animationFrameRef.value);
  }

  animationFrameRef.value = requestAnimationFrame(() => {
    const element = containerRef.value;
    if (!element) return;

    const { left, top, width, height } = element.getBoundingClientRect();
    const mouseX = e?.clientX ?? lastPosition.value.x; // Use clientX/Y from event or last pos. Note: e.x is alias for clientX in some browsers? React uses e.x? Native event is clientX.
    const mouseY = e?.clientY ?? lastPosition.value.y;

    if (e) {
      lastPosition.value = { x: mouseX, y: mouseY };
    }

    const center = [left + width * 0.5, top + height * 0.5];
    const distanceFromCenter = Math.hypot(
      mouseX - center[0],
      mouseY - center[1]
    );
    const inactiveRadius = 0.5 * Math.min(width, height) * props.inactiveZone;

    if (distanceFromCenter < inactiveRadius) {
      element.style.setProperty("--active", "0");
      return;
    }

    const isActive =
      mouseX > left - props.proximity &&
      mouseX < left + width + props.proximity &&
      mouseY > top - props.proximity &&
      mouseY < top + height + props.proximity;

    element.style.setProperty("--active", isActive ? "1" : "0");

    if (!isActive) return;

    const currentAngle =
      parseFloat(element.style.getPropertyValue("--start")) || 0;

    // atan2 returns radians, convert to deg.
    // +90 to adjust since CSS gradients usually start from top or right depending on syntax.
    let targetAngle =
      (180 * Math.atan2(mouseY - center[1], mouseX - center[0])) / Math.PI + 90;

    const angleDiff = ((targetAngle - currentAngle + 180) % 360) - 180;
    const newAngle = currentAngle + angleDiff;

    animate(currentAngle, newAngle, {
      duration: props.movementDuration,
      onUpdate: (value) => {
        element.style.setProperty("--start", String(value));
      },
    });
  });
};

onMounted(() => {
  if (props.disabled) return;
  window.addEventListener("scroll", handleMove, { passive: true });
  document.body.addEventListener("pointermove", handleMove, { passive: true });
});

onUnmounted(() => {
  if (animationFrameRef.value) cancelAnimationFrame(animationFrameRef.value);
  window.removeEventListener("scroll", handleMove);
  document.body.removeEventListener("pointermove", handleMove);
});

// Watch disabled prop to add/remove listeners if it changes dynamically (optional but good practice)
watch(
  () => props.disabled,
  (newVal) => {
    if (newVal) {
      window.removeEventListener("scroll", handleMove);
      document.body.removeEventListener("pointermove", handleMove);
    } else {
      window.addEventListener("scroll", handleMove, { passive: true });
      document.body.addEventListener("pointermove", handleMove, {
        passive: true,
      });
    }
  }
);

const gradientStyle = computed(() => {
  const defaultGradient = `
              radial-gradient(circle, #dd7bbb 10%, #dd7bbb00 20%),
              radial-gradient(circle at 40% 40%, #d79f1e 5%, #d79f1e00 15%),
              radial-gradient(circle at 60% 60%, #5a922c 10%, #5a922c00 20%), 
              radial-gradient(circle at 40% 60%, #4c7894 10%, #4c789400 20%),
              repeating-conic-gradient(
                from 236.84deg at 50% 50%,
                #dd7bbb 0%,
                #d79f1e calc(25% / var(--repeating-conic-gradient-times)),
                #5a922c calc(50% / var(--repeating-conic-gradient-times)), 
                #4c7894 calc(75% / var(--repeating-conic-gradient-times)),
                #dd7bbb calc(100% / var(--repeating-conic-gradient-times))
              )
    `;
  const whiteGradient = `
                repeating-conic-gradient(
                from 236.84deg at 50% 50%,
                var(--black),
                var(--black) calc(25% / var(--repeating-conic-gradient-times))
              )
    `;
  const primaryGradient = `
             repeating-conic-gradient(
                from 236.84deg at 50% 50%,
                var(--primary) 0%,
                var(--primary) calc(100% / var(--repeating-conic-gradient-times))
              )
  `;
  if (props.variant === "white") return whiteGradient;
  if (props.variant === "primary") return primaryGradient;
  return defaultGradient;
});
</script>

<template>
  <!-- Fallback border container when disabled -->
  <div
    class="glowing-effect-border"
    :class="{
      show: props.glow,
      'border-white': props.variant === 'white',
      'visible-block': props.disabled,
    }"
  ></div>

  <!-- Active glow container -->
  <div
    ref="containerRef"
    class="glowing-effect-container"
    :class="{
      'opacity-100': props.glow,
      hidden: props.disabled,
      [props.className]: true,
    }"
    :style="{
      '--blur': `${props.blur}px`,
      '--spread': props.spread,
      '--start': '0',
      '--active': '0',
      '--glowingeffect-border-width': `${props.borderWidth}px`,
      '--repeating-conic-gradient-times': '5',
      '--gradient': gradientStyle,
    }"
  >
    <div class="glow"></div>
  </div>
</template>

<style scoped>
.glowing-effect-border {
  pointer-events: none;
  position: absolute;
  inset: -1px;
  display: none;
  border-radius: inherit;
  border: 1px solid var(--border);
  opacity: 0;
  transition: opacity 300ms;
}
.glowing-effect-border.show {
  opacity: 1;
}
.glowing-effect-border.border-white {
  border-color: white;
}
.glowing-effect-border.visible-block {
  display: block !important;
}

.glowing-effect-container {
  pointer-events: none;
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 1; /* Default opacity-100 from snippet, though snippet base had opacity-100 AND hidden? Wait. No, second div has opacity-100 by default. */
  transition: opacity 300ms;
}
.glowing-effect-container.hidden {
  display: none !important;
}

.glow {
  border-radius: inherit;
  width: 100%;
  height: 100%;
}

.glow::after {
  content: "";
  border-radius: inherit;
  position: absolute;
  inset: calc(-1 * var(--glowingeffect-border-width));
  border: var(--glowingeffect-border-width) solid transparent;
  background: var(--gradient);
  background-attachment: fixed;
  opacity: calc(var(--active) * 0.7);
  transition: opacity 300ms;

  mask-clip: padding-box, border-box;
  mask-composite: intersect;
  -webkit-mask-clip: padding-box, border-box;
  -webkit-mask-composite: source-in; /* 'intersect' equivalent for some browsers? No, standard is differentiate mask-image. */

  mask-image: linear-gradient(transparent, transparent),
    conic-gradient(
      from calc((var(--start) - var(--spread)) * 1deg),
      transparent 0deg,
      white,
      transparent calc(var(--spread) * 2deg)
    );
  -webkit-mask-image: linear-gradient(transparent, transparent),
    conic-gradient(
      from calc((var(--start) - var(--spread)) * 1deg),
      transparent 0deg,
      white,
      transparent calc(var(--spread) * 2deg)
    );
}
</style>
