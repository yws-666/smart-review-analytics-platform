const UserFavorites = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <div class="card">
    <div class="card-title">❤️ 我的收藏 <span class="tag tag-orange">{{ list?.length || 0 }}家商户</span></div>
    <div class="fav-grid" v-if="list && list.length">
      <div class="fav-item" v-for="f in list" @click="viewDetail(f.business_id)" style="cursor:pointer"><div class="fav-icon">⭐</div>
        <div style="flex:1"><div style="font-size:14px;font-weight:500">{{ f.business_name }}</div><div style="font-size:12px;color:var(--text-lighter)">{{ f.business_type }} · ★{{ formatStars(f.business_stars) }}</div></div>
        <button class="btn btn-sm" style="background:var(--danger);color:white;font-size:11px" @click.stop="remove(f.business_id)">取消</button>
      </div>
    </div>
    <div class="no-data" v-else>还没有收藏</div>
  </div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { list:[] } },
  async mounted() {
    if (!this.username) return;
    const res = await this.api.get('/api/users/' + this.username + '/favorites');
    this.list = res || [];
  },
  methods: {
    formatStars(stars) {
      return parseFloat(stars).toFixed(1);
    },
    viewDetail(id) { 
      this.$emit('navigate', 'detail'); 
      this.$nextTick(() => { EventBus.emit('viewBusiness', id); }); 
    },
    async remove(bizId) {
      await this.api.del('/api/users/' + this.username + '/favorites/' + bizId);
      this.list = this.list.filter(f => f.business_id !== bizId);
    }
  }
};