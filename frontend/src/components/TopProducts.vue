<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { formatPrice } from "../utils/format";
import SparklesCore from "./SparklesCore.vue";
import Skeleton from "./Skeleton.vue";

const router = useRouter();
const products = ref([]);
const loading = ref(true);
const shouldRender = ref(true);

const currentIndex = ref(0);
const visibleCount = ref(3);
const transitionName = ref("slide-next");

const updateVisibleCount = () => {
  if (window.innerWidth >= 1024) {
    visibleCount.value = 3;
  } else if (window.innerWidth >= 768) {
    visibleCount.value = 2;
  } else {
    visibleCount.value = 1;
  }
};

const fetchTopProducts = async () => {
  loading.value = true;
  try {
    const response = await fetch("/api/products/top-selling?limit=10");
    if (!response.ok) throw new Error("Failed to fetch top products");
    const data = await response.json();
    if (data && data.length > 0) {
      products.value = data;
      shouldRender.value = true;
    } else {
      shouldRender.value = false;
    }
  } catch (err) {
    console.error(err);
    shouldRender.value = false;
  } finally {
    loading.value = false;
  }
};

const visibleProducts = computed(() => {
  const items = [];
  for (let i = 0; i < visibleCount.value; i++) {
    const index = (currentIndex.value + i) % products.value.length;
    items.push(products.value[index]);
  }
  return items;
});

const next = () => {
  transitionName.value = "slide-next";
  currentIndex.value = (currentIndex.value + 1) % products.value.length;
};

const prev = () => {
  transitionName.value = "slide-prev";
  currentIndex.value =
    (currentIndex.value - 1 + products.value.length) % products.value.length;
};

onMounted(() => {
  fetchTopProducts();
  updateVisibleCount();
  window.addEventListener("resize", updateVisibleCount);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateVisibleCount);
});

const navigateToProduct = (id) => {
  router.push(`/products/${id}`);
};
</script>

<template>
  <section v-if="shouldRender" class="top-products-section">
    <div class="gradient-light center"></div>
    <div class="sparkles-wrapper">
      <SparklesCore
        id="tsparticles-top-products"
        background="transparent"
        :minSize="0.6"
        :maxSize="1.4"
        :particleDensity="100"
        class="w-full h-full fade-mask"
        particleColor="#FFFFFF"
      />
    </div>
    <div class="container content-container">
      <h2 class="section-title">Top Products</h2>

      <div v-if="loading" class="carousel-container">
        <!-- Navigation Buttons -->
        <button class="nav-btn prev-btn" disabled aria-label="Previous">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
        </button>

        <div class="carousel-viewport">
          <div class="carousel-track">
            <div
              v-for="n in visibleCount"
              :key="n"
              class="carousel-item-wrapper"
              :style="{
                width: `${100 / visibleCount}%`,
                flex: `0 0 ${100 / visibleCount}%`,
              }"
            >
              <div class="product-card glass-card">
                <div class="corner-borders">
                  <span class="corner top-left"></span>
                  <span class="corner top-right"></span>
                  <span class="corner bottom-left"></span>
                  <span class="corner bottom-right"></span>
                </div>
                <div class="card-image">
                  <Skeleton class="w-full h-full" />
                </div>
                <div class="card-content">
                  <div class="flex justify-between mb-2">
                    <Skeleton class="w-1/3 h-4" />
                    <Skeleton class="w-1/4 h-4" />
                  </div>
                  <Skeleton class="w-3/4 h-6 mb-2" />
                  <Skeleton class="w-full h-12" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <button class="nav-btn next-btn" disabled aria-label="Next">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>
      </div>

      <div v-else-if="products.length > 0" class="carousel-container">
        <!-- Navigation Buttons -->
        <button class="nav-btn prev-btn" @click="prev" aria-label="Previous">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
        </button>

        <div class="carousel-viewport">
          <transition-group
            :name="transitionName"
            tag="div"
            class="carousel-track"
          >
            <div
              v-for="product in visibleProducts"
              :key="product.id"
              class="carousel-item-wrapper"
              :style="{
                width: `${100 / visibleCount}%`,
                flex: `0 0 ${100 / visibleCount}%`,
              }"
            >
              <article
                class="product-card glass-card"
                @click="navigateToProduct(product.id)"
              >
                <div class="corner-borders">
                  <span class="corner top-left"></span>
                  <span class="corner top-right"></span>
                  <span class="corner bottom-left"></span>
                  <span class="corner bottom-right"></span>
                </div>
                <div class="card-image">
                  <img
                    :src="product.image_url || '/images/default-product.webp'"
                    :alt="product.name"
                    loading="lazy"
                    @error="
                      $event.target.src =
                        'https://placehold.co/600x400/1a1a1a/FFF?text=Product'
                    "
                  />
                  <div class="price-tag">${{ formatPrice(product.price) }}</div>
                </div>
                <div class="card-content">
                  <div class="card-meta">
                    <span class="architecture" v-if="product.architecture">
                      {{ product.architecture }}
                    </span>
                    <span class="rating" v-if="product.average_rating">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                        stroke="none"
                        class="text-warning"
                      >
                        <polygon
                          points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                        />
                      </svg>
                      {{ product.average_rating.toFixed(1) }} ({{
                        product.review_count
                      }})
                    </span>
                  </div>
                  <h3 class="card-title">{{ product.name }}</h3>
                  <p class="card-excerpt">
                    {{
                      product.description
                        ? product.description.substring(0, 80) + "..."
                        : ""
                    }}
                  </p>
                </div>
              </article>
            </div>
          </transition-group>
        </div>

        <button class="nav-btn next-btn" @click="next" aria-label="Next">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.top-products-section {
  padding: var(--spacing-2xl) 0;
  padding-top: 5rem;
  background-color: var(--background);
  position: relative;
  overflow: hidden;
}

