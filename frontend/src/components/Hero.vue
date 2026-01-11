<script setup>
</script>

<template>
  <section class="hero-section d-flex align-items-center position-relative overflow-hidden">
    <!-- Background Elements -->
    <div class="bg-grid position-absolute top-0 start-0 w-100 h-100 z-0"></div>
    <div class="glow-effect position-absolute z-0"></div>
    
    <div class="container position-relative z-1">
      <div class="row align-items-center min-vh-75 py-5">
        
        <!-- Text Content -->
        <div class="col-lg-7 text-center text-lg-start mb-5 mb-lg-0">
          <div class="badge-pill mb-4 fade-in-up">
            <span class="text-primary font-mono text-sm">Now Shipping: NVIDIA H200</span>
          </div>
          
          <h1 class="display-1 mb-4 fade-in-up delay-100">
            Compute <br>
            <span class="text-gradient">Without Limits</span>
          </h1>
          
          <p class="lead text-muted mb-5 fade-in-up delay-200" style="max-width: 600px;">
            Accelerate your AI infrastructure with the world's most advanced GPUs. 
            InfiniteCompute delivers the hardware that powers the future of intelligence.
          </p>
          
          <div class="d-flex flex-column flex-sm-row gap-3 justify-content-center justify-content-lg-start fade-in-up delay-300">
            <button class="btn btn-tech">
              Reserve Your Cluster
            </button>
            <button class="btn btn-outline-tech">
              View Specifications
            </button>
          </div>
          
          <div class="mt-5 pt-4 d-flex gap-5 justify-content-center justify-content-lg-start fade-in-up delay-300 opacity-75">
            <div>
              <h3 class="h2 mb-0 font-mono">30x</h3>
              <small class="text-muted text-uppercase">Faster Inference</small>
            </div>
            <div>
              <h3 class="h2 mb-0 font-mono">4TB/s</h3>
              <small class="text-muted text-uppercase">Memory Bandwidth</small>
            </div>
             <div>
              <h3 class="h2 mb-0 font-mono">∞</h3>
              <small class="text-muted text-uppercase">Scalability</small>
            </div>
          </div>
        </div>

        <!-- Visual Content -->
        <div class="col-lg-5 position-relative">
          <div class="hero-visual animate-float">
            <div class="glass-card p-4 position-relative">
              <!-- Decorative tech lines -->
              <div class="tech-line top-left"></div>
              <div class="tech-line bottom-right"></div>
              
              <!-- Abstract GPU Representation -->
              <div class="gpu-model-container d-flex justify-content-center align-items-center">
                 <img src="/infinity.svg" alt="Infinity Core" class="infinity-spin" style="width: 150px; height: 150px; opacity: 0.8;">
              </div>
              
              <div class="mt-4 text-center">
                <div class="font-mono text-xs text-primary mb-2">SYSTEM STATUS: ONLINE</div>
                <div class="progress" style="height: 4px; background: rgba(255,255,255,0.1);">
                  <div class="progress-bar bg-primary" role="progressbar" style="width: 100%"></div>
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
  min-height: 90vh;
}

.text-gradient {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.badge-pill {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  background: color-mix(in srgb, var(--primary), transparent 90%);
  border: 1px solid var(--border);
  backdrop-filter: blur(4px);
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

.gpu-model-container {
  height: 300px;
  background: radial-gradient(circle at center, rgba(255,255,255,0.03) 0%, transparent 70%);
  border-radius: var(--radius);
  border: 1px solid rgba(255,255,255,0.05);
}

.infinity-spin {
  filter: drop-shadow(0 0 10px var(--primary));
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
</style>
