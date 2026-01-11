<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const isVisible = ref(true);
const isScrolled = ref(false);
const isDarkMode = ref(true);
const isMenuExpanded = ref(false);
let lastScrollPosition = 0;

const handleScroll = () => {
  const currentScrollPosition = window.scrollY;

  if (currentScrollPosition < 0) {
    return;
  }

  if (currentScrollPosition < 10) {
    isVisible.value = true;
    isScrolled.value = false;
    return;
  }

  isScrolled.value = currentScrollPosition > 10;

  if (Math.abs(currentScrollPosition - lastScrollPosition) < 60) {
    return;
  }

  isVisible.value = currentScrollPosition < lastScrollPosition;
  lastScrollPosition = currentScrollPosition;
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) {
    document.body.classList.remove("light-mode");
    localStorage.setItem("theme", "dark");
  } else {
    document.body.classList.add("light-mode");
    localStorage.setItem("theme", "light");
  }
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll, { passive: true });

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    isDarkMode.value = false;
    document.body.classList.add("light-mode");
  }
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<template>
  <nav
    class="navbar navbar-expand-lg"
    :class="{
      'navbar-hidden': !isVisible,
      'navbar-scrolled': isScrolled,
      'navbar-expanded': isMenuExpanded,
    }"
  >
    <div class="container">
      <div class="d-flex align-items-center gap-3">
        <router-link class="navbar-brand" to="/">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="infinity-logo"
          >
            <path
              d="M6 16c5 0 7-8 12-8a4 4 0 0 1 0 8c-5 0-7-8-12-8a4 4 0 1 0 0 8"
            />
          </svg>
          InfiniteCompute
        </router-link>
        <div class="nav-links d-none d-lg-flex gap-4 align-items-center">
          <a class="nav-link text-foreground" href="#">Products</a>
          <router-link class="nav-link text-foreground" to="/news"
            >News</router-link
          >
          <a class="nav-link text-foreground" href="#">About</a>
        </div>
      </div>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        @click="isMenuExpanded = !isMenuExpanded"
      >
        <div
          v-if="!isMenuExpanded"
          class="menu-icon hamburger-icon"
          aria-label="Menu"
        ></div>
        <div v-else class="menu-icon x-icon" aria-label="Close"></div>
      </button>
      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav gap-2 align-items-center">
          <li class="nav-item d-lg-none mt-3">
            <a class="nav-link text-foreground" href="#">Products</a>
          </li>
          <li class="nav-item d-lg-none">
            <router-link class="nav-link text-foreground" to="/news"
              >News</router-link
            >
          </li>
          <li class="nav-item d-lg-none mb-3">
            <a class="nav-link text-foreground" href="#">About</a>
          </li>
          <li class="nav-item d-none d-lg-block">
            <div class="search-wrapper">
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
                class="search-icon"
              >
                <path d="m21 21-4.34-4.34" />
                <circle cx="11" cy="11" r="8" />
              </svg>
              <input
                type="search"
                placeholder="Search..."
                class="search-input"
              />
            </div>
          </li>
          <li class="nav-item">
            <a class="btn btn-sm btn-outline" href="#">Login</a>
          </li>
          <li class="nav-item mb-3 mb-lg-0">
            <a class="btn btn-sm btn-primary" href="#">Sign Up</a>
          </li>
          <li class="nav-item">
            <button
              class="btn btn-sm btn-icon btn-ghost theme-toggle"
              @click="toggleTheme"
              :aria-label="
                isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'
              "
            >
              <svg
                v-if="isDarkMode"
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
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2" />
                <path d="M12 20v2" />
                <path d="m4.93 4.93 1.41 1.41" />
                <path d="m17.66 17.66 1.41 1.41" />
                <path d="M2 12h2" />
                <path d="M20 12h2" />
                <path d="m6.34 17.66-1.41 1.41" />
                <path d="m19.07 4.93-1.41 1.41" />
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
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
              </svg>
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: transform 0.3s ease-in-out, background-color 0.3s ease,
    backdrop-filter 0.3s ease;
  transform: translateY(0);
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.navbar-scrolled,
.navbar-expanded {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

body.light-mode .navbar-scrolled,
body.light-mode .navbar-expanded {
  background-color: rgba(255, 255, 255, 0.5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.navbar-hidden {
  transform: translateY(-100%);
}

.nav-link {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  transition: color 0.2s;
  text-decoration: none;
  padding: 0;
}
.nav-link:hover {
  color: var(--primary) !important;
}
.infinity-logo {
  color: var(--primary);
}
.search-wrapper {
  position: relative;
  display: inline-block;
}
.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
}
.search-input {
  height: 2.25rem;
  width: 200px;
  min-width: 0;
  border-radius: var(--radius);
  border: 1px solid var(--input);
  background: var(--background);
  padding: 0.25rem 0.75rem 0.25rem 2.25rem;
  font-size: 0.875rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  transition: color 0.2s, box-shadow 0.2s;
  outline: none;
  color: var(--foreground);
}
.search-input::placeholder {
  color: var(--muted-foreground);
}
.search-input::selection {
  background-color: var(--primary);
  color: var(--primary-foreground);
}
.search-input:focus-visible {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring), transparent 50%);
}
.search-input[aria-invalid="true"] {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive), transparent 80%);
  border-color: var(--destructive);
}
.search-input:disabled {
  pointer-events: none;
  cursor: not-allowed;
  opacity: 0.5;
}

.navbar-toggler {
  border: none;
  padding: 0.25rem 0.5rem;
  background: transparent;
  border-radius: 0;
  color: var(--foreground);
}

.navbar-toggler:focus {
  box-shadow: none;
  border: none;
  outline: none;
}

.navbar-toggler-icon {
  display: none;
}

.menu-icon {
  width: 1.5em;
  height: 1.5em;
  display: block;
  background-color: var(--foreground);
  -webkit-mask-size: contain;
  mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-position: center;
}

.hamburger-icon {
  -webkit-mask-image: url("/icons/hamburger-menu.svg");
  mask-image: url("/icons/hamburger-menu.svg");
}

.x-icon {
  -webkit-mask-image: url("/icons/x.svg");
  mask-image: url("/icons/x.svg");
}

.theme-toggle {
  color: var(--foreground);
}

.theme-toggle:hover {
  color: var(--primary);
}
</style>
