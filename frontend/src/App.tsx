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
import { AuthProvider, useAuth } from './auth/AuthProvider';

const PrivateRoute = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* 启动加载页面 */}
          <Route path="/" element={<Splash />} />
          
          {/* 登录页面 */}
          <Route path="/login" element={<Login />} />

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
