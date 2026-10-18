const UserCenter = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <div v-if="!user" class="loading">请先登录</div>
    <div v-else>
      <div class="user-header">
        <div class="user-avatar">👤</div>
        <div style="flex:1">
          <div style="font-size:20px;font-weight:700">{{ user.name }}</div>
          <div style="font-size:13px;opacity:0.8">ID: {{ user.user_id }}</div>
          <div class="user-stats" style="margin-top:8px">
            <div class="stat"><div class="stat-num">{{ user.review_count }}</div><div class="stat-label">评论</div></div>
            <div class="stat"><div class="stat-num">{{ user.useful }}</div><div class="stat-label">有用</div></div>
            <div class="stat"><div class="stat-num">{{ user.fans }}</div><div class="stat-label">粉丝</div></div>
            <div class="stat"><div class="stat-num">{{ user.average_stars }}</div><div class="stat-label">平均评分</div></div>
          </div>
        </div>
        <button class="btn btn-sm btn-outline-white" @click="refreshData">🔄 刷新</button>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div class="card">
          <div class="card-title">📊 我的数据</div>
          <div style="font-size:14px;line-height:2.2">
            <div>评论总数：<strong>{{ user.review_count }}</strong> 条</div>
            <div>获得有用票：<strong>{{ user.useful }}</strong></div>
            <div>获得有趣票：<strong>{{ user.funny }}</strong></div>
            <div>获得不友好票：<strong>{{ user.cool }}</strong></div>
            <div>粉丝数：<strong>{{ user.fans }}</strong></div>
            <div>平均评分：<strong>{{ user.average_stars }}</strong></div>
          </div>
        </div>
        <div class="card">
          <div class="card-title">✏️ 编辑资料</div>
          <div class="form-group"><label>昵称</label><input v-model="editName" :placeholder="user.name"></div>
          <button class="btn btn-primary" @click="updateProfile">保存修改</button>
        </div>
      </div>
    </div>
  </div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { user:null, editName:'' } },
  async mounted() {
    if (!this.username) return;
    await this.loadUserInfo();
  },
  methods: {
    async loadUserInfo() {
      const res = await this.api.get('/api/auth/profile');
      this.user = res;
      this.editName = res.name || '';
    },
    async refreshData() {
      await this.loadUserInfo();
      alert('数据已刷新');
    },
    async updateProfile() {
      await this.api.put('/api/users/' + this.username, { name: this.editName });
      alert('更新成功');
      await this.loadUserInfo();
    }
  }
};