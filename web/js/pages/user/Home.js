const UserHome = {
  template: `
  <div>
    <div class="search-bar">
      <input v-model="keyword" @keyup.enter="searchBusinesses" placeholder="搜索商家名称、地址...">
      <select v-model="searchType"><option value="">全部分类</option><option v-for="t in types" :value="t">{{t}}</option></select>
      <select v-model="searchCity"><option value="">全部城市</option><option v-for="c in cities" :value="c">{{c}}</option></select>
      <button class="btn btn-primary" @click="searchBusinesses">搜索</button>
    </div>

    <div class="category-nav-container">
      <div class="category-nav">
        <div class="category-item" v-for="c in categoryData" :key="c.type" @click="searchByCategory(c.type)">
          <div class="cat-icon">{{ c.icon }}</div>
          <div class="cat-name">{{ c.type }}</div>
          <div class="cat-count">{{ c.count }}家</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">🔥 热门推荐 <span class="more" @click="goSearch">查看更多 ›</span></div>
      <div class="biz-grid" v-if="hotBusinesses && hotBusinesses.length">
        <div class="biz-card" v-for="(b,i) in hotBusinesses" @click="viewDetail(b.business_id)">
          <div class="biz-img">{{ b.categories?.includes('Restaurants') ? '🍜' : b.categories?.includes('Hotel') ? '🏨' : '🏪' }}<div class="biz-badge">TOP {{ i+1 }}</div></div>
          <div class="biz-info">
            <div class="biz-name">{{ b.name }}</div>
            <div class="biz-rating"><span class="rating-num">{{ formatStars(b.stars) }}</span><span class="rating-stars">{{ '★'.repeat(Math.round(b.stars)) }}</span><span class="review-count">({{ b.review_count }}条评价)</span></div>
            <div class="biz-meta"><span>📍 {{ b.city }}</span></div>
          </div>
        </div>
      </div>
      <div class="loading" v-else>加载中...</div>
    </div>

    <div class="card">
      <div class="card-title">💡 为你推荐 <span class="tag tag-green">智能推荐</span></div>
      <div class="biz-grid" v-if="recommendBusinesses && recommendBusinesses.length">
        <div class="biz-card" v-for="b in recommendBusinesses" @click="viewDetail(b.business_id)">
          <div class="biz-img">{{ b.categories?.includes('Restaurants') ? '🍴' : '⭐' }}</div>
          <div class="biz-info">
            <div class="biz-name">{{ b.name }}</div>
            <div class="biz-rating"><span class="rating-num">{{ formatStars(b.stars) }}</span><span class="rating-stars">{{ '★'.repeat(Math.round(b.stars)) }}</span><span class="review-count">({{ b.review_count }}条)</span></div>
            <div class="biz-meta"><span>📍 {{ b.city }}</span></div>
          </div>
        </div>
      </div>
      <div class="loading" v-else>加载中...</div>
    </div>
  </div>`,
  props: ['token', 'api', 'goBack', 'canGoBack'],
  data() { return { keyword:'', searchType:'', searchCity:'', types:[], cities:[], categoryData:[], hotBusinesses:[], recommendBusinesses:[], icons: { '美食餐饮':'🍜','购物零售':'🛍️','酒店旅游':'🏨','休闲娱乐':'🎭','生活服务':'🔧','美容美发':'💇','医疗健康':'🏥','汽车服务':'🚗','宠物服务':'🐾','教育培训':'📚','其他':'📌' } } },
  async mounted() {
    const [catRes, cityRes, hotRes, recRes] = await Promise.all([
      this.api.get('/api/businesses/categories'),
      this.api.get('/api/businesses/cities'),
      this.api.get('/api/businesses/hot', { limit: 6 }),
      this.api.get('/api/businesses/recommend', { limit: 6 })
    ]);
    this.types = (catRes || []).map(c => c.type);
    this.cities = (cityRes || []).map(c => c.city);
    this.categoryData = (catRes || []).map(c => ({ ...c, icon: this.icons[c.type] || '📌' }));
    this.hotBusinesses = hotRes || [];
    this.recommendBusinesses = recRes || [];
  },
  methods: {
    formatStars(stars) {
      return parseFloat(stars).toFixed(1);
    },
    goSearch() { this.$emit('navigate', 'search'); },
    searchBusinesses() {
      localStorage.setItem('travel_search_keyword', this.keyword || '');
      localStorage.setItem('travel_search_type', this.searchType || '');
      localStorage.setItem('travel_search_city', this.searchCity || '');
      this.$emit('navigate', 'search');
    },
    searchByCategory(type) {
      localStorage.setItem('travel_search_type', type);
      localStorage.setItem('travel_search_keyword', '');
      localStorage.setItem('travel_search_city', '');
      this.$emit('navigate', 'search');
    },
    viewDetail(id) { this.$emit('navigate', 'detail'); this.$nextTick(() => { EventBus.emit('viewBusiness', id); }); }
  }
};