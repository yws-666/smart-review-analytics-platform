const UserPreferences = {
  template: `
  <div>
    <button v-if="canGoBack" class="back-btn" @click="goBack">← 返回</button>
    <div class="card">
    <div class="card-title">⚙️ 偏好设置</div>
    <h4 style="margin:12px 0;font-size:14px">感兴趣的类别</h4>
    <div class="pref-grid" style="margin-bottom:16px">
      <div v-for="c in allCategories" :class="['pref-item', selCategories.includes(c) ? 'selected' : '']" @click="toggle(selCategories,c)">{{ c }}</div>
    </div>
    <h4 style="margin:12px 0;font-size:14px">价格区间</h4>
    <div class="pref-grid" style="margin-bottom:16px">
      <div v-for="p in prices" :class="['pref-item', selPrices.includes(p.val) ? 'selected' : '']" @click="toggle(selPrices,p.val)">{{ p.label }}</div>
    </div>
    <h4 style="margin:12px 0;font-size:14px">评分偏好</h4>
    <div class="pref-grid" style="margin-bottom:16px">
      <div v-for="s in starOptions" :class="['pref-item', minStars === s.val ? 'selected' : '']" @click="minStars=s.val">{{ s.label }}</div>
    </div>
    <button class="btn btn-primary" @click="save">保存偏好</button>
  </div>`,
  props: ['token', 'api', 'username', 'goBack', 'canGoBack'],
  data() { return { allCategories:['美食餐饮','购物零售','酒店旅游','休闲娱乐','生活服务','美容美发','医疗健康','汽车服务','宠物服务','教育培训'], selCategories:[], selPrices:[], prices:[{val:'1',label:'¥ 便宜'},{val:'2',label:'¥¥ 中档'},{val:'3',label:'¥¥¥ 高档'},{val:'4',label:'¥¥¥¥ 奢华'}], starOptions:[{val:3,label:'3星以上'},{val:4,label:'4星以上'},{val:4.5,label:'4.5星以上'}], minStars:4 } },
  async mounted() {
    if (!this.username) return;
    const res = await this.api.get('/api/users/' + this.username + '/preferences');
    if (res && !res.error) {
      this.selCategories = res.categories || [];
      this.selPrices = res.price_range || [];
      this.minStars = res.min_stars || 4;
    }
  },
  methods: {
    toggle(arr, val) { const i = arr.indexOf(val); if (i>=0) arr.splice(i,1); else arr.push(val); },
    async save() {
      await this.api.put('/api/users/' + this.username + '/preferences', { categories: this.selCategories, price_range: this.selPrices, min_stars: this.minStars });
      alert('偏好设置已保存');
    }
  }
};