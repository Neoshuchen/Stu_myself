<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const community = computed(() => route.path === '/community-guidelines')
</script>

<template>
  <main class="legal-page">
    <RouterLink class="brand" to="/"><span class="brand-mark">知</span><b>知序</b></RouterLink>
    <article class="panel legal-copy">
      <template v-if="community">
        <p class="eyebrow">COMMUNITY GUIDELINES</p>
        <h1>社区与课程使用规范</h1>
        <p>请尊重其他学习者，不发布违法、骚扰、隐私数据、真实账号凭据、恶意程序或未经授权的采集与逆向目标。</p>
        <h2>授权边界</h2>
        <p>采集与逆向实验仅限本人资产、专用靶场或取得明确授权的样本。禁止把课程用于绕过访问控制、窃取数据或破坏第三方系统。</p>
        <h2>举报和处置</h2>
        <p>举报进入人工审核；除明显紧急风险外，不因单次举报自动删除内容或封禁账号。管理员应记录处置理由，并允许用户提出申诉。</p>
        <h2>课程共建</h2>
        <p>提交课程补充即表示你有权分享相关内容；请勿复制无授权材料或上传包含个人数据的样本。</p>
      </template>
      <template v-else>
        <p class="eyebrow">PRIVACY</p>
        <h1>隐私说明</h1>
        <p>知序处理账号名、邮箱、学习进度、复盘、知识缺口、学习证据、社区内容、举报及必要安全日志，用于身份验证、学习功能、内容审核和安全防护。</p>
        <h2>保存与安全</h2>
        <p>验证码只短期保存在缓存中；访问令牌不持久化到浏览器，刷新令牌使用 HttpOnly Cookie。附件通过权限校验和短时签名访问。</p>
        <h2>AI 学习助手</h2>
        <p>只有你主动提问时，问题、最近对话和上传内容才会发送到你选择的第三方模型 HTTPS 接口。临时 Key 不持久化；主动保存的配置会与账号绑定，API Key 使用独立主密钥加密，配置名称、接口 URL、协议和模型名称作为非秘密信息保存。你可以长期保存、修改、切换或删除多条模型服务。图片和文件正文只在 Redis 中限时缓存，文字对话保留到你删除会话或账号。第三方留存遵循对应供应商政策，AI 回答可能出错，也不会自动改变学习完成状态。</p>
        <h2>你的选择</h2>
        <p>你可以在能力图谱导出 Markdown 或 JSON 学习记录，也可以在个人中心停用或删除账号。账号删除会清理学习记录、附件和社区关系；备份中的副本在保留周期结束后自然清除。</p>
        <h2>联系与投诉</h2>
        <p>如需访问、更正、导出、删除数据或投诉，请通过站点运营方在正式域名公示的隐私联系渠道提出。</p>
      </template>
      <nav class="legal-nav">
        <RouterLink to="/privacy">隐私说明</RouterLink>
        <RouterLink to="/community-guidelines">社区规范</RouterLink>
        <RouterLink to="/login">返回登录</RouterLink>
      </nav>
    </article>
  </main>
</template>
