<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const product = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchProduct = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch(
      `http://localhost:8000/products/${route.params.id}`
    );

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("Product not found");
      }
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    product.value = data;
  } catch (err) {
    console.error("Failed to fetch product:", err);
    error.value = err.message || "Failed to load product details.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchProduct);

const goBack = () => {
  router.push("/products");
};

const formatPrice = (price) => {
  if (!price) return "0.00";
  return parseFloat(price).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const specs = computed(() => {
  if (!product.value) return [];

  const relevantSpecs = [
    { label: "Architecture", value: product.value.architecture },
    { label: "Product Line", value: product.value.product_line },
    { label: "Memory", value: product.value.memory },
    { label: "Memory Type", value: product.value.memory_type },
    { label: "CUDA Cores", value: product.value.cuda_cores },
    { label: "Tensor Cores", value: product.value.tensor_cores },
    { label: "RT Cores", value: product.value.rt_cores },
    { label: "Boost Clock", value: product.value.boost_clock },
    { label: "TDP", value: product.value.tdp },
    { label: "Memory Bandwidth", value: product.value.memory_bandwidth },
  ];

  return relevantSpecs.filter(
    (spec) => spec.value !== null && spec.value !== undefined
  );
});
</script>

<template>
  <div class="product-details-page container">
    <!-- Back Button -->
    <button
      type="button"
      @click="goBack"
      class="btn btn-link text-decoration-none mb-4 back-btn fade-in-up"
    >
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
        class="me-2"
      >
        <path d="m15 18-6-6 6-6" />
      </svg>
      Back to Products
    </button>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-5">
      <div class="alert alert-danger d-inline-block">
        {{ error }}
      </div>
      <div class="mt-3">
        <button type="button" @click="goBack" class="btn btn-outline-primary">
          Return to Store
        </button>
      </div>
    </div>

    <!-- Product Content -->
    <div v-else-if="product" class="product-content fade-in-up delay-100">
      <div class="row g-5">
        <!-- Image Section -->
        <div class="col-lg-6">
          <img
            :src="product.image_url || '/images/default-product.webp'"
            :alt="product.name"
            class="img-fluid product-image"
            @error="
              $event.target.src =
                'https://placehold.co/600x400/1a1a1a/FFF?text=Product'
            "
          />
        </div>

        <!-- Details Section -->
        <div class="col-lg-6">
          <div class="product-info">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span
                class="badge badge-outline badge-lg badge-secondary-bg"
                v-if="product.architecture"
              >
                {{ product.architecture }}
              </span>
              <div class="rating-badge" v-if="product.average_rating">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  stroke="none"
                  class="text-warning me-1"
                >
                  <polygon
                    points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                  />
                </svg>
                <span class="fw-bold">{{
                  product.average_rating.toFixed(1)
                }}</span>
                <span class="text-muted ms-1"
                  >({{ product.review_count }}
                  {{ product.review_count === 1 ? "review" : "reviews" }})</span
                >
              </div>
            </div>

            <h1 class="product-title mb-3">{{ product.name }}</h1>

            <div class="price-section price-section-mobile">
              <span class="currency">$</span>
              <span class="amount">{{ formatPrice(product.price) }}</span>
            </div>

            <p class="description mb-4">{{ product.description }}</p>

            <div class="actions mb-5">
              <div class="d-grid gap-2">
                <button
                  class="btn btn-primary btn-lg d-flex align-items-center justify-content-center gap-2"
                  :disabled="product.stock_quantity <= 0"
                >
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
                    <circle cx="9" cy="21" r="1" />
                    <circle cx="20" cy="21" r="1" />
                    <path
                      d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
                    />
                  </svg>
                  {{
                    product.stock_quantity > 0 ? "Add to Cart" : "Out of Stock"
                  }}
                </button>
              </div>
              <p
                class="text-center mt-2 text-muted small"
                v-if="product.stock_quantity > 0"
              >
                {{ product.stock_quantity }} units in stock
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Technical Specifications -->
      <div v-if="specs.length > 0" class="row g-5">
        <div class="col-12">
          <div class="specs-section glass-card p-4">
            <h3
              class="h5 mb-3 fw-bold pb-2"
              style="border-bottom: 1px solid var(--border)"
            >
              Technical Specifications
            </h3>
            <div class="specs-grid">
              <div
                v-for="(spec, index) in specs"
                :key="index"
                class="spec-item"
              >
                <span class="spec-label">{{ spec.label }}</span>
                <span class="spec-value">{{ spec.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-details-page {
  padding-top: 1rem;
  padding-bottom: 4rem;
}

.back-btn {
  color: var(--muted-foreground);
  transition: color 0.2s;
  text-decoration: none;
  display: inline-block;
  margin-bottom: 1rem;
  position: relative;
  z-index: 10;
}

.back-btn:hover {
  color: var(--primary);
  text-decoration: none;
}

.product-image {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: contain;
}

.product-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--foreground);
  line-height: 1.2;
}

.price-section {
  color: var(--primary);
  font-family: var(--font-mono);
  margin-bottom: 1.5rem;
}

.price-section-mobile {
  margin-bottom: 1.5rem;
}

.currency {
  font-size: 1.5rem;
  vertical-align: top;
  margin-top: 0.2rem;
  display: inline-block;
}

.amount {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
}

.description {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--muted-foreground);
}

.specs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem 2rem;
}

.rating-badge {
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.spec-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.spec-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted-foreground);
}

.spec-value {
  font-weight: 600;
  color: var(--foreground);
  font-family: var(--font-mono);
}

@media (max-width: 768px) {
  .product-details-page {
    padding-top: 0rem;
  }

  .product-title {
    font-size: 1.75rem;
  }

  .amount {
    font-size: 2rem;
  }

  .price-section-mobile {
    margin-bottom: 0.5rem;
  }

  .description {
    font-size: 1rem;
    margin-bottom: 1.5rem;
  }

  .product-content {
    margin-top: 0;
  }

  .product-content .row {
    gap: 1.5rem;
  }

  .product-image {
    margin-bottom: -2.5rem;
    margin-top: -0.5rem;
  }

  .specs-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}
</style>
