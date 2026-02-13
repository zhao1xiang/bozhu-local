import axios from 'axios';

// 支持环境变量配置 API 地址
// Tauri 桌面版使用 127.0.0.1:8000
// Web 版可以通过 VITE_API_URL 环境变量配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 增加到 30 秒，给后端更多启动时间
  headers: {
    'Content-Type': 'application/json',
  },
});

// 重试配置
const MAX_RETRIES = 5; // 增加到 5 次
const RETRY_DELAY = 3000; // 增加到 3 秒

// 延迟函数
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Request interceptor for retry logic
apiClient.interceptors.request.use(
  (config) => {
    // 添加重试计数
    config.headers['X-Retry-Count'] = config.headers['X-Retry-Count'] || '0';
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling and retry
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    // 如果是网络错误或超时，尝试重试
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message.includes('timeout')) {
      const retryCount = parseInt(config.headers['X-Retry-Count'] || '0');
      
      if (retryCount < MAX_RETRIES) {
        config.headers['X-Retry-Count'] = (retryCount + 1).toString();
        console.log(`后端连接失败，${RETRY_DELAY / 1000} 秒后重试 (${retryCount + 1}/${MAX_RETRIES})...`);
        
        // 等待后重试
        await delay(RETRY_DELAY);
        return apiClient(config);
      } else {
        console.error('后端连接失败，已达到最大重试次数');
        error.message = '无法连接到后端服务，请稍后重试或联系管理员';
      }
    }
    
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

