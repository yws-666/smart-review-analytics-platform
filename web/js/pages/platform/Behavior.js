const PlatformBehavior = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <h3 style="margin-bottom:16px">📱 用户行为分析</h3>

    <div class="chart-row">
      <div class="card">
        <div class="card-title">📊 用户活跃度分布</div>
        <div class="chart-container"><canvas id="pb1"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">💰 消费习惯 (价格区间 × 类别)</div>
        <div class="chart-container"><canvas id="pb2"></canvas></div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">👥 用户活跃度分析详情</div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
        <div class="card" style="text-align:center" v-for="(label, i) in (activity.labels || [])" :key="i">
          <div style="font-size:32px;margin-bottom:8px">{{ ['🔥','⭐','💤','❌'][i] }}</div>
          <div style="font-size:24px;font-weight:700;color:var(--primary)">{{ (activity.data || [])[i] }}%</div>
          <div style="font-size:13px;color:var(--text-light);margin-top:4px">{{ label }}</div>
          <div class="progress-bar" style="width:100%;margin-top:8px">
            <div class="fill" style="background:var(--primary)" :style="{width:(activity.data||[])[i]+'%'}"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">💡 消费行为洞察</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;font-size:14px">
        <div class="card" style="text-align:center;padding:20px;background:#FFF5F0">
          <div style="font-size:28px">🍽️</div>
          <div style="font-weight:600;margin:8px 0">美食偏好</div>
          <div style="font-size:12px;color:var(--text-light)">中档消费(¥¥) 最受欢迎<br>占消费记录 40%</div>
        </div>
        <div class="card" style="text-align:center;padding:20px;background:#E6F7FF">
          <div style="font-size:28px">🏨</div>
          <div style="font-weight:600;margin:8px 0">酒店偏好</div>
          <div style="font-size:12px;color:var(--text-light)">高端消费(¥¥¥¥) 为主<br>占消费记录 35%</div>
        </div>
        <div class="card" style="text-align:center;padding:20px;background:#F6FFED">
          <div style="font-size:28px">🛒</div>
          <div style="font-weight:600;margin:8px 0">购物偏好</div>
          <div style="font-size:12px;color:var(--text-light)">中高档(¥¥¥) 均衡<br>占消费记录 35%</div>
        </div>
      </div>
    </div>
  </div>`,
  props: ['token', 'api', 'goBack', 'canGoBack'],
  data() { return { activity: { labels:[], data:[] }, habits: null } },
  async mounted() {
    if (!this.token) return;
    const [actRes, habRes] = await Promise.all([
      this.api.get('/api/platform/user-activity'),
      this.api.get('/api/platform/consumption-habits')
    ]);
    this.activity = actRes || this.activity;
    this.habits = habRes || {};
    this.$nextTick(() => this.initCharts());
  },
  methods: {
    initCharts() {
      const labels = this.activity.labels || ['高活跃(>100评论)','中活跃(10-100)','低活跃(<10)','不活跃(0)'];
      const data = (this.activity.data || [15,35,40,10]).map(Number);
      new Chart(document.getElementById('pb1'), {
        type: 'doughnut',
        data: { labels, datasets: [{ data, backgroundColor: ['#52C41A','#1890FF','#FAAD14','#D9D9D9'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
      });

      if (this.habits) {
        const colorMap = { '¥':'#52C41A', '¥¥':'#1890FF', '¥¥¥':'#FAAD14', '¥¥¥¥':'#FF6633' };
        const priceLabels = { '¥':'低档消费', '¥¥':'中档消费', '¥¥¥':'中高档消费', '¥¥¥¥':'高档消费' };
        const datasets = (this.habits.datasets || []).map(ds => ({
          label: priceLabels[ds.label] || ds.label, data: ds.data || [], backgroundColor: colorMap[ds.label] || '#999', borderRadius: 2
        }));
        new Chart(document.getElementById('pb2'), {
          type: 'bar',
          data: { labels: this.habits.labels || [], datasets },
          options: {
            responsive: true, maintainAspectRatio: false,
            scales: { x: { stacked: true }, y: { stacked: true, title: { display: true, text: '占比 (%)' } } },
            plugins: { legend: { position: 'bottom' } }
          }
        });
      }
    }
  }
};