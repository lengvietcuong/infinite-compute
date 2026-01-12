<script setup>
import Hero from "../components/Hero.vue";
import WhyChooseUs from "../components/WhyChooseUs.vue";
import TopProducts from "../components/TopProducts.vue";
import InfiniteMovingCards from "../components/InfiniteMovingCards.vue";

const testimonials = [
  {
    quote:
      "The GPU selection and availability is unmatched. We've been able to source the latest NVIDIA GPUs for our research projects without any hassle.",
    name: "Elon Musk",
    title: "CEO, Tesla & SpaceX",
    image: "/images/elon-musk.webp",
  },
  {
    quote:
      "Reliable supply chain and competitive pricing. This platform makes scaling AI infrastructure incredibly efficient for our operations.",
    name: "Jeff Bezos",
    title: "Founder, Amazon",
    image: "/images/jeff-bezos.webp",
  },
  {
    quote:
      "Outstanding selection of GPUs and fast delivery. Every component we need for our latest innovations is available here.",
    name: "Jensen Huang",
    title: "CEO, NVIDIA",
    image: "/images/jensen-huang.webp",
  },
  {
    quote:
      "The platform makes it simple to access high-performance computing resources. Perfect for building the next generation of AI infrastructure.",
    name: "Mark Zuckerberg",
    title: "CEO, Meta",
    image: "/images/mark-zuckerberg.webp",
  },
  {
    quote:
      "Excellent GPU inventory and exceptional customer service. A game-changer for anyone serious about AI and machine learning.",
    name: "Sundar Pichai",
    title: "CEO, Google",
    image: "/images/sundar-pichai.webp",
  },
];
</script>

<template>
  <Hero />
  <TopProducts />
  <WhyChooseUs />

  <section class="testimonials-section">
    <div class="container">
      <h2 class="section-title">What Leaders Say About Us</h2>
    </div>
    <div class="cards-container">
      <InfiniteMovingCards
        :items="testimonials"
        direction="right"
        speed="normal"
      />
    </div>
  </section>
</template>

<style scoped>
.testimonials-section {
  padding: 4rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
  background-color: var(--background);
}

.section-title {
  font-size: 2.5rem;
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
}

@media (max-width: 768px) {
  .section-title {
    font-size: 1.75rem;
    margin-bottom: 0.75rem;
  }
}

.cards-container {
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
