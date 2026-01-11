<script setup></script>

<template>
  <footer class="footer py-3 py-lg-5">
    <div class="container">
      <div class="row gy-4">
        <!-- Brand Section -->
        <div class="col-lg-5 col-md-12">
          <a
            class="footer-brand d-flex align-items-center gap-2 mb-3 text-decoration-none text-foreground"
            href="#"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--primary)"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="infinity-logo"
            >
              <path
                d="M6 16c5 0 7-8 12-8a4 4 0 0 1 0 8c-5 0-7-8-12-8a4 4 0 1 0 0 8"
              />
            </svg>
            <span class="brand-text fw-bold fs-5">InfiniteCompute</span>
          </a>
          <p class="text-muted pe-lg-5 mb-0 description">
            Infinite computing power for the future with secure, scalable
            infrastructure.
          </p>
        </div>

        <!-- Links Sections -->
        <div class="col-lg-2 col-md-4 col-4">
          <h6
            class="section-heading text-uppercase fw-bold mb-3 tracking-wider"
          >
            Platform
          </h6>
          <ul class="list-unstyled mb-0 d-flex flex-column gap-2">
            <li>
              <a href="#" class="text-muted text-decoration-none hover-primary"
                >Products</a
              >
            </li>
            <li>
              <a href="#" class="text-muted text-decoration-none hover-primary"
                >Solutions</a
              >
            </li>
            <li>
              <a href="#" class="text-muted text-decoration-none hover-primary"
                >Pricing</a
              >
            </li>
          </ul>
        </div>

        <div class="col-lg-2 col-md-4 col-4">
          <h6
            class="section-heading text-uppercase fw-bold mb-3 tracking-wider"
          >
            Company
          </h6>
          <ul class="list-unstyled mb-0 d-flex flex-column gap-2">
            <li>
              <a href="#" class="text-muted text-decoration-none hover-primary"
                >About</a
              >
            </li>
            <li>
              <a href="#" class="text-muted text-decoration-none hover-primary"
                >Careers</a
              >
            </li>
            <li>
              <a href="#" class="text-muted text-decoration-none hover-primary"
                >Contact</a
              >
            </li>
          </ul>
        </div>

        <div class="col-lg-3 col-md-4 col-4">
          <h6
            class="section-heading text-uppercase fw-bold mb-3 tracking-wider"
          >
            Follow
          </h6>
          <ul class="list-unstyled mb-0 d-flex flex-column gap-2">
            <li>
              <a
                href="#"
                class="social-link d-flex align-items-center gap-2 text-muted text-decoration-none hover-primary"
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
                  class="social-icon"
                >
                  <path
                    d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6 z M2 9h4v12H2z"
                  />
                  <circle cx="4" cy="4" r="2" />
                </svg>
                LinkedIn
              </a>
            </li>
            <li>
              <a
                href="#"
                class="social-link d-flex align-items-center gap-2 text-muted text-decoration-none hover-primary"
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
                  class="social-icon"
                >
                  <path
                    d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33 z"
                  />
                  <polygon
                    points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"
                  />
                </svg>
                YouTube
              </a>
            </li>
            <li>
              <a
                href="#"
                class="social-link d-flex align-items-center gap-2 text-muted text-decoration-none hover-primary"
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
                  class="social-icon"
                >
                  <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
                  <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37 z" />
                  <circle cx="17.5" cy="6.5" r="1.5" />
                </svg>
                Instagram
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div
        class="d-flex flex-column flex-md-row justify-content-between align-items-center gap-3 mt-5"
      >
        <p class="mb-0 text-muted small">
          &copy; 2026 InfiniteCompute. All rights reserved.
        </p>
        <div class="d-flex gap-4">
          <a
            href="#"
            class="text-muted text-decoration-none small hover-primary"
            >Privacy</a
          >
          <a
            href="#"
            class="text-muted text-decoration-none small hover-primary"
            >Terms</a
          >
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background-color: var(--background);
  color: var(--foreground);
  font-family: var(--font-sans);
}

.brand-text {
  font-family: var(--font-mono);
}

.section-heading {
  font-family: var(--font-mono);
  color: var(--primary) !important;
}

.text-muted {
  color: var(--muted-foreground) !important;
  font-family: var(--font-sans);
}

.hover-primary:hover {
  color: var(--primary) !important;
  transition: color 0.2s ease;
}

.social-link {
  font-family: var(--font-sans);
}

.social-icon {
  color: var(--muted-foreground);
  transition: color 0.2s ease;
}

.social-link:hover .social-icon {
  color: var(--primary);
}

.description {
  max-width: 300px;
  line-height: 1.6;
  font-size: 0.9rem;
  font-family: var(--font-sans);
}

.tracking-wider {
  letter-spacing: 0.05em;
  font-size: 0.75rem;
}

.separator {
  border-top-color: var(--border) !important;
  opacity: 0.5;
}

@media (max-width: 1279px) {
  .footer .mt-5 {
    margin-top: 2rem !important;
  }
}
</style>
