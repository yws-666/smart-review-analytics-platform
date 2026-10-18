const UserHistory = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <div class="card">
    <div class="card-title">📋 浏览历史</div>
    <table class="data-table" v-if="list && list.length">
      <thead><tr><th>商户名称</th><th>类别</th><th>评分</th><th>浏览时间</th><th>操作</th></tr></thead>
      <tbody><tr v-for="h in list">
        <td>{{ h.business_name }}</td>
        <td><span class="tag tag-orange">{{ h.business_type }}</span></td>
        <td><span class="rating-stars">{{ '★'.repeat(Math.round(h.business_stars)) }}</span> {{ formatStars(h.business_stars) }}</td>
        <td>{{ formatTime(h.browsed_at) }}</td>
        <td><button class="btn btn-sm btn-danger" @click="removeHistory(h.business_id)">删除</button></td>
      </tr></tbody>
    </table>
    <div class="no-data" v-else>暂无浏览记录</div>
  </div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { list:[] } },
  async mounted() {
    if (!this.username) return;
    await this.loadHistory();
  },
  methods: {
    formatStars(stars) {
      return parseFloat(stars).toFixed(1);
    },
    async loadHistory() {
      const res = await this.api.get('/api/users/' + this.username + '/history');
      this.list = res || [];
    },
    formatTime(timeStr) {
      if (!timeStr) return '';
      // 只保留到秒，去掉小数点后的数
      const index = timeStr.indexOf('.');
      if (index > -1) {
        return timeStr.substring(0, index);
      }
      return timeStr;
    },
    async removeHistory(bizId) {
      if (!confirm('确定要删除这条浏览记录吗？')) return;
      await this.api.delete('/api/users/' + this.username + '/history/' + bizId);
      await this.loadHistory();
    }
  }
};