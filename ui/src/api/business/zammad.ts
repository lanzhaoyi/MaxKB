import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import { type Ref } from 'vue'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/business/zammad'
  },
})

/**
 * 查询 Zammad 数据
 * @param data {dataType, region, createdAtStart, createdAtEnd, pageNo, pageSize, ...多维度分页}
 */
const queryData: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix.value}/data/query`, data, undefined, loading)
}

/**
 * 分析任务列表
 * @param params {data_type, status, region}
 */
const getTaskList: (
  page_no: number,
  page_size: number,
  params: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page_no, page_size, params, loading) => {
  return get(`${prefix.value}/tasks/${page_no}/${page_size}`, params, loading)
}

/**
 * 创建分析任务
 * @param data {dataType, region, createdAtStart, createdAtEnd, promptText, sampleSize}
 */
const createTask: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix.value}/task`, data, undefined, loading)
}

/**
 * 按任务回查数据明细
 * @param params {region}
 */
const getTaskData: (
  task_id: number,
  page_no: number,
  page_size: number,
  params: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (task_id, page_no, page_size, params, loading) => {
  return get(`${prefix.value}/task/${task_id}/data/${page_no}/${page_size}`, params, loading)
}

/**
 * 分析结果
 * @param params {region}
 */
const getTaskResult: (
  task_id: number,
  params: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (task_id, params, loading) => {
  return get(`${prefix.value}/task/${task_id}/result`, params, loading)
}

/**
 * 失败任务重试
 * @param params {region, promptText, sampleSize}
 */
const retryTask: (
  task_id: number,
  params: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (task_id, params, loading) => {
  return post(`${prefix.value}/task/${task_id}/retry`, undefined, params, loading)
}

export default {
  queryData,
  getTaskList,
  createTask,
  getTaskData,
  getTaskResult,
  retryTask,
}
