import { reactive } from 'vue'
import { errorText } from './domain'
const key = 'campus-market-token'
export const auth = reactive({token: sessionStorage.getItem(key) || '', user:null})
export function setSession(data) { auth.token=data.token; auth.user=data.user; sessionStorage.setItem(key,data.token) }
export function clearSession() { auth.token=''; auth.user=null; sessionStorage.removeItem(key) }
export async function api(path, {method='GET', body}={}) {
  const controller = new AbortController()
  const timer = setTimeout(()=>controller.abort(),15000)
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE || '/api'}${path}`, {method, signal:controller.signal, headers:{...(body ? {'Content-Type':'application/json'} : {}), ...(auth.token ? {Authorization:`Bearer ${auth.token}`} : {})}, ...(body ? {body:JSON.stringify(body)} : {})})
    const data = await response.json().catch(()=>null)
    if (!response.ok) {
      if (response.status===401) { clearSession(); window.dispatchEvent(new Event('auth-expired')) }
      throw new Error(data ? errorText(data) : `服务暂不可用（${response.status}），请检查后端是否启动`)
    }
    return data
  } catch(error) {
    if(error.name==='AbortError') throw new Error('请求超时，请检查后端服务后重试')
    if(error instanceof TypeError) throw new Error('无法连接服务，请确认后端已启动')
    throw error
  } finally {clearTimeout(timer)}
}
