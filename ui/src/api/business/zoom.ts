import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import { type Ref } from 'vue'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/business/zoom/report'
  },
})

/**
 * Zoom 监控报告列表
 */
const getZoomReportList: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/list`, undefined, loading)
}

/**
 * 重置 Zoom 监控报告，提示词1~5会重新生成
 * @param report_id 报告id
 */
const resetZoomReport: (report_id: number, loading?: Ref<boolean>) => Promise<Result<any>> = (
  report_id,
  loading,
) => {
  return post(`${prefix.value}/${report_id}/reset`, undefined, undefined, loading)
}

export default {
  getZoomReportList,
  resetZoomReport,
}
