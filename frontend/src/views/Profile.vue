<script setup>
import {reactive,ref,onMounted} from 'vue'
import {api,auth} from '../api'
import {safeImage} from '../domain'
const form=reactive({nickname:'',avatar:'',contact:''}),error=ref(''),notice=ref(''),busy=ref(false),ready=ref(false)
async function load(){error.value='';try{auth.user=await api('/auth/me');Object.assign(form,{nickname:auth.user.nickname,avatar:auth.user.avatar||'',contact:auth.user.contact||''});ready.value=true}catch(e){error.value=e.message}}
onMounted(load)
async function save(){busy.value=true;error.value='';notice.value='';try{if(form.avatar&&!safeImage(form.avatar))throw new Error('头像须为 http(s) 地址或站内图片路径');auth.user=await api('/auth/me',{method:'PATCH',body:{nickname:form.nickname,avatar:form.avatar||null,contact:form.contact||null}});notice.value='个人资料已保存'}catch(e){error.value=e.message}finally{busy.value=false}}
</script>
<template><div class="section-heading"><div><h1>个人资料</h1></div></div><p v-if="error" class="error" role="alert">{{error}} <button v-if="!ready" @click="load">重试</button></p><form v-if="ready" class="panel form-panel" @submit.prevent="save"><div class="profile-heading"><b class="avatar">{{form.nickname.slice(0,1)}}</b><div><h2>{{auth.user.nickname}}</h2><p class="muted">{{auth.user.is_admin?'管理员':'校园用户'}} · {{auth.user.student_no}}</p></div></div><label>邮箱<input :value="auth.user.email" disabled></label><label>昵称<input v-model.trim="form.nickname" required maxlength="20"></label><label>联系方式<input v-model.trim="form.contact" maxlength="100" placeholder="微信、QQ 或电话"></label><label>头像地址<input v-model.trim="form.avatar" maxlength="255" placeholder="https://…"></label><p v-if="notice" class="success" role="status">{{notice}}</p><button class="primary" :disabled="busy">{{busy?'保存中…':'保存资料'}}</button></form></template>
