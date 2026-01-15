<script setup>
import { ref, computed } from "vue";

// Tabs State
const activeTab = ref("store-1");

// Easter Egg State
const firstName = ref("");
const lastName = ref("");
const showModal = ref(false);
const couponCode = ref("");
const loading = ref(false);
const error = ref("");
const copied = ref(false);

const greetingText = computed(() => {
  const first = firstName.value.trim();
  const last = lastName.value.trim();
  if (first || last) {
    return `Welcome, ${first}${last ? ` ${last}` : ""}!`;
  }
  return "Easter egg";
});

const unlockReward = async () => {
  if (!firstName.value.trim() || !lastName.value.trim()) {
    error.value = "Please enter both first and last name.";
    return;
  }

  error.value = "";
  loading.value = true;

  try {
    const response = await fetch("/api/orders/coupon/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        first_name: firstName.value,
        last_name: lastName.value,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to generate coupon");
    }

    const data = await response.json();
    couponCode.value = data.code;
    showModal.value = true;
  } catch (err) {
    console.error(err);
    error.value = "Something went wrong. Please try again.";
  } finally {
    loading.value = false;
  }
};

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(couponCode.value);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy", err);
  }
};
</script>

<template>
  <div class="about-page container fade-in-up-fast pt-5">
    <!-- Easter Egg Section -->
    <div class="row justify-content-center mb-5">
      <div class="col-lg-8">
        <div class="easter-egg-card glass-card p-4">
          <div class="row align-items-center">
            <div class="col-md-6 mb-3 mb-md-0">
              <div
                class="d-flex align-items-center gap-2 mb-2 justify-content-center justify-content-md-start"
              >
                <div class="icon-wrapper text-foreground d-inline-block">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="40"
                    height="40"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="gift-icon"
                  >
                    <rect x="3" y="8" width="18" height="4" rx="1" />
                    <path d="M12 8v13" />
                    <path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7" />
                    <path
                      d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5"
                    />
                  </svg>
                </div>
                <h3 class="h5 mb-0">{{ greetingText }}</h3>
              </div>
              <p class="text-muted mb-0 small text-center text-md-start">
                Enter your name to unlock a special reward.
              </p>
            </div>
            <div class="col-md-6">
              <div class="d-flex flex-column gap-2">
                <div class="row g-2">
                  <div class="col-6">
                    <div class="input-group-custom">
                      <input
                        v-model="firstName"
                        type="text"
                        class="form-control-custom"
                        placeholder="First Name"
                      />
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="input-group-custom">
                      <input
                        v-model="lastName"
                        type="text"
                        class="form-control-custom"
                        placeholder="Last Name"
                      />
                    </div>
                  </div>
                </div>

                <button
                  :disabled="loading"
                  @click="unlockReward"
                  class="btn btn-primary w-100 d-flex align-items-center justify-content-center gap-2"
                  :aria-label="loading ? 'Unlocking reward' : 'Unlock reward'"
                >
                  <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  <span v-if="!loading" class="d-flex align-items-center gap-2">
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
                      aria-hidden="true"
                    >
                      <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                      <path d="M7 11V7a5 5 0 0 1 9.9-1" />
                    </svg>
                  </span>
                  <span>{{ loading ? "Unlocking..." : "Unlock" }}</span>
                </button>
                <div v-if="error" class="text-danger small mt-2">
                  {{ error }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Store Images & Story -->
    <div class="row justify-content-center mb-5">
      <div class="col-lg-10">
        <div class="tabs-container">
          <div class="row align-items-center justify-content-center gx-5">
            <div class="col-lg-5">
              <div class="tabs-wrapper">
                <div class="tabs-list mb-4">
                  <label class="tab-trigger d-flex align-items-center gap-2">
                    <input
                      type="radio"
                      name="storeLocation"
                      value="store-1"
                      v-model="activeTab"
                      class="form-check-input"
                    />
                    <span class="small">Sydney, Australia</span>
                  </label>
                  <label class="tab-trigger d-flex align-items-center gap-2">
                    <input
                      type="radio"
                      name="storeLocation"
                      value="store-2"
                      v-model="activeTab"
                      class="form-check-input"
                    />
                    <span class="small">Ho Chi Minh, Vietnam</span>
                  </label>
                </div>
              </div>

              <div class="store-image-wrapper">
                <img
                  v-if="activeTab === 'store-1'"
                  src="/images/store-1.webp"
                  alt="Sydney Store"
                  class="img-fluid shadow-sm store-img"
                  key="store-1"
                />
                <img
                  v-if="activeTab === 'store-2'"
                  src="/images/store-2.webp"
                  alt="HCMC Store"
                  class="img-fluid shadow-sm store-img"
                  key="store-2"
                />
              </div>
            </div>
            <div class="col-lg-5">
              <h2 class="h3 mb-3 text-primary">Our Story</h2>
              <p class="text-muted mb-0 leading-relaxed">
                At InfiniteCompute, we believe everyone deserves access to
                powerful computing hardware. That's why we've built a store
                focused on delivering authentic NVIDIA GPUs at fair prices with
                exceptional service. Our team understands the importance of
                getting the right GPU for your specific needs, and we're
                committed to making your buying experience smooth and
                straightforward. From gamers pushing for higher frame rates to
                professionals running complex workloads, we're here to power
                your possibilities.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reward Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="showModal = false">
        <div
          class="modal-content glass-card p-5 text-center fade-in-up-slow"
          @click.stop
        >
          <div class="success-icon mb-4">
            <!-- Gift icon with primary color -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="64"
              height="64"
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--primary)"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="gift-icon-modal mb-2"
            >
              <rect x="3" y="8" width="18" height="4" rx="1" />
              <path d="M12 8v13" />
              <path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7" />
              <path
                d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5"
              />
            </svg>
          </div>
          <h2 class="h3 mb-3">Congratulations!</h2>
          <p class="text-muted mb-4">
            Here is your
            <span class="text-primary fw-bold">10% OFF</span> coupon code.
          </p>

          <div
            class="coupon-display d-flex align-items-center justify-content-between p-3 mb-4"
          >
            <code class="fs-5 fw-bold text-foreground">{{ couponCode }}</code>
            <button
              @click="copyToClipboard"
              class="btn btn-ghost btn-sm p-2 position-relative"
              title="Copy to clipboard"
            >
              <div v-if="copied" class="tooltip-copied">Copied!</div>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--foreground)"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                <path
                  d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"
                />
              </svg>
            </button>
          </div>

          <button @click="showModal = false" class="btn btn-primary w-100">
            Awesome!
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.page-title {
  font-family: var(--font-mono);
  font-weight: 700;
  margin-bottom: 2rem;
}

