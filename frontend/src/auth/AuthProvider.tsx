import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import { message } from 'antd';

interface AuthContextType {
    token: string | null;
    login: (token: string, remember?: boolean) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(() => {
        // 优先从 localStorage 获取，如果没有则从 sessionStorage 获取
        return localStorage.getItem('token') || sessionStorage.getItem('token');
    });

    useEffect(() => {
        if (token) {
            // 检查 token 是否存储在 localStorage 中（记住登录状态）
            const isRemembered = localStorage.getItem('token') === token;
            
            if (isRemembered) {
                localStorage.setItem('token', token);
            } else {
                sessionStorage.setItem('token', token);
            }
            
            // Configure axios interceptor
            const interceptor = apiClient.interceptors.request.use(config => {
                config.headers.Authorization = `Bearer ${token}`;
                return config;
            });

            // Response interceptor to handle 401
            const resInterceptor = apiClient.interceptors.response.use(
                response => response,
                error => {
                    if (error.response && error.response.status === 401) {
                        logout();
                    }
                    return Promise.reject(error);
                }
            );

            return () => {
                apiClient.interceptors.request.eject(interceptor);
                apiClient.interceptors.response.eject(resInterceptor);
            };
        } else {
            localStorage.removeItem('token');
            sessionStorage.removeItem('token');
        }
    }, [token]);

    const login = (newToken: string, remember: boolean = true) => {
        setToken(newToken);
        
        if (remember) {
            // 记住登录状态，存储到 localStorage
            localStorage.setItem('token', newToken);
            sessionStorage.removeItem('token');
        } else {
            // 不记住登录状态，存储到 sessionStorage
            sessionStorage.setItem('token', newToken);
            localStorage.removeItem('token');
        }
    };

    const logout = () => {
        setToken(null);
        localStorage.removeItem('token');
        sessionStorage.removeItem('token');
        message.info('已退出登录');
    };

    return (
        <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
