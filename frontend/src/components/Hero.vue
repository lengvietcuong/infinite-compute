<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const gpuCount = ref(0);
const customerCount = ref(0);
const countryCount = ref(0);

const currentImageIndex = ref(0);
const gpuImages = [
  "/images/gpu-1.webp",
  "/images/gpu-2.webp",
  "/images/gpu-3.webp",
  "/images/gpu-4.webp",
];

let imageInterval = null;

const animateCounter = (target, duration, setter) => {
  const start = 0;
  const startTime = Date.now();

  const timer = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Ease-out effect: y = 1 - (1 - x)^3
    const easedProgress = 1 - Math.pow(1 - progress, 3);
    const current = start + (target - start) * easedProgress;

    if (progress >= 1) {
      setter(target);
      clearInterval(timer);
    } else {
      setter(Math.floor(current));
    }
  }, 16);
};

onMounted(() => {
  setTimeout(() => {
    animateCounter(40, 1000, (val) => (gpuCount.value = val));
  }, 600);

  setTimeout(() => {
    animateCounter(5000, 1000, (val) => (customerCount.value = val));
  }, 700);

  setTimeout(() => {
    animateCounter(100, 1000, (val) => (countryCount.value = val));
  }, 800);

  imageInterval = setInterval(() => {
    currentImageIndex.value = (currentImageIndex.value + 1) % gpuImages.length;
  }, 2000);
});

onUnmounted(() => {
  if (imageInterval) {
    clearInterval(imageInterval);
  }
});
</script>

<template>
  <section
    class="hero-section d-flex align-items-center position-relative overflow-hidden"
  >
    <!-- Background Elements -->
    <div class="bg-grid position-absolute top-0 start-0 w-100 h-100 z-0"></div>
    <div class="glow-effect position-absolute z-0"></div>
    <div class="moving-blob position-absolute z-0"></div>
    <div class="moving-blob-2 position-absolute z-0"></div>

    <div class="container position-relative z-1">
      <div class="row align-items-center min-vh-75 py-5">
        <!-- Text Content -->
        <div class="col-lg-7 text-center text-lg-start mb-5 mb-lg-0">
          <div
            class="badge badge-outline badge-lg badge-secondary-bg mb-4 fade-in-up"
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
              style="margin-right: 0.25rem"
            >
              <path
                d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"
              />
              <path d="M15 18H9" />
              <path
                d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"
              />
              <circle cx="17" cy="18" r="2" />
              <circle cx="7" cy="18" r="2" />
            </svg>
            <span class="font-mono">Free Worldwide Shipping</span>
          </div>

          <h1 class="hero-heading mb-4 fade-in-up delay-100">
            Limitless GPUs, <br />
            <span class="text-primary">Endless Possibilities</span>
          </h1>

          <p
            class="lead text-muted mb-5 fade-in-up delay-200"
            style="max-width: 600px"
          >
            Shop authentic NVIDIA GPUs with competitive pricing, expert support,
            and fast shipping on every order
          </p>

          <div
            class="d-flex flex-column flex-sm-row gap-3 justify-content-center justify-content-lg-start fade-in-up delay-300"
          >
            <a href="#" class="btn btn-lg btn-primary"> Browse Products </a>
            <a href="#" class="btn btn-lg btn-outline"> Contact Sales </a>
          </div>
        </div>

        <!-- Visual Content -->
        <div class="col-lg-5 position-relative">
          <div class="hero-visual animate-float">
            <div class="glass-card p-4 position-relative card-with-glow">
              <!-- Decorative tech lines -->
              <div class="tech-line top-left"></div>
              <div class="tech-line bottom-right"></div>

              <!-- Abstract GPU Representation -->
              <div
                class="gpu-model-container d-flex justify-content-center align-items-center"
              >
                <img
                  :src="gpuImages[currentImageIndex]"
                  alt="GPU"
                  class="gpu-image"
                  style="max-width: 100%; max-height: 100%; object-fit: contain"
                />
              </div>

              <!-- Statistics inside card -->
              <div
                class="mt-5 d-flex gap-5 justify-content-center fade-in-up delay-300 opacity-75"
              >
                <div class="text-center">
                  <h2 class="mb-1 font-mono" style="font-size: 2.2rem">
                    {{ gpuCount }}+
                  </h2>
                  <small
                    class="text-muted text-uppercase"
                    style="font-size: 0.8rem"
                    >NVIDIA GPUs</small
                  >
                </div>
                <div class="text-center">
                  <h2 class="mb-1 font-mono" style="font-size: 2.2rem">
                    {{ customerCount.toLocaleString() }}+
                  </h2>
                  <small
                    class="text-muted text-uppercase"
                    style="font-size: 0.8rem"
                    >Happy Customers</small
                  >
                </div>
                <div class="text-center">
                  <h2 class="mb-1 font-mono" style="font-size: 2.2rem">
                    {{ countryCount }}+
                  </h2>
                  <small
                    class="text-muted text-uppercase"
                    style="font-size: 0.8rem"
                    >Countries</small
                  >
                </div>
              </div>
            </div>

            <!-- Background Glow behind card -->
            <div class="card-glow"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  min-height: 100vh;
  margin-top: -60px;
  padding-top: 60px;
}

