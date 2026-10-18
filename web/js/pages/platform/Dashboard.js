const PlatformDashboard = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <h3 style="margin-bottom:16px">📊 平台数据监控中心</h3>

    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background:#FFF5F0;color:var(--primary)">🏪</div>
        <div class="stat-value">{{ overview.business_count?.toLocaleString() || 0 }}</div>
        <div class="stat-label">商户总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#FFF5F0;color:var(--info)">👥</div>
        <div class="stat-value">{{ overview.user_count?.toLocaleString() || 0 }}</div>
        <div class="stat-label">用户总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#FFF5F0;color:var(--success)">💬</div>
        <div class="stat-value">{{ overview.review_count?.toLocaleString() || 0 }}</div>
        <div class="stat-label">评论总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#FFF5F0;color:var(--warning)">📝</div>
        <div class="stat-value">{{ overview.tip_count?.toLocaleString() || 0 }}</div>
        <div class="stat-label">提示总数</div>
      </div>
    </div>

    <div class="chart-row">
      <div class="card">
        <div class="card-title">📈 商户类别分布</div>
        <div class="chart-container"><canvas id="pd1"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">🏙️ TOP10 城市排名</div>
        <div class="chart-container"><canvas id="pd2"></canvas></div>
      </div>
    </div>

    <div class="chart-row">
      <div class="card">
        <div class="card-title">⭐ 评分分布</div>
        <div class="chart-container"><canvas id="pd3"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">📅 平台月度趋势</div>
        <div class="chart-container"><canvas id="pd4"></canvas></div>
      </div>
    </div>
  </div>`,
  props: ['token', 'api', 'goBack', 'canGoBack'],
  data() { return { overview: {}, typeDist: null, cityRank: null, starsDist: null, monthlyTrend: null } },
  async mounted() {
    if (!this.token) return;
    const [ov, td, cr, sd, mt] = await Promise.all([
      this.api.get('/api/platform/overview'),
      this.api.get('/api/platform/business-type-distribution'),
      this.api.get('/api/platform/city-ranking'),
      this.api.get('/api/platform/stars-distribution'),
      this.api.get('/api/platform/monthly-trend')
    ]);
    this.overview = ov || {};
    this.typeDist = td;
    this.cityRank = cr;
    this.starsDist = sd;
    this.monthlyTrend = mt;
    this.$nextTick(() => this.initCharts());
  },
  methods: {
    initCharts() {
      if (this.typeDist) {
        new Chart(document.getElementById('pd1'), {
          type: 'doughnut',
          data: {
            labels: this.typeDist.labels || [],
            datasets: [{
              data: this.typeDist.data || [],
              backgroundColor: ['#FF6633','#FF9966','#1890FF','#52C41A','#FAAD14','#FF4D4F','#722ED1','#EB2F96','#13C2C2','#2F54EB','#D9D9D9']
            }]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { padding: 12, font: { size: 11 } } } } }
        });
      }
      if (this.cityRank) {
        new Chart(document.getElementById('pd2'), {
          type: 'bar',
          data: {
            labels: this.cityRank.labels || [],
            datasets: [{ label: '商户数', data: this.cityRank.data || [], backgroundColor: '#FF6633', borderRadius: 4 }]
          },
          options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false } } }
        });
      }
      if (this.starsDist) {
        new Chart(document.getElementById('pd3'), {
          type: 'pie',
          data: {
            labels: (this.starsDist.labels || []).map(l => parseFloat(l).toFixed(1) + '星'),
            datasets: [{
              data: this.starsDist.data || [],
              backgroundColor: ['#FFD666','#FFBB33','#FF9933','#FF8833','#FF6633','#E55520','#CC4422','#AA3322','#882222']
            }]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { padding: 12, font: { size: 11 } } } } }
        });
      }
      if (this.monthlyTrend) {
        new Chart(document.getElementById('pd4'), {
          type: 'line',
          data: {
            labels: this.monthlyTrend.labels || [],
            datasets: [
              { label: '新增商户', data: this.monthlyTrend.new_business || [], borderColor: '#FF6633', backgroundColor: 'rgba(255,102,51,0.1)', fill: true, tension: 0.4 },
              { label: '新增用户', data: this.monthlyTrend.new_users || [], borderColor: '#1890FF', backgroundColor: 'rgba(24,144,255,0.1)', fill: true, tension: 0.4 },
              { label: '新增评论', data: this.monthlyTrend.new_reviews || [], borderColor: '#52C41A', backgroundColor: 'rgba(82,196,26,0.1)', fill: true, tension: 0.4 }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });
      }
    }
  }
};