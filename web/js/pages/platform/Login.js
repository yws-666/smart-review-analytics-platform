const PlatformLogin = {
  template: `
  <div class="login-page"><div class="login-box">
    <h2>🛡️ 平台管理端</h2>
    <div class="form-group"><label>管理员账号</label><input v-model="userId" placeholder="请输入管理员账号"></div>
    <div class="form-group"><label>密码</label><input v-model="password" type="password" placeholder="请输入密码"></div>
    <div class="form-group"><label>角色</label>
      <select v-model="role">
        <option value="admin">超级管理员</option>
        <option value="data_admin">数据管理员</option>
        <option value="op_admin">运营管理员</option>
        <option value="viewer">只读查看</option>
      </select>
    </div>
    <button class="login-btn" @click="login">管理员登录</button>
    <div class="alert alert-error" v-if="error">{{ error }}</div>
    <div style="margin-top:12px;font-size:13px;color:var(--text-lighter);text-align:center">
      默认账号: admin / 密码: admin123
    </div>
  </div></div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { userId:'', password:'', role:'admin', error:'' } },
  methods: {
    async login() {
      this.error = '';
      const res = await this.api.post('/api/auth/admin-login', { user_id: this.userId, password: this.password });
      if (res.error) { this.error = res.error; return; }
      localStorage.setItem('travel_token', res.token);
      localStorage.setItem('travel_user', this.userId);
      localStorage.setItem('travel_role', 'admin');
      window.location.reload();
    }
  }
};