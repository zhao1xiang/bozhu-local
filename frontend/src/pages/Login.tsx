import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, message, Typography, Alert, Spin } from 'antd';
import { UserOutlined, LockOutlined, LoadingOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { apiClient } from '@/api/client';

const { Title } = Typography;

const Login: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [backendReady, setBackendReady] = useState(false);
    const [checkingBackend, setCheckingBackend] = useState(true);
    const navigate = useNavigate();
    const { login } = useAuth();

    // 检测是否在 Tauri 环境（EXE）或应该跳过检测
    const isTauri = () => {
        return window.__TAURI__ !== undefined;
    };

    const shouldCheckBackend = () => {
        // 如果设置了环境变量跳过检测
        if (import.meta.env.VITE_SKIP_SPLASH === 'true') {
            return false;
        }
        // 否则只在 Tauri 环境中检测
        return isTauri();
    };

    // 检查后端是否就绪（仅在需要时执行）
    useEffect(() => {
        const checkBackend = async () => {
            // 如果不需要检测，直接跳过
            if (!shouldCheckBackend()) {
                setBackendReady(true);
                setCheckingBackend(false);
                return;
            }

            // EXE 环境才检测后端
            let attempts = 0;
            const maxAttempts = 10;
            
            while (attempts < maxAttempts) {
                try {
                    await apiClient.get('/health', { timeout: 2000 });
                    setBackendReady(true);
                    setCheckingBackend(false);
                    return;
                } catch (error) {
                    attempts++;
                    if (attempts < maxAttempts) {
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                }
            }
            
            // 如果检查失败，仍然允许登录（可能后端已就绪但健康检查失败）
            setBackendReady(true);
            setCheckingBackend(false);
        };

        checkBackend();
    }, []);

    const onFinish = async (values: any) => {
        setLoading(true);
        try {
            // Use URLSearchParams for x-www-form-urlencoded
            const params = new URLSearchParams();
            params.append('username', values.username);
            params.append('password', values.password);

            const response = await apiClient.post('/auth/token', params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            login(response.data.access_token);
            message.success('登录成功');
            navigate('/app/dashboard');
        } catch (error: any) {
            console.error(error);
            let msg = '登录失败';
            
            if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
                msg = '无法连接到服务器，请稍后重试';
            } else if (error.response?.status === 401) {
                msg = '用户名或密码错误';
            } else if (error.response?.data?.detail) {
                msg = error.response.data.detail;
            } else if (error.message) {
                msg = error.message;
            }
            
            message.error(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            background: '#f0f2f5'
        }}>
            <Card style={{ width: 400, boxShadow: '0 4px 8px rgba(0,0,0,0.1)' }}>
                <div style={{ textAlign: 'center', marginBottom: 24 }}>
                    {/* Logo - 优先使用图片，如果加载失败则使用 emoji */}
                    <div style={{ 
                        display: 'flex', 
                        justifyContent: 'center', 
                        alignItems: 'center',
                        marginBottom: 8 
                    }}>
                        <img 
                            src="/logo.png" 
                            alt="Logo" 
                            style={{ 
                                width: 64, 
                                height: 64,
                                objectFit: 'contain',
                                display: 'block'
                            }}
                            onError={(e) => {
                                // 如果图片加载失败，隐藏图片并显示 emoji
                                e.currentTarget.style.display = 'none';
                                const emojiDiv = document.createElement('div');
                                emojiDiv.style.cssText = 'font-size: 48px; color: #1890ff; line-height: 1;';
                                emojiDiv.textContent = '👁️';
                                e.currentTarget.parentElement?.appendChild(emojiDiv);
                            }}
                        />
                    </div>
                    <Title level={3} style={{ margin: 0 }}>玻注预约系统</Title>
                </div>
                
                {checkingBackend && (
                    <Alert
                        message="系统启动中"
                        description={
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <Spin indicator={<LoadingOutlined spin />} size="small" />
                                <span>正在启动后端服务，请稍候...</span>
                            </div>
                        }
                        type="info"
                        showIcon
                        style={{ marginBottom: 16 }}
                    />
                )}
                
                <Form
                    name="login"
                    initialValues={{ remember: true }}
                    onFinish={onFinish}
                    size="large"
                    disabled={checkingBackend}
                >
                    <Form.Item
                        name="username"
                        rules={[{ required: true, message: '请输入用户名' }]}
                    >
                        <Input prefix={<UserOutlined />} placeholder="用户名" />
                    </Form.Item>

                    <Form.Item
                        name="password"
                        rules={[{ required: true, message: '请输入密码' }]}
                    >
                        <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                    </Form.Item>

                    <Form.Item>
                        <Button 
                            type="primary" 
                            htmlType="submit" 
                            style={{ width: '100%' }} 
                            loading={loading}
                            disabled={checkingBackend}
                        >
                            {checkingBackend ? '系统启动中...' : '登录'}
                        </Button>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
};

export default Login;
