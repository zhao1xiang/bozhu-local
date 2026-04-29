content = '''import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || (() => {
  const hostname = window.location.hostname;
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
  const isProduction = import.meta.env.MODE === 'production';
  
  if (isLocalhost) {
    return 'http://127.0.0.1:38126/api';
  }
  
  if (isProduction) {
    if (hostname.match(/^(192\\.168|10\\.|172\\.(1[6-9]|2[0-9]|3[01]))\\./)) {
      return `http://${hostname}:38126/api`;
    }
    return '/api';
  }
  
  return '/api';
})();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const MAX_RETRIES = 5;
const RETRY_DELAY = 3000;
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

apiClient.interceptors.request.use(
  (config) => {
    config.headers['X-Retry-Count'] = config.headers['X-Retry-Count'] || '0';
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message.includes('timeout')) {
      const retryCount = parseInt(config.headers['X-Retry-Count'] || '0');
      if (retryCount < MAX_RETRIES) {
        config.headers['X-Retry-Count'] = (retryCount + 1).toString();
        await delay(RETRY_DELAY);
        return apiClient(config);
      } else {
        error.message = 'Cannot connect to backend service';
      }
    }
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
'''

with open('frontend/src/api/client.ts', 'w', encoding='utf-8') as f:
    f.write(content)
print('done')
