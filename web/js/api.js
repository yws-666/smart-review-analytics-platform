class TravelAPI {
  constructor(tokenRef) {
    this.tokenRef = tokenRef;
  }
  get headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.tokenRef && this.tokenRef.value) {
      h['Authorization'] = 'Bearer ' + this.tokenRef.value;
    }
    return h;
  }
  async get(url, params = {}) {
    try {
      const res = await axios.get(url, { params, headers: this.headers });
      return res.data;
    } catch (e) {
      return { error: e.response?.data?.error || '请求失败' };
    }
  }
  async post(url, data = {}) {
    try {
      const res = await axios.post(url, data, { headers: this.headers });
      return res.data;
    } catch (e) {
      return { error: e.response?.data?.error || '请求失败' };
    }
  }
  async put(url, data = {}) {
    try {
      const res = await axios.put(url, data, { headers: this.headers });
      return res.data;
    } catch (e) {
      return { error: e.response?.data?.error || '请求失败' };
    }
  }
  async del(url) {
    try {
      const res = await axios.delete(url, { headers: this.headers });
      return res.data;
    } catch (e) {
      return { error: e.response?.data?.error || '请求失败' };
    }
  }
  async delete(url) {
    return this.del(url);
  }
}