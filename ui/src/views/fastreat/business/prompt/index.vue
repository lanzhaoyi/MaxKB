<template>
  <el-scrollbar>
    <div class="business-prompt p-16">
      <el-card style="--el-card-padding: 24px">
        <h4 class="mb-16">{{ $t('views.business.prompt.title') }}</h4>
        <el-empty :description="$t('views.business.prompt.placeholder')" />
      </el-card>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
defineOptions({ name: 'BusinessPrompt' })
</script>
<style lang="scss" scoped></style>
