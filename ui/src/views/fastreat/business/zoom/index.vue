<template>
  <el-scrollbar>
    <div class="business-zoom p-16">
      <el-card style="--el-card-padding: 24px">
        <h4 class="mb-16">{{ $t('views.business.zoom.title') }}</h4>
        <el-empty :description="$t('views.business.zoom.placeholder')" />
      </el-card>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
defineOptions({ name: 'BusinessZoom' })
</script>
<style lang="scss" scoped></style>
