const MerchantLogin = {
  template: `
  <div class="login-page"><div class="login-box">
    <h2>🏪 商家后台</h2>
    <div class="form-group"><label>商户ID</label><input v-model="bizId" placeholder="请输入商户ID"></div>
    <div class="form-group"><label>密码</label><input v-model="password" type="password" placeholder="请输入密码（默认123456）"></div>
    <button class="login-btn" @click="login">商家登录</button>
    <div class="alert alert-error" v-if="error">{{ error }}</div>
    <div style="margin-top:12px;font-size:13px;color:var(--text-lighter);text-align:center">首次使用密码：123456</div>
  </div></div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { bizId:'', password:'', error:'' } },
  methods: {
    async login() {
      this.error = '';
      const res = await this.api.post('/api/auth/merchant-login', { business_id: this.bizId, password: this.password });
      if (res.error) { this.error = res.error; return; }
      localStorage.setItem('travel_token', res.token);
      localStorage.setItem('travel_user', this.bizId);
      localStorage.setItem('travel_role', 'merchant');
      window.location.reload();
    }
  }
};