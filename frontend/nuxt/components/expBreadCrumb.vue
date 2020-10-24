<template>
  <v-breadcrumbs v-if="Array.isArray(BreadCrumb) && BreadCrumb.length > 0" :dense="true" :items="BreadCrumb" class="pb-1">
    <template v-slot:item="{ item }">
      <v-breadcrumbs-item
        :small="true"
        class="text-info item-miga py-0"
        @click="((item.link != '') ? openRoute(item.link): false)"
        :disabled="item.disabled">
        {{ item.name.toUpperCase() }}
      </v-breadcrumbs-item>
    </template>
  </v-breadcrumbs>
</template>

<script>
import BasicMixin from '@/mixins/basic'

export default {
  mixins: [ BasicMixin ],
  name: 'ExpBreadCrumb',
  data () {
    return {
    }
  },
  computed: {
    BreadCrumb () {
      return this.$store.getters.getBreadcrumbItems
    }
  }
}
</script>

<style>
  ul.breadcrumb > li > span {
    padding-left: 3px;
  }
  .item-miga {
    cursor: pointer;
    font-size: .8rem !important;
  }
</style>
