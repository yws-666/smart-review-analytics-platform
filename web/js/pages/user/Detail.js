const UserDetail = {
  template: `
  <div>
    <div v-if="!business" class="loading">加载中...</div>
    <div v-else>
      <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
      <div class="detail-header">
        <div class="biz-title">{{ business.name }}</div>
        <div class="biz-subtitle">📍 {{ business.address }}, {{ business.city }}, {{ business.state }} {{ business.postal_code }}</div>
        <div class="biz-rating-big">
          <div class="big-score">{{ formatStars(business.stars) }}</div>
          <div style="line-height:1.8">
            <div class="rating-stars">{{ '★'.repeat(Math.round(business.stars)) }}{{ '☆'.repeat(5-Math.round(business.stars)) }} <span style="opacity:0.8;font-size:13px">{{ business.review_count }}条评价</span></div>
            <div style="font-size:13px;opacity:0.8">⭐ 质量 4.2 | 🏠 环境 3.8 | 👨‍💼 服务 4.0 | 💰 性价比 3.9</div>
          </div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px">
        <div>
          <div class="card">
            <div class="card-title">📝 用户评价 <span style="font-size:13px;color:#999">共{{ reviewTotal }}条</span></div>
            
            <div v-if="showReviewForm" class="review-form" style="padding:12px;border-bottom:1px solid var(--border);margin-bottom:8px">
              <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
                <span>评分：</span>
                <div class="star-rating">
                  <span v-for="i in 5" :key="i" :class="['star', newReviewStars >= i ? 'active' : '']" @click="newReviewStars = i">★</span>
                </div>
                <span style="font-weight:600">{{ newReviewStars }}星</span>
              </div>
              <textarea v-model="newReviewText" placeholder="写下您的评价..." rows="3" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:6px"></textarea>
              <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:8px">
                <button class="btn btn-sm" @click="showReviewForm=false">取消</button>
                <button class="btn btn-sm btn-primary" @click="submitReview">发表评价</button>
              </div>
            </div>
            
            <button v-if="username && !showReviewForm" class="btn btn-outline-primary" style="width:100%;margin-bottom:12px" @click="showReviewForm=true">✏️ 写评价</button>

            <div v-if="reviews && reviews.length">
              <div class="info-row" v-for="r in reviews" style="padding:14px;border-bottom:1px solid var(--border);flex-direction:column;align-items:flex-start">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span style="width:30px;height:30px;border-radius:50%;background:#FFE4CC;display:flex;align-items:center;justify-content:center;font-size:14px">👤</span>
                  <span style="font-weight:600;font-size:14px">{{ r.user_name || r.user_id }}</span>
                  <span style="font-size:12px;color:var(--text-lighter)">{{ r.year }}-{{ String(r.month).padStart(2,'0') }}-{{ String(r.day).padStart(2,'0') }}</span>
                  <button v-if="r.user_id === username" class="btn btn-sm" style="margin-left:auto;color:var(--danger)" @click="deleteReview(r.review_id)">🗑️ 删除</button>
                </div>
                <div class="rating-stars" style="font-size:13px;margin-bottom:4px">{{ '★'.repeat(r.stars) }}{{ '☆'.repeat(5-r.stars) }} {{ r.stars }}</div>
                <div style="font-size:14px;line-height:1.6;color:var(--text-light)">{{ r.text?.substring(0,300) }}</div>
                <div style="display:flex;gap:12px;margin-top:8px">
                  <button :class="['vote-btn', isVoted(r.review_id, 'useful') ? 'voted' : '']" @click="voteReview(r.review_id, 'useful')">👍 {{ r.useful || 0 }}</button>
                  <button :class="['vote-btn', isVoted(r.review_id, 'funny') ? 'voted' : '']" @click="voteReview(r.review_id, 'funny')">😂 {{ r.funny || 0 }}</button>
                  <button :class="['vote-btn', isVoted(r.review_id, 'cool') ? 'voted' : '']" @click="voteReview(r.review_id, 'cool')">😒 {{ r.cool || 0 }}</button>
                </div>
              </div>
              <div class="pagination">
                <button class="page-btn" :disabled="reviewPage<=1" @click="reviewPage--;loadReviews()">‹</button>
                <button class="page-btn active">{{ reviewPage }}</button>
                <button class="page-btn" :disabled="reviewPage*10>=reviewTotal" @click="reviewPage++;loadReviews()">›</button>
              </div>
            </div>
            <div class="loading" v-else>暂无评价</div>
          </div>
        </div>

        <div>
          <div class="card"><div class="card-title">📋 基本信息</div>
            <div class="info-row"><span class="info-label">城市</span>{{ business.city }}, {{ business.state }}</div>
            <div class="info-row"><span class="info-label">邮编</span>{{ business.postal_code }}</div>
            <div class="info-row"><span class="info-label">状态</span><span :style="{color:business.is_open?'var(--success)':'var(--danger)'}">{{ business.is_open ? '● 营业中' : '● 已关闭' }}</span></div>
            <div class="info-row"><span class="info-label">评分</span>{{ business.stars }} / 5.0</div>
            <div class="info-row"><span class="info-label">评论</span>{{ business.review_count }} 条</div>
            <div class="info-row"><span class="info-label">类别</span><span class="tag tag-orange">{{ business.business_type }}</span></div>
          </div>

          <div class="card"><div class="card-title">🏷️ 商户属性</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px">
              <span class="tag tag-orange" v-if="business.attrs?.accepts_credit_cards?.includes('True')">💳 信用卡</span>
              <span class="tag tag-blue" v-if="business.attrs?.take_out?.includes('True')">🥡 外卖</span>
              <span class="tag tag-green" v-if="business.attrs?.delivery?.includes('True')">🚗 配送</span>
              <span class="tag tag-orange" v-if="business.attrs?.good_for_kids?.includes('True')">👶 适合儿童</span>
              <span class="tag tag-blue" v-if="business.attrs?.outdoor_seating?.includes('True')">🪑 户外座位</span>
              <span class="tag tag-green" v-if="business.attrs?.reservations?.includes('True')">📞 接受预订</span>
              <span class="tag tag-gray">{{ business.attrs?.price_range ? '💰 ¥' + '¥'.repeat(parseInt(business.attrs.price_range)||1) : '' }}</span>
            </div>
          </div>

          <button class="btn btn-primary" style="width:100%;margin-top:8px" @click="addFavorite">❤️ 收藏商家</button>
        </div>
      </div>
    </div>
  </div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { 
    business:null, reviews:[], reviewPage:1, reviewTotal:0, currentBizId:'',
    showReviewForm: false,
    newReviewStars: 5,
    newReviewText: '',
    votedReviews: {}
  } },
  async mounted() {
    const self = this;
    EventBus.on('viewBusiness', async (id) => { 
      self.currentBizId = id; 
      await self.loadDetail(); 
      self.recordHistory();
    });
  },
  methods: {
    formatStars(stars) {
      return parseFloat(stars).toFixed(1);
    },
    async loadDetail() {
      const [bizRes, revRes] = await Promise.all([
        this.api.get('/api/businesses/' + this.currentBizId),
        this.api.get('/api/businesses/' + this.currentBizId + '/reviews?page=1&page_size=10')
      ]);
      this.business = bizRes;
      this.reviews = revRes.data || [];
      this.reviewTotal = revRes.total || 0;
    },
    async loadReviews() {
      const revRes = await this.api.get('/api/businesses/' + this.currentBizId + '/reviews?page=' + this.reviewPage + '&page_size=10');
      this.reviews = revRes.data || [];
    },
    async addFavorite() {
      if (!this.username) { alert('请先登录'); return; }
      if (!this.currentBizId) { alert('请先选择商家'); return; }
      const res = await this.api.post('/api/users/' + this.username + '/favorites', { business_id: this.currentBizId });
      if (res.error) {
        alert('收藏失败：' + res.error);
      } else {
        alert('收藏成功！');
      }
    },
    async recordHistory() {
      if (!this.username || !this.currentBizId) return;
      await this.api.post('/api/businesses/' + this.currentBizId + '/history', { user_id: this.username });
    },
    async submitReview() {
      if (!this.username) { alert('请先登录'); return; }
      if (!this.currentBizId) { alert('请先选择商家'); return; }
      if (!this.newReviewText.trim()) { alert('请输入评价内容'); return; }
      
      const res = await this.api.post('/api/businesses/' + this.currentBizId + '/reviews', { 
        stars: this.newReviewStars, 
        text: this.newReviewText 
      });
      if (res.error) {
        alert('评论失败：' + res.error);
      } else {
        alert('评论成功！');
        this.showReviewForm = false;
        this.newReviewStars = 5;
        this.newReviewText = '';
        this.reviewPage = 1;
        await this.loadReviews();
      }
    },
    isVoted(reviewId, voteType) {
      const key = reviewId + '_' + voteType;
      return this.votedReviews[key] === true;
    },
    async voteReview(reviewId, voteType) {
      if (!this.username) { alert('请先登录'); return; }
      const res = await this.api.post('/api/businesses/reviews/' + reviewId + '/vote', { type: voteType });
      if (res.error) {
        alert('投票失败：' + res.error);
      } else {
        const review = this.reviews.find(r => r.review_id === reviewId);
        if (review) {
          review[voteType] = res.count[voteType];
        }
        const key = reviewId + '_' + voteType;
        this.votedReviews[key] = res.voted;
      }
    },
    async deleteReview(reviewId) {
      if (!confirm('确定要删除这条评论吗？')) return;
      const res = await this.api.delete('/api/businesses/reviews/' + reviewId);
      if (res.error) {
        alert('删除失败：' + res.error);
      } else {
        alert('删除成功！');
        // 重新加载评论列表确保数据一致
        await this.loadReviews();
        // 更新总数
        this.reviewTotal = Math.max(0, (this.reviewTotal || 0) - 1);
      }
    }
  }
};