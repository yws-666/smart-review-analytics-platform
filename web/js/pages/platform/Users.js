const PlatformUsers = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <h3 style="margin-bottom:16px">👥 用户管理</h3>

    <div class="search-bar">
      <input v-model="keyword" @keyup.enter="loadUsers" placeholder="搜索用户名...">
      <button class="btn btn-primary" @click="loadUsers">搜索</button>
    </div>

    <div class="card">
      <div class="card-title">
        <span>用户列表</span>
        <span style="font-size:13px;color:var(--text-lighter);font-weight:400">共 {{ total }} 个用户</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>用户ID</th>
            <th>用户名</th>
            <th>评论数</th>
            <th>有用票</th>
            <th>粉丝</th>
            <th>平均评分</th>
            <th>角色</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.user_id">
            <td><code style="font-size:12px">{{ u.user_id?.slice(0,12) }}...</code></td>
            <td><strong>{{ u.name }}</strong></td>
            <td>{{ u.review_count }}</td>
            <td>{{ u.useful }}</td>
            <td>{{ u.fans }}</td>
            <td>⭐ {{ u.average_stars }}</td>
            <td>
              <span :class="['tag', u.role==='admin'?'tag-red':u.role==='super_admin'?'tag-red':u.role==='merchant'?'tag-blue':u.role==='viewer'?'tag-gray':'tag-green']">
                {{ u.role === 'super_admin' ? '超级管理员' : u.role === 'admin' ? '管理员' : u.role === 'merchant' ? '商家' : u.role === 'viewer' ? '只读' : '普通用户' }}
              </span>
            </td>
            <td>
              <select style="padding:4px 8px;border-radius:4px;border:1px solid var(--border);font-size:12px" :value="u.role" @change="changeRole(u.user_id, $event.target.value)">
                <option value="user">普通用户</option>
                <option value="merchant">商家</option>
                <option value="admin">管理员</option>
                <option value="viewer">只读查看</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="total > pageSize">
        <button class="page-btn" :disabled="page<=1" @click="page--;loadUsers()">‹</button>
        <button class="page-btn" v-for="p in visiblePages" :key="p" :class="{active: p===page}" @click="p!=='...' && (page=p, loadUsers())">{{ p }}</button>
        <button class="page-btn" :disabled="page>=totalPages" @click="page++;loadUsers()">›</button>
      </div>
      <div class="no-data" v-if="!loading && (!users || users.length===0)">暂无用户数据</div>
      <div class="loading" v-if="loading">加载中...</div>
    </div>
  </div>`,
  props: ['token', 'api', 'goBack', 'canGoBack'],
  data() { return { keyword:'', users:[], total:0, page:1, pageSize:20, loading:false } },
  computed: {
    totalPages() { return Math.ceil(this.total / this.pageSize) || 1; },
    visiblePages() {
      const total = this.totalPages;
      const current = this.page;
      const pages = [];
      
      if (total <= 10) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        if (current > 4) pages.push('...');
        const start = Math.max(2, current - 2);
        const end = Math.min(total - 1, current + 2);
        for (let i = start; i <= end; i++) pages.push(i);
        if (current < total - 3) pages.push('...');
        pages.push(total);
      }
      return pages;
    }
  },
  async mounted() {
    if (!this.token) return;
    await this.loadUsers();
  },
  methods: {
    async loadUsers() {
      this.loading = true;
      const res = await this.api.get('/api/platform/users', { page: this.page, page_size: this.pageSize, keyword: this.keyword });
      this.users = res.data || [];
      this.total = res.total || 0;
      this.loading = false;
    },
    async changeRole(userId, role) {
      await this.api.put('/api/platform/users/' + userId + '/role', { role });
      const idx = this.users.findIndex(u => u.user_id === userId);
      if (idx >= 0) this.users[idx].role = role;
    }
  }
};