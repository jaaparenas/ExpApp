<template>
  <div class="app-shell">
    <AppHeader />
    <main class="app-main">
      <slot />
    </main>
    <footer class="app-footer">
      ExpAPP · {{ new Date().getFullYear() }} ·
      <a href="/LICENSE" target="_blank" rel="noopener">MIT License</a>
    </footer>
  </div>
</template>
