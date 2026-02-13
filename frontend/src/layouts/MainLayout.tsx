import React, { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import {
  UserOutlined,
  CalendarOutlined,
  DashboardOutlined,
  PrinterOutlined,
  SettingOutlined,
  CheckSquareOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { APP_VERSION } from '../config/version';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();

  const items = [
    {
      key: '/app/dashboard',
      icon: <DashboardOutlined />,
      label: '工作台',
    },
    {
      key: '/app/daily-work',
      icon: <CheckSquareOutlined />,
      label: '每日工作',
    },
    {
      key: '/app/patients',
      icon: <UserOutlined />,
      label: '患者管理',
    },
    {
      key: '/app/appointments',
      icon: <CalendarOutlined />,
      label: '预约管理',
    },
    {
      key: '/app/print-center',
      icon: <PrinterOutlined />,
      label: '打印中心',
    },
    {
      key: '/app/system-config',
      icon: <SettingOutlined />,
      label: '系统配置',
    },
    {
      key: 'logout',
      icon: <UserOutlined />,
      label: '退出登录',
      danger: true,
    }
  ];

  const handleMenuClick = (e: any) => {
    if (e.key === 'logout') {
      logout();
      navigate('/login');
    } else {
      navigate(e.key);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div className="demo-logo-vertical" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', overflow: 'hidden', whiteSpace: 'nowrap' }}>
          {collapsed ? '玻' : '玻注预约系统'}
        </div>
        <Menu
          theme="dark"
          defaultSelectedKeys={[location.pathname]}
          selectedKeys={[location.pathname]}
          mode="inline"
          items={items}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          padding: '0 24px', 
          background: colorBgContainer,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <div style={{ 
            fontSize: '18px', 
            fontWeight: 'bold',
            color: '#1890ff'
          }}>
            眼科注射预约系统
          </div>
        </Header>
        <Content style={{ margin: '16px 16px' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
              height: '100%',
              overflow: 'auto'
            }}
          >
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
