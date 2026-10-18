const UserLogin = {
  template: `
  <div class="login-page">
    <div class="login-box">
      <h2>⭐ 智评优选</h2>
      
      <!-- 标签切换 -->
      <div class="login-tabs">
        <div :class="['tab', { active: !showRegister }]" @click="showRegister=false">登录</div>
        <div :class="['tab', { active: showRegister }]" @click="showRegister=true">注册</div>
      </div>
      
      <!-- 登录表单 -->
      <div v-if="!showRegister">
        <div class="form-group"><label>用户ID</label><input v-model="userId" placeholder="请输入用户ID"></div>
        <div class="form-group"><label>密码</label><input v-model="password" type="password" placeholder="请输入密码"></div>
        <button class="login-btn" @click="login">登 录</button>
      </div>
      
      <!-- 注册表单 -->
      <div v-else>
        <div class="form-group"><label>用户名</label><input v-model="regName" placeholder="请输入用户名"></div>
        <div class="form-group"><label>用户ID</label><input v-model="regId" placeholder="请输入新用户ID"></div>
        <div class="form-group"><label>密码</label><input v-model="regPwd" type="password" placeholder="请输入密码"></div>
        <button class="login-btn" @click="register" style="background:var(--info)">注 册</button>
      </div>
      
      <div class="alert alert-error" v-if="error">{{ error }}</div>
    </div>
  </div>`,
  props: ['token', 'api', 'goPage', 'username', 'goBack', 'canGoBack'],
  data() { return { userId:'', password:'', showRegister:false, regName:'', regId:'', regPwd:'', error:'' } },
  emits: ['login-success'],
  methods: {
    async login() {
      this.error = '';
      const res = await this.api.post('/api/auth/login', { user_id: this.userId, password: this.password });
      if (res.error) { this.error = res.error; return; }
      localStorage.setItem('travel_token', res.token);
      localStorage.setItem('travel_user', res.user.user_id);
      localStorage.setItem('travel_role', res.user.role || 'user');
      this.$emit('login-success', { token: res.token, username: res.user.user_id, role: res.user.role });
      window.location.reload();
    },
    async register() {
      this.error = '';
      const res = await this.api.post('/api/auth/register', { user_id: this.regId, name: this.regName, password: this.regPwd });
      if (res.error) { this.error = res.error; return; }
      localStorage.setItem('travel_token', res.token);
      localStorage.setItem('travel_user', res.user.user_id);
      localStorage.setItem('travel_role', res.user.role || 'user');
      this.$emit('login-success', { token: res.token, username: res.user.user_id, role: res.user.role });
      window.location.reload();
    }
  }
};