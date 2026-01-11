<script setup>
</script>

<template>
  <nav class="navbar navbar-expand-lg">
    <div class="container">
      <a class="navbar-brand" href="#">
        <img src="/infinity.svg" alt="Infinity Logo" class="d-inline-block align-text-top">
        InfiniteCompute
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav gap-3">
          <li class="nav-item">
            <a class="nav-link text-foreground" href="#">Products</a>
          </li>
          <li class="nav-item">
            <a class="nav-link text-foreground" href="#">Solutions</a>
          </li>
          <li class="nav-item">
            <a class="nav-link text-foreground" href="#">Research</a>
          </li>
          <li class="nav-item">
            <a class="btn btn-sm btn-outline-tech" href="#">Login</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.nav-link {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  transition: color 0.2s;
}
.nav-link:hover {
  color: var(--primary) !important;
}
</style>
