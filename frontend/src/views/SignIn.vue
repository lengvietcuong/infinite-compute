<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const email = ref("");
const password = ref("");
const showPassword = ref(false);
const isLoading = ref(false);
const error = ref("");

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const handleLogin = async () => {
  error.value = "";

  if (!email.value || !password.value) {
    error.value = "Please fill in all fields";
    return;
  }

  isLoading.value = true;

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to login");
    }

    localStorage.setItem("token", data.access_token);
    router.push("/");
  } catch (e) {
    error.value = e.message;
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="auth-page container-fluid p-0">
    <div class="gradient-light top-right"></div>
    <div class="row g-0 h-100">
      <!-- Left Column: Auth Form -->
      <div
        class="col-12 col-lg-6 d-flex justify-content-center align-items-center"
      >
        <div class="glass-card auth-card p-4 p-md-5">
          <div class="text-center mb-4">
            <h2 class="mb-2">Welcome Back</h2>
          </div>

          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <div class="input-group-custom">
                <span class="input-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7" />
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                  </svg>
                </span>
                <input
                  type="email"
                  id="email"
                  v-model="email"
                  class="form-control-custom"
                  placeholder="name@example.com"
                  required
                />
              </div>
            </div>

            <div class="mb-4">
              <label for="password" class="form-label">Password</label>
              <div class="input-group-custom">
                <span class="input-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  v-model="password"
                  class="form-control-custom"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="togglePassword"
                >
                  <svg
                    v-if="!showPassword"
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path
                      d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"
                    />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path
                      d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"
                    />
                    <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242" />
                    <path
                      d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"
                    />
                    <path d="m2 2 20 20" />
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="error" class="alert alert-danger mb-4" role="alert">
              {{ error }}
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100 py-2 mb-4 auth-submit-btn"
              :disabled="isLoading"
            >
              <svg
                v-if="isLoading"
                xmlns="http://www.w3.org/2000/svg"
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="spinner-icon"
              >
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              <span v-if="!isLoading">Sign In</span>
              <span v-else>Signing in...</span>
            </button>

            <p class="text-center text-muted mb-0">
              Don't have an account?
              <router-link to="/sign-up" class="text-primary text-decoration-none"
                >Sign up</router-link
              >
            </p>
          </form>
        </div>
      </div>

      <!-- Right Column: Image (Desktop only) -->
      <div class="d-none d-lg-block col-lg-6 p-0">
        <div class="auth-image"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  height: 90vh;
  position: relative;
  overflow: hidden;
}

.gradient-light {
  position: absolute;
  width: 40rem;
  height: 40rem;
  border-radius: var(--radius-full);
  background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
  filter: blur(100px);
  opacity: 0.35;
  pointer-events: none;
  z-index: 0;
}

body.light-mode .gradient-light {
  opacity: 0.1;
}

.gradient-light.top-right {
  top: 0;
  left: 0;
  transform: translate(-40%, -40%);
}

.auth-image {
  height: 100%;
  width: 100%;
  background-image: url("/images/gpu-cover-1.webp");
  background-size: cover;
  background-position: center;
}

.auth-card {
  width: 100%;
  max-width: 450px;
  border: none;
  background: transparent;
  box-shadow: none;
}

.form-label {
  font-weight: 500;
  font-size: 0.875rem;
  margin-bottom: var(--spacing-xs);
}

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

.input-icon svg {
  width: 18px;
  height: 18px;
}

.form-control-custom {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md) var(--spacing-sm) 2.75rem;
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

.password-toggle {
  position: absolute;
  right: var(--spacing-md);
  background: none;
  border: none;
  color: var(--muted-foreground);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.password-toggle:hover {
  color: var(--foreground);
}

.alert-danger {
  color: var(--error);
  background-color: color-mix(in srgb, var(--error), transparent 90%);
  border: 1px solid color-mix(in srgb, var(--error), transparent 80%);
  padding: var(--spacing-sm);
  border-radius: var(--radius);
  font-size: 0.875rem;
}

.auth-submit-btn:disabled {
  opacity: 1 !important;
  pointer-events: none;
  background-color: var(--primary) !important;
  border-color: transparent !important;
  color: var(--primary-foreground) !important;
}

.spinner-icon {
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
