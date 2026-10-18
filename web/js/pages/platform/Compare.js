const PlatformCompare = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <h3 style="margin-bottom:16px">📊 多维度对比分析</h3>

    <div class="chart-row">
      <div class="card">
        <div class="card-title">🏙️ 城市商户数 & 均分对比</div>
        <div class="chart-container"><canvas id="pc1"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">📂 类别商户数 & 均分对比</div>
        <div class="chart-container" style="height:350px"><canvas id="pc2"></canvas></div>
      </div>
    </div>

    <div class="card" v-if="cityComparison">
      <div class="card-title">🏙️ 城市详细对比表</div>
      <table class="data-table">
        <thead>
          <tr><th>城市</th><th>商户数</th><th>平均评分</th><th>占比</th></tr>
        </thead>
        <tbody>
          <tr v-for="(label, i) in cityComparison.labels || []" :key="i">
            <td><strong>{{ label }}</strong></td>
            <td>{{ (cityComparison.business_count || [])[i]?.toLocaleString() }}</td>
            <td><span class="tag tag-orange">⭐ {{ (cityComparison.avg_stars || [])[i] }}</span></td>
            <td>
              {{ ((cityComparison.business_count || [])[i] / (cityComparison.business_count || []).reduce((a,b) => a+b, 1) * 100).toFixed(1) }}%
              <div class="progress-bar" style="width:100%">
                <div class="fill" style="background:var(--primary)" :style="{width: ((cityComparison.business_count||[])[i]/(cityComparison.business_count||[]).reduce((a,b)=>a+b,1)*100)+'%'}"></div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card" v-if="typeComparison">
      <div class="card-title">📂 类别详细对比表</div>
      <table class="data-table">
        <thead>
          <tr><th>类别</th><th>商户数</th><th>平均评分</th><th>平均评论数</th></tr>
        </thead>
        <tbody>
          <tr v-for="(label, i) in typeComparison.labels || []" :key="i">
            <td><strong>{{ label }}</strong></td>
            <td>{{ (typeComparison.count || [])[i]?.toLocaleString() }}</td>
            <td><span class="tag tag-orange">⭐ {{ (typeComparison.avg_stars || [])[i] }}</span></td>
            <td>{{ parseFloat((typeComparison.avg_reviews || [])[i] || 0).toFixed(1) }} 条</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>`,
  props: ['token', 'api', 'goBack', 'canGoBack'],
  data() { return { cityComparison: null, typeComparison: null } },
  async mounted() {
    if (!this.token) return;
    const [cityRes, typeRes] = await Promise.all([
      this.api.get('/api/platform/city-comparison'),
      this.api.get('/api/platform/type-comparison')
    ]);
    this.cityComparison = cityRes;
    this.typeComparison = typeRes;
    this.$nextTick(() => this.initCharts());
  },
  methods: {
    initCharts() {
      if (this.cityComparison) {
        new Chart(document.getElementById('pc1'), {
          type: 'bar',
          data: {
            labels: this.cityComparison.labels || [],
            datasets: [
              { label: '商户数', data: this.cityComparison.business_count || [], backgroundColor: '#FF9966', borderRadius: 4, yAxisID: 'y' },
              { label: '平均评分', data: (this.cityComparison.avg_stars || []).map(v => v * 10000), backgroundColor: 'rgba(24,144,255,0.6)', borderRadius: 4, yAxisID: 'y1' }
            ]
          },
          options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
              y: { type: 'linear', position: 'left', title: { display: true, text: '商户数' } },
              y1: { type: 'linear', position: 'right', title: { display: true, text: '评分(×10000)' }, grid: { drawOnChartArea: false } }
            },
            plugins: { legend: { position: 'bottom' } }
          }
        });
      }
      if (this.typeComparison) {
        new Chart(document.getElementById('pc2'), {
          type: 'bar',
          data: {
            labels: this.typeComparison.labels || [],
            datasets: [
              { label: '商户数', data: this.typeComparison.count || [], backgroundColor: '#1890FF', borderRadius: 4 },
              { label: '平均评分(×100)', data: (this.typeComparison.avg_stars || []).map(v => v * 100), backgroundColor: 'rgba(255,102,51,0.7)', borderRadius: 4 }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });
      }
    }
  }
};