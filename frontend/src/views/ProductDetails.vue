<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCart } from "../composables/useCart";
import { useAuth } from "../composables/useAuth";
import { formatPrice } from "../utils/format";
import Modal from "../components/ui/Modal.vue";

const route = useRoute();
const router = useRouter();
const { addToCart } = useCart();
const { user, isAuthenticated, token } = useAuth();
const product = ref(null);
const loading = ref(true);
const error = ref(null);
const reviews = ref([]);
const reviewsLoading = ref(true);

// Review Logic
const showReviewModal = ref(false);
const reviewEligibility = ref({ can_review: false, reason: null });
const checkingEligibility = ref(false);
const reviewForm = ref({
  rating: 5,
  comment: "",
});
const hoverRating = ref(0);
const reviewSubmitting = ref(false);
const reviewError = ref("");
const isDeleteModalOpen = ref(false);
const reviewToDelete = ref(null);

const checkEligibility = async () => {
  if (!isAuthenticated.value) return;

  checkingEligibility.value = true;
  try {
    const response = await fetch(
      `http://localhost:8000/reviews/check-eligibility/${route.params.id}`,
      {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      }
    );
    if (response.ok) {
      reviewEligibility.value = await response.json();
    }
  } catch (e) {
    console.error("Failed to check eligibility", e);
  } finally {
    checkingEligibility.value = false;
  }
};

const openReviewModal = () => {
  showReviewModal.value = true;
  if (isAuthenticated.value) {
    checkEligibility();
  }
};

const closeReviewModal = () => {
  showReviewModal.value = false;
  reviewError.value = "";
  reviewForm.value = { rating: 5, comment: "" };
  hoverRating.value = 0;
};

