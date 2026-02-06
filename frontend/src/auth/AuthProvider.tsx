import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import { message } from 'antd';

interface AuthContextType {
    token: string | null;
    login: (token: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token);
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
        }
    }, [token]);

    const login = (newToken: string) => {
        setToken(newToken);
    };

    const logout = () => {
        setToken(null);
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
