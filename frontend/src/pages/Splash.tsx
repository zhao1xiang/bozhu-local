import React, { useEffect, useState } from 'react';
import { Spin, Progress, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api/client';

const { Title, Text } = Typography;

const Splash: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('正在启动系统...');
  const navigate = useNavigate();

  useEffect(() => {
    const checkBackend = async () => {
      let attempts = 0;
      const maxAttempts = 15; // 最多等待 15 秒
      
      // 模拟进度条
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) return prev;
          return prev + 5;
        });
      }, 500);

      while (attempts < maxAttempts) {
        try {
          setStatus(`正在启动后端服务... (${attempts + 1}/${maxAttempts})`);
          
          await apiClient.get('/health', { timeout: 2000 });
          
          // 后端就绪
          clearInterval(progressInterval);
          setProgress(100);
          setStatus('系统启动完成！');
          
          // 等待一下让用户看到完成状态
          await new Promise(resolve => setTimeout(resolve, 500));
          
          // 跳转到登录页
          navigate('/login', { replace: true });
          return;
        } catch (error) {
          attempts++;
          if (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      }
      
      // 超时后仍然跳转，让用户尝试登录
      clearInterval(progressInterval);
      setProgress(100);
      setStatus('系统启动完成');
      await new Promise(resolve => setTimeout(resolve, 500));
      navigate('/login', { replace: true });
    };

    checkBackend();
  }, [navigate]);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        gap: 24, 
        width: 400 
      }}>
        {/* Logo */}
        <div
          style={{
            fontSize: 80,
            marginBottom: 20,
            animation: 'pulse 2s ease-in-out infinite',
          }}
        >
          👁️
        </div>

        {/* 标题 */}
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          眼科注射预约系统
        </Title>

        {/* 加载动画 */}
        <Spin
          indicator={<LoadingOutlined style={{ fontSize: 48, color: 'white' }} spin />}
        />

        {/* 进度条 */}
        <div style={{ width: '100%' }}>
          <Progress
            percent={progress}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
            showInfo={false}
          />
        </div>

        {/* 状态文本 */}
        <Text style={{ color: 'rgba(255, 255, 255, 0.85)', fontSize: 16 }}>
          {status}
        </Text>

        {/* 版本号 */}
        <Text style={{ color: 'rgba(255, 255, 255, 0.65)', fontSize: 12, marginTop: 20 }}>
          v2.1.1
        </Text>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.1);
            opacity: 0.8;
          }
        }
      `}</style>
    </div>
  );
};

export default Splash;
