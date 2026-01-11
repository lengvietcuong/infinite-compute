<script setup>
import Navbar from "./components/Navbar.vue";
import Hero from "./components/Hero.vue";
import WhyChooseUs from "./components/WhyChooseUs.vue";
import Footer from "./components/Footer.vue";
</script>

<template>
  <div class="app-container">
    <Navbar />
    <Hero />
    <WhyChooseUs />
    <Footer />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  width: 100%;
}
</style>