const submitReview = async () => {
  reviewSubmitting.value = true;
  reviewError.value = "";

  try {
    const response = await fetch("http://localhost:8000/reviews", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify({
        product_id: parseInt(route.params.id),
        rating: reviewForm.value.rating,
        comment: reviewForm.value.comment,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to submit review");
    }

    // Success
    closeReviewModal();
    fetchReviews(); // Refresh reviews
  } catch (e) {
    reviewError.value = e.message;
  } finally {
    reviewSubmitting.value = false;
  }
};

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

const fetchReviews = async () => {
  reviewsLoading.value = true;
  try {
    const response = await fetch(
      `http://localhost:8000/reviews/product/${route.params.id}`
    );
    if (response.ok) {
      reviews.value = await response.json();
    }
  } catch (error) {
    console.error("Failed to fetch reviews:", error);
  } finally {
    reviewsLoading.value = false;
  }
};

const openDeleteModal = (review) => {
  reviewToDelete.value = review;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  reviewToDelete.value = null;
};

const deleteReview = async () => {
  if (!reviewToDelete.value) return;

  try {
    const response = await fetch(
      `http://localhost:8000/reviews/${reviewToDelete.value.id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      }
    );

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to delete review");
    }

    closeDeleteModal();
    fetchReviews();
  } catch (e) {
    console.error("Failed to delete review:", e);
    alert(e.message || "Failed to delete review");
  }
};

onMounted(() => {
  fetchProduct();
  fetchReviews();
});

const goBack = () => {
  router.push("/products");
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
      class="btn btn-link text-decoration-none mb-4 back-btn fade-in-up-none"
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
    <div
      v-else-if="product"
      class="product-content fade-in-up-none delay-100-none"
    >
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
              <span class="amount">{{
                product.price ? formatPrice(product.price) : "0.00"
              }}</span>
            </div>

            <p class="description mb-4">{{ product.description }}</p>

            <div class="actions mb-5">
              <div class="d-grid gap-2">
                <button
                  class="btn btn-primary btn-lg d-flex align-items-center justify-content-center gap-2"
                  :disabled="product.stock_quantity <= 0"
                  @click="addToCart(product)"
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
              class="h5 mb-3 fw-bold pb-2 d-flex align-items-center gap-2"
              style="border-bottom: 1px solid var(--border)"
            >
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
                class="text-primary"
              >
                <path
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              Technical Specs
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

      <!-- Reviews Section -->
      <div class="row g-5 mt-1">
        <div class="col-12">
          <div class="reviews-section glass-card p-4">
            <div
              class="d-flex justify-content-between align-items-center mb-4 pb-2"
              style="border-bottom: 1px solid var(--border)"
            >
              <h3 class="h5 m-0 fw-bold d-flex align-items-center gap-2">
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
                  class="text-primary"
                >
                  <path
                    d="M16.051 12.616a1 1 0 0 1 1.909.024l.737 1.452a1 1 0 0 0 .737.535l1.634.256a1 1 0 0 1 .588 1.806l-1.172 1.168a1 1 0 0 0-.282.866l.259 1.613a1 1 0 0 1-1.541 1.134l-1.465-.75a1 1 0 0 0-.912 0l-1.465.75a1 1 0 0 1-1.539-1.133l.258-1.613a1 1 0 0 0-.282-.866l-1.156-1.153a1 1 0 0 1 .572-1.822l1.633-.256a1 1 0 0 0 .737-.535z"
                  />
                  <path d="M8 15H7a4 4 0 0 0-4 4v2" />
                  <circle cx="10" cy="7" r="4" />
                </svg>
                Customer Reviews
              </h3>
              <button
                class="btn btn-primary btn-sm d-flex align-items-center gap-2"
                @click="openReviewModal"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                </svg>
                <span class="d-none d-sm-inline">Write a Review</span>
              </button>
            </div>
            <div v-if="reviewsLoading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading reviews...</span>
              </div>
            </div>
            <div
              v-else-if="reviews.length === 0"
              class="text-center py-4 text-muted"
            >
              No reviews yet for this product.
            </div>
            <div v-else class="reviews-list">
              <div
                v-for="(review, index) in reviews"
                :key="review.id"
                :class="
                  index !== reviews.length - 1
                    ? 'review-item mb-3 pb-3'
                    : 'review-item'
                "
                :style="
                  index !== reviews.length - 1
                    ? 'border-bottom: 1px solid var(--border)'
                    : ''
                "
              >
                <div
                  class="d-flex justify-content-between align-items-center mb-2"
                >
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-bold">{{
                      review.user_name || "Anonymous"
                    }}</span>
                    <div class="rating">
                      <span v-for="i in 5" :key="i" class="star">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          viewBox="0 0 24 24"
                          :fill="i <= review.rating ? 'currentColor' : 'var(--muted)'"
                          stroke="none"
                          :class="
                            i <= review.rating ? 'text-warning' : 'text-muted'
                          "
                        >
                          <polygon
                            points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                          />
                        </svg>
                      </span>
                    </div>
                    <button
                      v-if="isAuthenticated && user && review.user_id === user.id"
                      type="button"
                      class="btn btn-icon btn-ghost btn-sm p-1 delete-review-btn ms-2"
                      @click="openDeleteModal(review)"
                      title="Delete review"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        class="delete-review-icon"
                      >
                        <path d="M3 6h18" />
                        <path
                          d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"
                        />
                        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                      </svg>
                    </button>
                  </div>
                  <span class="text-muted small">{{
                    new Date(review.created_at).toLocaleDateString()
                  }}</span>
                </div>
                <p class="mb-0">{{ review.comment }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Review Modal -->
  <div
    v-if="showReviewModal"
    class="modal-overlay"
    @click.self="closeReviewModal"
  >
    <div
      class="modal-content glass-card p-4 fade-in-up-fast"
      style="max-width: 500px; width: 100%"
    >
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="h4 mb-0">Write a Review</h3>
        <button class="btn btn-icon btn-ghost" @click="closeReviewModal">
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
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div v-if="!isAuthenticated" class="text-center py-4">
        <p class="mb-3">You need to be logged in to write a review.</p>
        <router-link to="/sign-in" class="btn btn-primary">Log In</router-link>
      </div>

      <div v-else-if="checkingEligibility" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Checking eligibility...</span>
        </div>
      </div>

      <div v-else-if="!reviewEligibility.can_review" class="text-center py-4">
        <div class="mb-3 text-destructive">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"
            />
            <path d="M12 9v4" />
            <path d="M12 17h.01" />
          </svg>
        </div>
        <p v-if="reviewEligibility.reason === 'already_reviewed'">
          You have already reviewed this product.
        </p>
        <p v-else-if="reviewEligibility.reason === 'no_purchase'">
          You can only review products that you have purchased and received.
        </p>
        <p v-else>You are not eligible to review this product.</p>
      </div>

      <form v-else @submit.prevent="submitReview">
        <div class="mb-3">
          <label class="form-label rating-label">Rating</label>
          <div class="stars-container">
            <button
              type="button"
              v-for="star in 5"
              :key="star"
              class="btn btn-icon btn-ghost p-0 star-button"
              @click="reviewForm.rating = star"
              @mouseenter="hoverRating = star"
              @mouseleave="hoverRating = 0"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                :fill="
                  star <= (hoverRating || reviewForm.rating)
                    ? 'currentColor'
                    : 'none'
                "
                :class="
                  star <= (hoverRating || reviewForm.rating)
                    ? 'text-warning'
                    : 'text-muted'
                "
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polygon
                  points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                ></polygon>
              </svg>
            </button>
          </div>
        </div>

        <div class="mb-3">
          <label for="review-comment" class="form-label">Comment</label>
          <textarea
            id="review-comment"
            v-model="reviewForm.comment"
            class="form-control-custom w-100"
            rows="4"
            placeholder="Share your thoughts..."
            required
          ></textarea>
        </div>

        <div v-if="reviewError" class="alert alert-danger">
          {{ reviewError }}
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100"
          :disabled="reviewSubmitting"
        >
          <span
            v-if="reviewSubmitting"
            class="spinner-border spinner-border-sm me-1"
            role="status"
            aria-hidden="true"
          ></span>
          <span v-if="reviewSubmitting">Submitting...</span>
          <span v-else>Submit Review</span>
        </button>
      </form>
    </div>
  </div>

  <!-- Delete Review Modal -->
  <Modal
    :isOpen="isDeleteModalOpen"
    title="Delete Review"
    @close="closeDeleteModal"
  >
    <div class="modal-content-padding">
      <p>
        Are you sure you want to delete this review? This action cannot be
        undone.
      </p>
      <div class="modal-actions">
        <button @click="closeDeleteModal" class="btn btn-outline">
          Cancel
        </button>
        <button @click="deleteReview" class="btn btn-destructive">
          Delete
        </button>
      </div>
    </div>
  </Modal>
</template>

<style scoped>
.product-details-page {
  padding-top: var(--spacing-md);
  padding-bottom: var(--spacing-2xl);
}

.back-btn {
  color: var(--muted-foreground);
  transition: color var(--transition-base);
  text-decoration: none;
  display: inline-block;
  margin-bottom: var(--spacing-md);
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
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--foreground);
  line-height: 1.2;
}

.price-section {
  color: var(--primary);
  font-family: var(--font-mono);
  margin-bottom: var(--spacing-lg);
}

.price-section-mobile {
  margin-bottom: var(--spacing-lg);
}

.currency {
  font-size: var(--text-2xl);
  vertical-align: top;
  margin-top: 0.2rem;
  display: inline-block;
}

.amount {
  font-size: var(--text-5xl);
  font-weight: 700;
  line-height: 1;
}

.description {
  font-size: var(--text-lg);
  line-height: 1.6;
  color: var(--muted-foreground);
}

@media (min-width: 1024px) {
  .description {
    font-size: var(--text-base);
  }
}

.specs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md) var(--spacing-xl);
}

.rating-badge {
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.spec-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.spec-label {
  font-size: var(--text-sm);
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
    padding-top: 0;
  }

  .product-title {
    font-size: var(--text-3xl);
  }

  .amount {
    font-size: var(--text-3xl);
  }

  .price-section-mobile {
    margin-bottom: var(--spacing-sm);
  }

  .description {
    font-size: var(--text-base);
    margin-bottom: var(--spacing-lg);
  }

  .product-content {
    margin-top: 0;
  }

  .product-content .row {
    gap: var(--spacing-lg);
  }

  .product-image {
    margin-bottom: -2.5rem;
    margin-top: -0.5rem;
  }

  .specs-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
}
</style>

<style scoped>
/* Add styling to match sign up inputs */
.form-control-custom {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--text-sm);
  background-color: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--input);
  border-radius: var(--radius);
  color: var(--foreground);
  transition: all var(--transition-base);
  outline: none;
}

.form-control-custom:focus {
  border-color: var(--ring);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--ring), transparent 70%);
}

.rating-label {
  margin-bottom: 0.1rem;
}

.stars-container {
  display: flex;
  gap: 0.05rem;
  align-items: center;
}

.star-button {
  margin: 0;
  line-height: 1;
}

.delete-review-icon {
  color: var(--muted-foreground);
  transition: color var(--transition-base);
}

.delete-review-btn:hover .delete-review-icon {
  color: var(--destructive);
}

.delete-review-btn:hover {
  background-color: color-mix(in srgb, var(--destructive), transparent 90%);
}

.modal-content-padding {
  padding: 0 var(--spacing-lg) var(--spacing-lg) var(--spacing-lg);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}
</style>
