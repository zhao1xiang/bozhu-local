import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import Appointments from './pages/Appointments';
import DailyWork from './pages/DailyWork';
import PrintCenter from './pages/PrintCenter';
import SystemConfig from './pages/SystemConfig';
import Login from './pages/Login';
import Splash from './pages/Splash';
import DebugInfo from './pages/DebugInfo';
import { AuthProvider, useAuth } from './auth/AuthProvider';

const PrivateRoute = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

// 检测是否在 Tauri 环境中
const isTauri = () => {
  // 方法1: 检查 __TAURI__ API
  if (typeof window !== 'undefined' && window.__TAURI__) {
    return true;
  }
  
  // 方法2: 检查 URL 协议
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    
    // Tauri 使用 tauri:// 协议或 localhost
    if (protocol === 'tauri:' || hostname === 'tauri.localhost') {
      return true;
    }
  }
  
  // 方法3: 检查是否在文件系统中运行（file:// 协议通常不是 Tauri）
  // Tauri 应用不会使用 http://localhost:5173 (开发服务器)
  if (typeof window !== 'undefined') {
    const href = window.location.href;
    // 如果不是开发服务器，且不是 https://，很可能是 Tauri
    if (!href.startsWith('http://localhost:') && !href.startsWith('https://')) {
      return true;
    }
  }
  
  return false;
};

// 检测是否应该显示 Splash（通过环境变量或 Tauri 环境判断）
const shouldShowSplash = () => {
  // 如果设置了环境变量 VITE_SKIP_SPLASH，则跳过
  if (import.meta.env.VITE_SKIP_SPLASH === 'true') {
    return false;
  }
  
  // 否则只在 Tauri 环境中显示
  return isTauri();
};

// 根据环境决定首页
const HomePage = () => {
  // 根据配置决定是否显示 Splash
  if (shouldShowSplash()) {
    return <Splash />;
  } else {
    return <Navigate to="/login" replace />;
  }
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* 首页：EXE 显示 Splash，Web 跳转登录 */}
          <Route path="/" element={<HomePage />} />
          
          {/* 登录页面 */}
          <Route path="/login" element={<Login />} />
          
          {/* 调试信息页面 */}
          <Route path="/debug" element={<DebugInfo />} />

          {/* 受保护的路由 */}
          <Route element={<PrivateRoute />}>
            <Route path="/app" element={<MainLayout />}>
              <Route index element={<Navigate to="/app/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="patients" element={<Patients />} />
              <Route path="appointments" element={<Appointments />} />
              <Route path="daily-work" element={<DailyWork />} />
              <Route path="print-center" element={<PrintCenter />} />
              <Route path="system-config" element={<SystemConfig />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
