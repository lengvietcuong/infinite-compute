<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { formatDate } from "../utils/format";

const route = useRoute();
const router = useRouter();
const newsItem = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchNewsItem = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch(
      `http://localhost:8000/news/${route.params.id}`
    );

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("News article not found");
      }
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    newsItem.value = data;
  } catch (err) {
    console.error("Failed to fetch news item:", err);
    error.value = err.message || "Failed to load news article.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchNewsItem);

const goBack = () => {
  router.push("/news");
};

const formattedDate = computed(() => {
  if (!newsItem.value?.published_date) return "";
  return formatDate(newsItem.value.published_date);
});
</script>

<template>
  <div class="news-details-page container">
    <!-- Back Button -->
    <button
      @click="goBack"
      class="btn btn-link text-decoration-none mb-4 back-btn fade-in-up-none"
      aria-label="Back to news"
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
        aria-hidden="true"
      >
        <path d="m15 18-6-6 6-6" />
      </svg>
      Back to News
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
        <button @click="goBack" class="btn btn-outline-primary">
          Return to News
        </button>
      </div>
    </div>

    <!-- News Content -->
    <article
      v-else-if="newsItem"
      class="news-content fade-in-up-none delay-100-none"
    >
      <!-- Header -->
      <header class="mb-5 text-center">
        <h1 class="news-title mb-3">{{ newsItem.title }}</h1>
        <div
          class="text-muted d-flex align-items-center justify-content-center gap-3"
        >
          <span
            v-if="newsItem.published_date"
            class="d-flex align-items-center"
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
              class="me-2"
              aria-hidden="true"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            {{ formattedDate }}
          </span>
          <span
            v-if="newsItem.category"
            class="d-flex align-items-center border-start ps-3"
          >
            {{ newsItem.category }}
          </span>
        </div>
      </header>

      <!-- Featured Image -->
      <div
        class="news-image-container glass-card mb-3"
        v-if="newsItem.image_url"
      >
        <img
          :src="newsItem.image_url"
          :alt="newsItem.title"
          class="img-fluid news-image"
          @error="$event.target.style.display = 'none'"
        />
      </div>

      <!-- Content Body -->
      <div
        class="content-text mb-4"
        v-html="newsItem.content.replace(/\n/g, '<br/')"
      ></div>

      <!-- Source Link -->
      <div v-if="newsItem.source" class="source-link mt-5">
        <a :href="newsItem.source" target="_blank" rel="noopener noreferrer">
          Source
        </a>
      </div>
    </article>
  </div>
</template>

<style scoped>
.news-details-page {
  padding-top: var(--spacing-xl);
  padding-bottom: 4rem;
  max-width: 900px;
  margin: 0 auto;
}

.back-btn {
  color: var(--muted-foreground);
  transition: color var(--transition-base);
}

.back-btn:hover {
  color: var(--primary);
}

.news-title {
  font-size: var(--text-4xl);
  font-weight: 800;
  color: var(--foreground);
  line-height: 1.2;
}

.news-image-container {
  overflow: hidden;
  border-radius: var(--radius);
  background-color: var(--card);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 500px;
}

.news-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.content-text {
  white-space: pre-wrap;
  font-size: var(--text-lg);
  line-height: 1.8;
  color: var(--foreground);
}

@media (min-width: 1024px) {
  .content-text {
    font-size: var(--text-base);
  }
}

.source-link {
  border-top: 1px solid var(--border);
  padding-top: var(--spacing-xl);
  font-size: var(--text-base);
}

.source-link a {
  color: var(--primary);
}

.source-link a:hover {
  opacity: var(--opacity-hover);
}

@media (max-width: 768px) {
  .news-details-page {
    padding-top: 0;
  }

  .news-title {
    font-size: var(--text-3xl);
  }
}
</style>
