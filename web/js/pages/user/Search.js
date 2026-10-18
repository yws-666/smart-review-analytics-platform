const UserSearch = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <div class="search-bar">
      <input v-model="keyword" @keyup.enter="search" placeholder="搜索商家...">
      <select v-model="filterType"><option value="">全部分类</option><option v-for="t in types" :value="t">{{ t }}</option></select>
      <select v-model="filterCity"><option value="">全部城市</option><option v-for="c in cities" :value="c">{{ c }}</option></select>
      <select v-model="sort" @change="search"><option value="stars">评分最高</option><option value="review_count">评论最多</option></select>
      <button class="btn btn-primary" @click="search">筛选</button>
    </div>
    <div style="margin-bottom:12px;font-size:13px;color:#999">找到 {{ total }} 个结果</div>
    <div v-if="list && list.length">
      <div class="biz-grid">
        <div class="biz-card" v-for="b in list" @click="viewDetail(b.business_id)">
          <div class="biz-img">{{ getCategoryIcon(b.business_type) }}</div>
          <div class="biz-info">
            <div class="biz-name">{{ b.name }}</div>
            <div class="biz-tag">{{ b.business_type }}</div>
            <div class="biz-rating"><span class="rating-num">{{ formatStars(b.stars) }}</span><span class="rating-stars">{{ '★'.repeat(Math.round(b.stars)) }}</span><span class="review-count">({{ b.review_count }}条)</span></div>
            <div class="biz-meta"><span>📍 {{ b.city }}</span></div>
          </div>
        </div>
      </div>
      <div class="pagination">
        <button class="page-btn" :disabled="page<=1" @click="page--;search()">‹</button>
        <button class="page-btn active">{{ page }}</button>
        <button class="page-btn" :disabled="page*20>=total" @click="page++;search()">›</button>
      </div>
    </div>
    <div class="no-data" v-else-if="!loading">没有找到匹配的商户</div>
    <div class="loading" v-else>搜索中...</div>
  </div>`,
  props: ['token', 'api', 'goBack', 'canGoBack'],
  data() { return { keyword:'', filterType:'', filterCity:'', sort:'stars', list:[], total:0, page:1, types:[], cities:[], loading:false, 
    categoryIcons: { '美食餐饮':'🍜','购物零售':'🛍️','酒店旅游':'🏨','休闲娱乐':'🎭','生活服务':'🔧','美容美发':'💇','医疗健康':'🏥','汽车服务':'🚗','宠物服务':'🐾','教育培训':'📚','其他':'📌' } } },
  async mounted() {
    const [catRes, cityRes] = await Promise.all([this.api.get('/api/businesses/categories'), this.api.get('/api/businesses/cities')]);
    this.types = (catRes || []).map(c => c.type);
    this.cities = (cityRes || []).map(c => c.city);
    
    // 从 localStorage 读取搜索参数
    const savedType = localStorage.getItem('travel_search_type');
    const savedKeyword = localStorage.getItem('travel_search_keyword');
    const savedCity = localStorage.getItem('travel_search_city');
    
    if (savedType) {
      this.filterType = savedType;
      localStorage.removeItem('travel_search_type');
    }
    if (savedKeyword) {
      this.keyword = savedKeyword;
      localStorage.removeItem('travel_search_keyword');
    }
    if (savedCity) {
      this.filterCity = savedCity;
      localStorage.removeItem('travel_search_city');
    }
    
    // 执行搜索
    this.search();
  },
  methods: {
    formatStars(stars) {
      return parseFloat(stars).toFixed(1);
    },
    getCategoryIcon(type) { return this.categoryIcons[type] || '📌'; },
    async search() {
      this.loading = true;
      const params = { page: this.page, page_size: 20, sort: this.sort, order: 'desc' };
      if (this.keyword) params.keyword = this.keyword;
      if (this.filterType) params.type = this.filterType;
      if (this.filterCity) params.city = this.filterCity;
      const res = await this.api.get('/api/businesses', params);
      this.list = res.data || [];
      this.total = res.total || 0;
      this.loading = false;
    },
    viewDetail(id) { this.$emit('navigate', 'detail'); this.$nextTick(() => { EventBus.emit('viewBusiness', id); }); }
  }
};