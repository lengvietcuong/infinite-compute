<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const products = ref([]);
const loading = ref(true);
const shouldRender = ref(true);

const currentIndex = ref(0);
const visibleCount = ref(3);

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

const next = () => {
  if (currentIndex.value + visibleCount.value < products.value.length) {
    currentIndex.value++;
  } else {
    currentIndex.value = 0;
  }
};

const prev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  } else {
    currentIndex.value = products.value.length - visibleCount.value;
    if (currentIndex.value < 0) currentIndex.value = 0;
  }
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

const formatPrice = (price) => {
  return parseFloat(price).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};
</script>

<template>
  <section v-if="shouldRender" class="top-products-section">
    <div class="container">
      <h2 class="section-title">Top Selling Products</h2>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
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
          <div
            class="carousel-track"
            :style="{
              transform: `translateX(-${currentIndex * (100 / visibleCount)}%)`,
            }"
          >
            <div
              v-for="product in products"
              :key="product.id"
              class="carousel-item-wrapper"
              :style="{ flex: `0 0 ${100 / visibleCount}%` }"
            >
              <article
                class="product-card glass-card"
                @click="navigateToProduct(product.id)"
              >
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
          </div>
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
  padding: 4rem 0;
  background-color: var(--background);
}

.section-title {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 2rem;
  background: linear-gradient(
    to right,
    var(--foreground),
    var(--muted-foreground)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.carousel-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.carousel-viewport {
  overflow: hidden;
  width: 100%;
  margin: 0 1rem; /* Space for buttons */
}

.carousel-track {
  display: flex;
  transition: transform 0.5s ease-in-out;
  width: 100%;
}

.carousel-item-wrapper {
  padding: 0 0.75rem;
  /* This padding creates the gap between cards.
       Since we wrap every item, two adjacent items will have 0.75 + 0.75 = 1.5rem gap.
    */
  box-sizing: border-box;
  /* Flex basis is set inline */
}

.product-card {
  /* Shared card styles (copied) */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  cursor: pointer;
  background: color-mix(in srgb, var(--card), transparent 80%);
  border: 1px solid var(--border);
  height: 100%;
  width: 100%; /* Fill wrapper */
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
  border-color: var(--primary);
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
  transition: transform 0.5s ease;
}

.product-card:hover .card-image img {
  transform: scale(1.05);
}

.price-tag {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: var(--primary);
  color: var(--primary-foreground);
  padding: 0.25rem 0.5rem;
  font-weight: 700;
  font-family: var(--font-mono);
  border-radius: var(--radius);
  font-size: 0.9rem;
}

.card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--muted-foreground);
  margin-bottom: 0.5rem;
  font-family: var(--font-mono);
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.text-warning {
  color: #f59e0b;
}

.card-title {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  font-weight: 600;
  color: var(--foreground);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-excerpt {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  margin-bottom: 1rem;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Nav Buttons */
.nav-btn {
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--foreground);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
  flex-shrink: 0;
}

.nav-btn:hover {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
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
</style>
