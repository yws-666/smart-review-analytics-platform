const MerchantAnalysis = {
  template: `<div><button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button><h3 style="margin-bottom:16px">数据分析</h3>
    <div class="chart-row"><div class="card"><div class="card-title">评论互动趋势</div><div class="chart-container"><canvas id="ma1"></canvas></div></div>
    <div class="card"><div class="card-title">评分维度雷达图</div><div class="chart-container"><canvas id="ma2"></canvas></div></div></div>
    <div class="chart-row"><div class="card"><div class="card-title">评论来源城市分布</div><div class="chart-container"><canvas id="ma3"></canvas></div></div>
    <div class="card"><div class="card-title">用户消费时段分析</div><div class="chart-container"><canvas id="ma4"></canvas></div></div></div></div>`,
  props: ['api', 'username', 'goBack', 'canGoBack'],
  async mounted() {
    if (!this.token && !this.api.tokenRef?.value) return;
    const bizId = this.username || '';
    const res = await this.api.get('/api/merchant/interaction-trend?business_id=' + bizId);
    const data = (res || []).slice(-6);
    this.$nextTick(() => {
      new Chart(document.getElementById('ma1'), {type:'bar',data:{labels:data.map(r=>r.year+'-'+r.month),datasets:[{label:'有用',data:data.map(r=>r.useful),backgroundColor:'#1890FF'},{label:'有趣',data:data.map(r=>r.funny),backgroundColor:'#FAAD14'},{label:'酷',data:data.map(r=>r.cool),backgroundColor:'#52C41A'}]},options:{responsive:true,maintainAspectRatio:false}});
      new Chart(document.getElementById('ma2'), {type:'radar',data:{labels:['质量','环境','服务','性价比','位置','氛围'],datasets:[{label:'本店',data:[4.2,3.8,4.0,3.9,3.5,4.1],borderColor:'#FF6633',backgroundColor:'rgba(255,102,51,0.2)'},{label:'同类平均',data:[3.8,3.6,3.7,3.5,3.4,3.6],borderColor:'#1890FF',backgroundColor:'rgba(24,144,255,0.1)'}]},options:{responsive:true,maintainAspectRatio:false,scales:{r:{min:0,max:5}}}});
      new Chart(document.getElementById('ma3'), {type:'doughnut',data:{labels:['Philadelphia','Tucson','Tampa','Indianapolis','Nashville','其他'],datasets:[{data:[35,18,15,12,10,10],backgroundColor:['#FF6633','#1890FF','#52C41A','#FAAD14','#722ED1','#999']}]},options:{responsive:true,maintainAspectRatio:false}});
      new Chart(document.getElementById('ma4'), {type:'bar',data:{labels:['6-9时','9-12时','12-14时','14-17时','17-20时','20-23时','23-6时'],datasets:[{label:'访问量',data:[50,120,280,150,350,200,30],backgroundColor:'#FF6633'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
    });
  }
};

const MerchantTrends = {
  template: `<div><button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button><h3 style="margin-bottom:16px">趋势分析</h3>
    <div class="card"><div class="card-title">评分趋势</div><div class="chart-full"><canvas id="mt1"></canvas></div></div>
    <div class="card"><div class="card-title">评论情感趋势分析</div><div class="chart-full"><canvas id="mt2"></canvas></div></div>
    <div class="card"><div class="card-title">关键指标趋势对比</div><div class="chart-full"><canvas id="mt3"></canvas></div></div></div>`,
  props: ['api', 'username', 'goBack', 'canGoBack'],
  async mounted() {
    this.$nextTick(() => {
      new Chart(document.getElementById('mt1'), {type:'line',data:{labels:['2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04'],datasets:[{label:'评分',data:[3.7,3.8,3.8,3.9,3.9,4.0,4.0],borderColor:'#FF6633',backgroundColor:'rgba(255,102,51,0.1)',fill:true,tension:0.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{min:3,max:5}}}});
      new Chart(document.getElementById('mt2'), {type:'line',data:{labels:['2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04'],datasets:[{label:'正面',data:[65,68,70,72,75,78,80],borderColor:'#52C41A',fill:true,tension:0.4},{label:'中性',data:[25,22,20,18,17,15,14],borderColor:'#FAAD14',fill:true,tension:0.4},{label:'负面',data:[10,10,10,10,8,7,6],borderColor:'#FF4D4F',fill:true,tension:0.4}]},options:{responsive:true,maintainAspectRatio:false}});
      new Chart(document.getElementById('mt3'), {type:'line',data:{labels:['2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04'],datasets:[{label:'评论数',data:[5,8,6,9,7,11,12],borderColor:'#1890FF',yAxisID:'y'},{label:'评分(x10)',data:[37,38,38,39,39,40,40],borderColor:'#FF6633',yAxisID:'y1'}]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{position:'left'},y1:{position:'right'}}}});
    });
  }
};

const MerchantWordCloud = {
  template: `<div><button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button><h3 style="margin-bottom:16px">评论分析</h3>
    <div class="chart-row">
      <div class="card" style="flex:1.2">
        <div class="card-title">用户评价关键词 <span class="tag tag-green">基于text_cleaned数据</span></div>
        <div class="word-cloud" v-if="words && words.length"><span v-for="w in words" class="word" :style="{fontSize:w.weight*1.5+10+'px',color:w.color,fontWeight:w.weight>10?'700':'400'}">{{ w.text }}</span></div>
        <div class="loading" v-else>加载中...</div>
      </div>
      <div class="card" style="flex:1.8">
        <div class="card-title">用户评论 <span style="font-size:12px;font-weight:400;color:#999">共 {{ total }} 条</span></div>
        <div class="review-list" v-if="reviews && reviews.length">
          <div class="review-item" v-for="r in reviews" :key="r.review_id">
            <div class="review-header">
              <span class="review-user">{{ r.user_id?.slice(0,8) }}...</span>
              <span class="review-stars">{{ '★'.repeat(Math.round(r.stars)) }}</span>
              <span class="review-date">{{ r.date }}</span>
            </div>
            <div class="review-text">{{ r.text || '(暂无评论内容)' }}</div>
            <div class="review-meta">
              <span>👍 {{ r.useful }}</span>
              <span>😂 {{ r.funny }}</span>
              <span>😎 {{ r.cool }}</span>
            </div>
          </div>
        </div>
        <div class="loading" v-else-if="loading">加载中...</div>
        <div class="no-data" v-else>暂无评论数据</div>
        <div class="pagination" v-if="total > pageSize">
          <button class="page-btn" :disabled="page<=1" @click="page--;loadReviews()">‹</button>
          <template v-for="p in visiblePages" :key="p">
            <span v-if="p==='...'" class="page-btn disabled">...</span>
            <button v-else class="page-btn" :class="{active: p===page}" @click="page=p;loadReviews()">{{ p }}</button>
          </template>
          <button class="page-btn" :disabled="page>=totalPages" @click="page++;loadReviews()">›</button>
        </div>
      </div>
    </div></div>`,
  props: ['api', 'username', 'goBack', 'canGoBack'],
  data() { return { words:[], reviews:[], total:0, page:1, pageSize:5, loading:false } },
  computed: {
    totalPages() { return Math.ceil(this.total / this.pageSize) || 1; },
    visiblePages() {
      const total = this.totalPages;
      const current = this.page;
      const pages = [];
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        if (current > 3) pages.push('...');
        const start = Math.max(2, current - 1);
        const end = Math.min(total - 1, current + 1);
        for (let i = start; i <= end; i++) pages.push(i);
        if (current < total - 2) pages.push('...');
        pages.push(total);
      }
      return pages;
    }
  },
  async mounted() {
    await Promise.all([this.loadWordcloud(), this.loadReviews()]);
  },
  methods: {
    async loadWordcloud() {
      const bizId = this.username || '';
      const res = await this.api.get('/api/merchant/wordcloud?business_id=' + bizId);
      const colors = ['#FF6633','#1890FF','#52C41A','#FAAD14','#722ED1','#13C2C2','#EB2F96'];
      this.words = (res || []).map(w => ({ ...w, color: colors[Math.floor(Math.random()*colors.length)] }));
    },
    async loadReviews() {
      this.loading = true;
      const bizId = this.username || '';
      const res = await this.api.get('/api/merchant/reviews?business_id=' + bizId + '&page=' + this.page + '&page_size=' + this.pageSize);
      this.reviews = res.data || [];
      this.total = res.total || 0;
      this.loading = false;
    }
  }
};

const MerchantInfo = {
  template: `<div><button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button><h3 style="margin-bottom:16px">商家详情</h3>
    <div class="card" style="background: linear-gradient(135deg, #FFF5F0, #FFF8F3);padding:24px">
      <div class="biz-header">
        <div class="biz-icon">🏪</div>
        <div class="biz-info">
          <h2>{{ info.name }}</h2>
          <div class="biz-rating">
            <span class="big-stars">{{ '★'.repeat(Math.round(info.stars)) }}</span>
            <span class="big-num">{{ info.stars }}</span>
            <span class="review-count">({{ info.review_count }}条评论)</span>
          </div>
        </div>
        <div class="biz-status" :class="{open: info.is_open}">{{ info.is_open ? '营业中' : '已关闭' }}</div>
      </div>
    </div>

    <div class="chart-row">
      <div class="card">
        <div class="card-title">📋 基本信息</div>
        <div class="info-grid">
          <div class="info-item"><span class="info-label">地址</span><span class="info-value">{{ info.address }}</span></div>
          <div class="info-item"><span class="info-label">城市</span><span class="info-value">{{ info.city }}</span></div>
          <div class="info-item"><span class="info-label">州</span><span class="info-value">{{ info.state }}</span></div>
          <div class="info-item"><span class="info-label">邮编</span><span class="info-value">{{ info.postal_code }}</span></div>
          <div class="info-item"><span class="info-label">商户ID</span><span class="info-value code">{{ info.business_id }}</span></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">🏷️ 分类标签</div>
        <div class="category-tags">
          <span v-for="(cat, i) in categories" :key="i" class="tag tag-orange">{{ cat }}</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">✏️ 修改信息</div>
      <div class="form-grid">
        <div class="form-group"><label>商户名称</label><input v-model="form.name"></div>
        <div class="form-group"><label>地址</label><input v-model="form.address"></div>
        <div class="form-group"><label>城市</label><input v-model="form.city"></div>
        <div class="form-group"><label>州</label><input v-model="form.state"></div>
        <div class="form-group"><label>邮编</label><input v-model="form.postal_code"></div>
      </div>
      <button class="btn btn-primary" @click="save">保存修改</button>
    </div>
  </div>`,
  props: ['api', 'username', 'goBack', 'canGoBack'],
  data() { return { info:{}, form:{}, categories:[] } },
  async mounted() {
    const bizId = this.username || '';
    const res = await this.api.get('/api/merchant/info?business_id=' + bizId);
    if (res && !res.error) {
      this.info = res;
      this.form = { name: res.name, address: res.address, city: res.city, state: res.state, postal_code: res.postal_code };
      this.categories = res.categories ? res.categories.split(',').map(c => c.trim()).filter(c => c) : [];
    }
  },
  methods: {
    async save() {
      const bizId = this.username || '';
      await this.api.put('/api/merchant/info?business_id=' + bizId, this.form);
      this.info.name = this.form.name;
      this.info.address = this.form.address;
      this.info.city = this.form.city;
      this.info.state = this.form.state;
      this.info.postal_code = this.form.postal_code;
      alert('更新成功');
    }
  }
};