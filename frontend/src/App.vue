<script setup>
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";
import CartSheet from "./components/CartSheet.vue";
</script>

<template>
  <div class="app-container">
    <Navbar />
    <router-view />
    <CartSheet />
    <Footer />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  width: 100%;
}
</style>