.text-gradient {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.font-mono {
  font-family: var(--font-mono);
}

.glow-effect {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
  opacity: 0.15;
  filter: blur(100px);
  top: -20%;
  left: -10%;
  border-radius: 50%;
}

body.light-mode .glow-effect {
  opacity: 0.08;
}

.moving-blob {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, var(--primary) 0%, transparent 60%);
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.25;
  top: -5%;
  left: 5%;
  animation: float-blob 20s infinite ease-in-out;
  pointer-events: none;
}

body.light-mode .moving-blob {
  opacity: 0.08;
}

@keyframes float-blob {
  0% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(200px, 150px) scale(1.2);
  }
  50% {
    transform: translate(400px, 50px) scale(0.9);
  }
  75% {
    transform: translate(100px, 200px) scale(1.1);
  }
  100% {
    transform: translate(0, 0) scale(1);
  }
}

.moving-blob-2 {
  width: 550px;
  height: 550px;
  background: radial-gradient(circle, var(--primary) 0%, transparent 60%);
  position: absolute;
  border-radius: 50%;
  filter: blur(110px);
  opacity: 0.25;
  bottom: 5%;
  right: 5%;
  animation: float-blob-2 18s infinite ease-in-out;
  pointer-events: none;
}

body.light-mode .moving-blob-2 {
  opacity: 0.08;
}

@keyframes float-blob-2 {
  0% {
    transform: translate(0, 0) scale(1);
  }
  30% {
    transform: translate(-180px, -120px) scale(1.1);
  }
  60% {
    transform: translate(-300px, 80px) scale(0.95);
  }
  85% {
    transform: translate(-80px, -150px) scale(1.15);
  }
  100% {
    transform: translate(0, 0) scale(1);
  }
}

.card-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120%;
  height: 120%;
  background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
  opacity: 0.2;
  filter: blur(60px);
  z-index: -1;
}

.card-with-glow {
  box-shadow: 0 0 40px rgba(var(--primary-rgb), 0.3);
}

.gpu-model-container {
  aspect-ratio: 3 / 2;
  width: 100%;
  background: radial-gradient(
    circle at center,
    rgba(255, 255, 255, 0.03) 0%,
    transparent 70%
  );
  border-radius: var(--radius);
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 1.5rem;
}

.gpu-image {
  transition: opacity 0.5s ease-in-out;
}

.tech-line {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid var(--primary);
  opacity: 0.5;
}

.tech-line.top-left {
  top: -1px;
  left: -1px;
  border-bottom: 0;
  border-right: 0;
}

.tech-line.bottom-right {
  bottom: -1px;
  right: -1px;
  border-top: 0;
  border-left: 0;
}

@media (max-width: 1279px) {
  .glass-card h2 {
    font-size: 1.5rem !important;
  }
}
</style>
