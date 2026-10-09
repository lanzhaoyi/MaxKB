<template>
  <el-scrollbar>
    <div class="business-zammad p-16">
      <el-card style="--el-card-padding: 24px">
        <h4 class="mb-16">{{ $t('views.business.zammad.title') }}</h4>
        <el-empty :description="$t('views.business.zammad.placeholder')" />
      </el-card>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
defineOptions({ name: 'BusinessZammad' })
</script>
<style lang="scss" scoped></style>