.sparkles-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

.fade-mask {
  mask-image: radial-gradient(ellipse at center, white 40%, transparent 80%);
  -webkit-mask-image: radial-gradient(
    ellipse at center,
    white 40%,
    transparent 80%
  );
}

.content-container {
  position: relative;
  z-index: 1;
}

.gradient-light {
  position: absolute;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--primary), transparent 90%) 0%,
    transparent 70%
  );
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

.gradient-light.center {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80vw;
  height: 40vw;
}

.section-title {
  font-size: var(--text-4xl);
  text-align: center;
  margin-bottom: 1.25rem;
  background: linear-gradient(
    to right,
    var(--foreground),
    var(--muted-foreground)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .section-title {
    font-size: var(--text-3xl);
    margin-bottom: 0.75rem;
  }
}

.carousel-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.carousel-viewport {
  overflow: hidden;
  width: 100%;
  margin: 0;
}

.carousel-track {
  display: flex;
  width: 100%;
  position: relative;
}

.carousel-item-wrapper {
  padding: var(--spacing-md) var(--spacing-sm);
  box-sizing: border-box;
}

.product-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform var(--transition-slow) ease,
    box-shadow var(--transition-slow) ease,
    border-color var(--transition-slow) ease;
  cursor: pointer;
  background: color-mix(in srgb, var(--card), transparent 80%);
  border: 1px solid var(--border);
  height: 100%;
  width: 100%;
  position: relative;
}

.corner-borders {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}

.corner {
  position: absolute;
  width: 24px;
  height: 24px;
  border: 3px solid var(--primary);
  opacity: 0;
  transition: opacity var(--transition-slow) ease;
}

.corner.top-left {
  top: -1px;
  left: -1px;
  border-bottom: 0;
  border-right: 0;
}

.corner.top-right {
  top: -1px;
  right: -1px;
  border-bottom: 0;
  border-left: 0;
}

.corner.bottom-left {
  bottom: -1px;
  left: -1px;
  border-top: 0;
  border-right: 0;
}

.corner.bottom-right {
  bottom: -1px;
  right: -1px;
  border-top: 0;
  border-left: 0;
}

.product-card:hover {
  transform: translateY(-5px);
  border-color: transparent;
}

.product-card:hover .corner {
  opacity: var(--opacity-hover);
}

.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
  background-color: var(--card);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slower) ease;
}

.product-card:hover .card-image img {
  transform: scale(1.05);
}

.price-tag {
  position: absolute;
  bottom: var(--spacing-sm);
  right: var(--spacing-sm);
  background: var(--primary);
  color: var(--primary-foreground);
  padding: var(--spacing-xs) var(--spacing-sm);
  font-weight: 700;
  font-family: var(--font-mono);
  border-radius: var(--radius);
  font-size: var(--text-sm);
}

.card-content {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 0.75rem;
  color: var(--muted-foreground);
  margin-bottom: var(--spacing-sm);
  font-family: var(--font-mono);
}

.rating {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.text-warning {
  color: var(--warning);
}

.card-title {
  font-size: var(--text-lg);
  margin-bottom: var(--spacing-sm);
  line-height: 1.3;
  font-weight: 600;
  color: var(--foreground);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-excerpt {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
  margin-bottom: var(--spacing-md);
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.nav-btn {
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--foreground);
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  z-index: 10;
  flex-shrink: 0;
}

.nav-btn:hover {
  background: var(--card);
  border-color: var(--border);
}

.nav-btn:hover svg {
  color: var(--primary);
  stroke: var(--primary);
}

.nav-btn:disabled {
  opacity: var(--opacity-disabled);
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 32px;
    height: 32px;
  }

  .prev-btn {
    left: -1rem;
  }

  .next-btn {
    right: -1rem;
  }

  .carousel-viewport {
    margin: 0;
  }
}

.slide-next-move,
.slide-next-enter-active,
.slide-next-leave-active,
.slide-prev-move,
.slide-prev-enter-active,
.slide-prev-leave-active {
  transition: all var(--transition-slower) ease;
}

.slide-next-leave-active {
  position: absolute;
  top: 0;
  left: 0;
}

.slide-prev-leave-active {
  position: absolute;
  top: 0;
  right: 0;
}

.slide-next-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.slide-next-leave-to {
  transform: translateX(-100%);
}

.slide-prev-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}
.slide-prev-leave-to {
  transform: translateX(100%);
}
</style>
