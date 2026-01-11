<script setup>
import GlowingEffect from "./GlowingEffect.vue";
import CardSpotlight from "./CardSpotlight.vue";

const features = [
  {
    icon: "chip",
    title: "Authentic NVIDIA Products",
    description:
      "100% genuine GPUs sourced directly from authorized distributors, backed by full manufacturer warranties.",
  },
  {
    icon: "truck",
    title: "Fast & Reliable Shipping",
    description:
      "Quick delivery with expedited shipping options, careful packing, and real-time tracking.",
  },
  {
    icon: "headset",
    title: "Expert Customer Support",
    description:
      "Knowledgeable team ready to help you find the perfect GPU for gaming or professional workstations.",
  },
  {
    icon: "price-badge",
    title: "Competitive Pricing",
    description:
      "Daily market monitoring ensures the best prices on NVIDIA GPUs with no hidden fees.",
  },
  {
    icon: "package",
    title: "Hassle-Free Returns",
    description:
      "Straightforward return policy with no complicated hoops. Your satisfaction is our priority.",
  },
  {
    icon: "medal",
    title: "Trusted by Thousands",
    description:
      "Join our growing community of gamers, creators, and professionals who trust us for their GPU needs.",
  },
];

const icons = {
  chip: '<path d="M12 20v2"/><path d="M12 2v2"/><path d="M17 20v2"/><path d="M17 2v2"/><path d="M2 12h2"/><path d="M2 17h2"/><path d="M2 7h2"/><path d="M20 12h2"/><path d="M20 17h2"/><path d="M20 7h2"/><path d="M7 20v2"/><path d="M7 2v2"/><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="8" y="8" width="8" height="8" rx="1"/>',
  truck:
    '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
  headset:
    '<path d="M3 11h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5Zm0 0a9 9 0 1 1 18 0m0 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3Z"/><path d="M21 16v2a4 4 0 0 1-4 4h-5"/>',
  "price-badge":
    '<path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path d="m15 9-6 6"/><path d="M9 9h.01"/><path d="M15 15h.01"/>',
  package:
    '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><polyline points="3.29 7 12 12 20.71 7"/><path d="m7.5 4.27 9 5.15"/>',
  medal:
    '<path d="M7.21 15 2.66 7.14a2 2 0 0 1 .13-2.2L4.4 2.8A2 2 0 0 1 6 2h12a2 2 0 0 1 1.6.8l1.6 2.14a2 2 0 0 1 .14 2.2L16.79 15"/><path d="M11 12 5.12 2.2"/><path d="m13 12 5.88-9.8"/><path d="M8 7h8"/><circle cx="12" cy="17" r="5"/><path d="M12 18v-2h-.5"/>',
};
</script>

<template>
  <section class="why-choose-us-section">
    <div class="gradient-light top-left"></div>
    <div class="gradient-light bottom-right"></div>
    <div class="container section-container">
      <h2 class="section-title">Why Choose Us?</h2>

      <div class="features-grid">
        <CardSpotlight
          v-for="feature in features"
          :key="feature.title"
          class="feature-card"
          color="color-mix(in srgb, var(--primary), transparent 85%)"
        >
          <GlowingEffect
            :spread="40"
            :glow="true"
            :disabled="false"
            :proximity="64"
            :inactiveZone="0.01"
            :borderWidth="1"
            variant="primary"
          />

          <div class="feature-content">
            <div class="icon-wrapper">
              <svg
                class="feature-icon"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1"
                stroke-linecap="round"
                stroke-linejoin="round"
                v-html="icons[feature.icon]"
              ></svg>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </CardSpotlight>
      </div>
    </div>
  </section>
</template>

<style scoped>
.why-choose-us-section {
  padding-top: 5rem;
  padding-bottom: 5rem;
  position: relative;
  overflow: hidden;
}

.gradient-light {
  position: absolute;
  width: 40rem;
  height: 40rem;
  border-radius: 50%;
  background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
  filter: blur(100px);
  opacity: 0.35;
  pointer-events: none;
  z-index: 0;
}

body.light-mode .gradient-light {
  opacity: 0.1;
}

.gradient-light.top-left {
  top: 0;
  left: 0;
  transform: translate(-40%, -40%);
}

.gradient-light.bottom-right {
  bottom: 0;
  right: 0;
  transform: translate(40%, 40%);
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  font-family: var(--font-mono);
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 992px) {
  .features-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.feature-card {
  position: relative;
  border-radius: 0;
  padding: 1.5rem;
  background-color: color-mix(in srgb, var(--card), transparent 80%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--border);
}

.feature-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.icon-wrapper {
  width: 3rem;
  height: 3rem;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.25rem;
  color: var(--primary);
}

.feature-icon {
  width: 2.5rem;
  height: 2.5rem;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 700;
  font-family: var(--font-mono);
  margin: 0;
}

.feature-description {
  font-size: 0.95rem;
  color: var(--muted-foreground);
  margin: 0;
  line-height: 1.6;
}
</style>