.tabs-wrapper {
  display: flex;
  justify-content: center;
  width: 100%;
}

.tabs-list {
  display: inline-flex;
  background: var(--muted);
  padding: var(--spacing-xs);
  border-radius: 0;
  width: fit-content;
}

.tab-trigger {
  background: transparent;
  border: none;
  color: var(--muted-foreground);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: 0;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base) ease;
}

.tab-trigger:has(input:checked) {
  background: var(--background);
  color: var(--foreground);
  box-shadow: var(--shadow-sm);
}

.form-check-input {
  cursor: pointer;
  margin: 0;
  background-color: var(--muted);
  border-color: var(--border);
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
}

.form-check-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.25rem rgba(var(--primary), 0.25);
}

.store-img {
  width: 100%;
  height: auto;
  object-fit: cover;
  aspect-ratio: 1/1;
  border-radius: 0;
}

.store-image-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

@media (max-width: 991px) {
  .store-img {
    width: 100%;
  }

  .tabs-wrapper {
    justify-content: center;
    width: 100%;
  }

  .store-image-wrapper {
    justify-content: center !important;
  }

  .tabs-container .col-md-5 {
    max-width: 100%;
    flex: 0 0 100%;
  }

  .tabs-container .col-md-5:first-child {
    margin-bottom: var(--spacing-xl);
  }

  .tabs-container .col-lg-5:last-child h2 {
    margin-top: var(--spacing-xl);
  }
}

.store-image-wrapper img {
  animation: fadeInImage var(--transition-slow) ease-in-out;
}

@keyframes fadeInImage {
  from {
    opacity: 0;
    transform: translateY(var(--spacing-xs));
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.leading-relaxed {
  line-height: 1.7;
}

/* Easter Egg Styles */
.easter-egg-card {
  border: 1px solid var(--border) !important;
  transition: transform var(--transition-slow) ease;
  position: relative;
  overflow: hidden;
  background: transparent;
}

.easter-egg-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at center,
    color-mix(in srgb, var(--primary), transparent 85%),
    transparent 70%
  );
  z-index: -1;
}

@media (min-width: 768px) {
  .easter-egg-card::before {
    background: radial-gradient(
      circle at 0% 50%,
      color-mix(in srgb, var(--primary), transparent 80%),
      transparent 40%
    );
  }
}

.easter-egg-card:hover {
  transform: translateY(-2px);
}

.gift-icon {
  filter: drop-shadow(0 0 8px rgba(var(--primary), 0.3));
}

.coupon-display {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-modal);
}

.modal-content {
  max-width: 400px;
  width: 90%;
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
}

/* Custom Input Styles */
.input-group-custom {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: var(--spacing-md);
  color: var(--muted-foreground);
  pointer-events: none;
  z-index: 10;
  display: flex;
  align-items: center;
  height: 100%;
}

.form-control-custom {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--text-sm);
  background-color: color-mix(in srgb, var(--background), transparent 50%);
  border: 1px solid var(--input);
  border-radius: var(--radius);
  color: var(--foreground);
  transition: all var(--transition-base);
  outline: none;
}

.form-control-custom::placeholder {
  font-size: var(--text-sm);
}

.form-control-custom:focus {
  border-color: var(--ring);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--ring), transparent 70%);
}

/* Tooltip Styles */
.tooltip-copied {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: transparent;
  color: var(--primary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-xs);
  font-size: 0.75rem;
  font-weight: bold;
  pointer-events: none;
  animation: fadeIn var(--transition-slow) ease-out;
  margin-bottom: var(--spacing-sm);
  white-space: nowrap;
}

.tooltip-copied::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -4px;
  border-width: 4px;
  border-style: solid;
  border-color: var(--primary) transparent transparent transparent;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, var(--spacing-xs));
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

.coupon-display button {
  position: relative;
}
</style>
