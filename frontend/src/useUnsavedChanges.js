import { onBeforeUnmount, watch } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

/** 保护传入的未保存状态 ref；无返回值，离开页面时确认，卸载时清除浏览器监听。 */
export function useUnsavedChanges(dirty) {
  const confirmLeave = () => !dirty.value || window.confirm('有尚未保存或提交的内容，离开后可能丢失。确定离开吗？')
  const beforeUnload = (event) => {
    if (!dirty.value) return
    event.preventDefault()
    event.returnValue = ''
  }
  onBeforeRouteLeave(confirmLeave)
  // 切换学习日会复用组件，也需要保护草稿；查询参数变化不算离开。
  onBeforeRouteUpdate((to, from) => to.path === from.path || confirmLeave())
  watch(dirty, (value) => {
    window.removeEventListener('beforeunload', beforeUnload)
    if (value) window.addEventListener('beforeunload', beforeUnload)
  }, { immediate: true, flush: 'sync' })
  onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
}
