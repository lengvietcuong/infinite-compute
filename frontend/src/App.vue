<script setup>
import Navbar from "./components/Navbar.vue";
import Hero from "./components/Hero.vue";
import WhyChooseUs from "./components/WhyChooseUs.vue";
import InfiniteMovingCards from "./components/InfiniteMovingCards.vue";
import Footer from "./components/Footer.vue";

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
  <div class="app-container">
    <Navbar />
    <Hero />
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

    <Footer />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  width: 100%;
}

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
  margin-bottom: 1.5rem;
  background: linear-gradient(
    to right,
    var(--foreground),
    var(--muted-foreground)
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cards-container {
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
