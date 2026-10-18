const MerchantDashboard = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <h3 style="margin-bottom:16px">数据概览仪表盘</h3>
    <div class="stat-cards">
      <div class="stat-card"><div class="stat-icon" style="background:#FEF3C7;color:var(--primary)">⭐</div><div class="stat-value">{{ data.stars }}</div><div class="stat-label">总体评分</div><div class="stat-change up">↑ 0.2 较上月</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#DBEAFE;color:var(--info)">💬</div><div class="stat-value">{{ data.review_count }}</div><div class="stat-label">评论总数</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#D1FAE5;color:var(--success)">👍</div><div class="stat-value">{{ data.total_useful }}</div><div class="stat-label">有用票总数</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#FEF3C7;color:var(--warning)">👥</div><div class="stat-value">{{ data.visit_count }}</div><div class="stat-label">预估浏览量</div></div>
    </div>
    <div class="chart-row">
      <div class="card"><div class="card-title">月度评论数趋势</div><div class="chart-container"><canvas id="mc1"></canvas></div></div>
      <div class="card"><div class="card-title">评分分布</div><div class="chart-container"><canvas id="mc2"></canvas></div></div>
    </div>
  </div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { data: { stars:0, review_count:0, total_useful:0, visit_count:0 } } },
  async mounted() {
    const bizId = this.username || '';
    if (!this.token) { return; }
    const [dashRes, trendRes, distRes] = await Promise.all([
      this.api.get('/api/merchant/dashboard?business_id=' + bizId),
      this.api.get('/api/merchant/review-trend?business_id=' + bizId),
      this.api.get('/api/merchant/rating-distribution?business_id=' + bizId)
    ]);
    this.data = dashRes || this.data;
    this.$nextTick(() => {
      new Chart(document.getElementById('mc1'), {
        type:'line', data:{labels:(trendRes||[]).slice(-12).map(r=>r.year+'-'+r.month), datasets:[{label:'评论数',data:(trendRes||[]).slice(-12).map(r=>r.count),borderColor:'#FF6633',backgroundColor:'rgba(255,102,51,0.1)',fill:true,tension:0.4}]},
        options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}
      });
      const distData = distRes || [];
      new Chart(document.getElementById('mc2'), {
        type:'bar', data:{labels:['1星','2星','3星','4星','5星'], datasets:[{data:[distData.find(d=>d.stars==1)?.count||0,distData.find(d=>d.stars==2)?.count||0,distData.find(d=>d.stars==3)?.count||0,distData.find(d=>d.stars==4)?.count||0,distData.find(d=>d.stars==5)?.count||0],backgroundColor:['#FF4D4F','#FAAD14','#FFD666','#FF9966','#52C41A']}]},
        options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}
      });
    });
  }
};