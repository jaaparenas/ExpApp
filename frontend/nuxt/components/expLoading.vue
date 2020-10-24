<template>
  <v-overlay>
    <v-container class="row align-center justify-center">
      <v-progress-circular
        :size="200"
        :width="20"
        color="blue"
        indeterminate
      ></v-progress-circular>
      <v-container class="row align-center justify-center">
        <h1>{{ $t('comun.general.procesando') }}...</h1>
      </v-container>
    </v-container>
  </v-overlay>
</template>
