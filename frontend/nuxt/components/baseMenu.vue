<template>
  <v-list dense nav>
    <v-list-item-group color="primary">
      <template v-for="(item, i) in items">
        <v-list-group v-show="item.visible" :key="i" v-if="item.items && item.items.length>0"
          :prepend-icon="item.icon"
          :color="item.color"
          no-action>
          <template v-slot:activator>
            <v-list-item-content>
              <v-list-item-title class="font-weight-regular">{{ item.name }}</v-list-item-title>
            </v-list-item-content>
          </template>
          <base-menu :items="item.items" />
        </v-list-group>
          <v-list-item v-show="item.visible" :to="fixPageRoute(item.link)" exact :key="i" v-else>
          <v-list-item-icon :color="item.color">
            <v-icon :color="item.color">{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title class="font-weight-regular">{{ item.name }}</v-list-item-title>
        </v-list-item>
      </template>
    </v-list-item-group>
  </v-list>
</template>

<script>
  import basicMixins from '@/mixins/basic'

  export default {
    mixins: [ basicMixins ],
    name: 'base-menu',
    props: {
      items: Array,
      itemKey: 0
    }
  }
</script>