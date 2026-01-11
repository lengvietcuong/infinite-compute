<script setup>
import { ref, onMounted } from "vue";

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  direction: {
    type: String,
    default: "left",
  },
  speed: {
    type: String,
    default: "fast",
  },
  pauseOnHover: {
    type: Boolean,
    default: true,
  },
});

const containerRef = ref(null);
const scrollerRef = ref(null);
const start = ref(false);

onMounted(() => {
  addAnimation();
});

function addAnimation() {
  if (containerRef.value && scrollerRef.value) {
    const container = containerRef.value;

    // Set direction
    if (props.direction === "left") {
      container.style.setProperty("--animation-direction", "forwards");
    } else {
      container.style.setProperty("--animation-direction", "reverse");
    }

    // Set speed
    if (props.speed === "fast") {
      container.style.setProperty("--animation-duration", "20s");
    } else if (props.speed === "normal") {
      container.style.setProperty("--animation-duration", "40s");
    } else {
      container.style.setProperty("--animation-duration", "80s");
    }

    start.value = true;
  }
}
</script>

<template>
  <div ref="containerRef" class="scroller scroller-mask">
    <ul
      ref="scrollerRef"
      class="scroll-list"
      :class="{
        'animate-scroll': start,
        'pause-animation': pauseOnHover,
      }"
    >
      <!-- Render Original Items -->
      <li v-for="(item, idx) in items" :key="item.name + idx" class="card-item">
        <div class="custom-card">
          <blockquote>
            <span class="quote-text"> "{{ item.quote }}" </span>
            <div class="author-info">
              <div class="profile-image-container">
                <img :src="item.image" :alt="item.name" class="profile-image" />
              </div>
              <span class="author-details">
                <span class="author-name">
                  {{ item.name }}
                </span>
                <span class="author-title">
                  {{ item.title }}
                </span>
              </span>
            </div>
          </blockquote>
        </div>
      </li>

      <!-- Render Duplicated Items for Loop -->
      <li
        v-for="(item, idx) in items"
        :key="item.name + idx + '-dup'"
        class="card-item"
      >
        <div class="custom-card">
          <blockquote>
            <span class="quote-text"> "{{ item.quote }}" </span>
            <div class="author-info">
              <div class="profile-image-container">
                <img :src="item.image" :alt="item.name" class="profile-image" />
              </div>
              <span class="author-details">
                <span class="author-name">
                  {{ item.name }}
                </span>
                <span class="author-title">
                  {{ item.title }}
                </span>
              </span>
            </div>
          </blockquote>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.scroller {
  position: relative;
  z-index: 20;
  max-width: 80rem; /* max-w-7xl approx */
  overflow: hidden;
  width: 100%;
  margin: 0 auto;
}

.scroll-list {
  display: flex;
  min-width: 100%;
  width: max-content;
  flex-shrink: 0;
  flex-wrap: nowrap;
  gap: 1rem;
  padding: 1rem 0;
  list-style-type: none; /* Remove bullet points */
  margin: 0;
}

.card-item {
  flex-shrink: 0;
}

.custom-card {
  width: 350px;
  max-width: 100%;
  position: relative;
  border-radius: 0;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--card), transparent 95%);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  padding: 1rem 1.5rem;
}

@media (min-width: 1280px) {
  .custom-card {
    width: 450px;
    padding: 1.5rem 2rem;
  }
}

blockquote {
  position: relative;
  margin: 0;
}

.quote-text {
  display: block;
  font-size: 0.875rem; /* text-sm */
  line-height: 1.6;
  font-weight: 400;
  color: var(--foreground);
  margin-top: 0;
}

.author-info {
  margin-top: 1.5rem; /* mt-6 */
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.profile-image-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid var(--border);
}

.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.author-name {
  font-size: 0.875rem;
  line-height: 1.6;
  font-weight: 500;
  color: var(--primary);
}

.author-title {
  font-size: 0.75rem;
  line-height: 1.6;
  font-weight: 400;
  color: var(--muted-foreground);
  opacity: 0.8;
}
</style>
