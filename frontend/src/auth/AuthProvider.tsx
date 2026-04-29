import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import { message } from 'antd';

interface AuthContextType {
    token: string | null;
    role: string;
    wards: string;
    username: string;
    login: (token: string, role?: string, wards?: string, username?: string, remember?: boolean) => void;
    logout: () => void;
    isAuthenticated: boolean;
    isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(() =>
        localStorage.getItem('token') || sessionStorage.getItem('token')
    );
    const [role, setRole] = useState<string>(() =>
        localStorage.getItem('role') || sessionStorage.getItem('role') || 'admin'
    );
    const [wards, setWards] = useState<string>(() =>
        localStorage.getItem('wards') || sessionStorage.getItem('wards') || ''
    );
    const [username, setUsername] = useState<string>(() =>
        localStorage.getItem('username') || sessionStorage.getItem('username') || ''
    );

    useEffect(() => {
        if (token) {
            const isRemembered = localStorage.getItem('token') === token;
            const storage = isRemembered ? localStorage : sessionStorage;
            storage.setItem('token', token);
            storage.setItem('role', role);
            storage.setItem('wards', wards);
            storage.setItem('username', username);

            const interceptor = apiClient.interceptors.request.use(config => {
                config.headers.Authorization = `Bearer ${token}`;
                return config;
            });
            const resInterceptor = apiClient.interceptors.response.use(
                response => response,
                error => {
                    if (error.response && error.response.status === 401) logout();
                    return Promise.reject(error);
                }
            );
            return () => {
                apiClient.interceptors.request.eject(interceptor);
                apiClient.interceptors.response.eject(resInterceptor);
            };
        } else {
            ['token', 'role', 'wards', 'username'].forEach(k => {
                localStorage.removeItem(k);
                sessionStorage.removeItem(k);
            });
        }
    }, [token]);

    const login = (newToken: string, newRole = 'admin', newWards = '', newUsername = '', remember = true) => {
        setToken(newToken);
        setRole(newRole);
        setWards(newWards);
        setUsername(newUsername);
        const storage = remember ? localStorage : sessionStorage;
        const other = remember ? sessionStorage : localStorage;
        storage.setItem('token', newToken);
        storage.setItem('role', newRole);
        storage.setItem('wards', newWards);
        storage.setItem('username', newUsername);
        ['token', 'role', 'wards', 'username'].forEach(k => other.removeItem(k));
    };

    const logout = () => {
        setToken(null);
        setRole('admin');
        setWards('');
        setUsername('');
        ['token', 'role', 'wards', 'username'].forEach(k => {
            localStorage.removeItem(k);
            sessionStorage.removeItem(k);
        });
        message.info('已退出登录');
    };

    return (
        <AuthContext.Provider value={{
            token, role, wards, username,
            login, logout,
            isAuthenticated: !!token,
            isAdmin: role === 'admin',
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within an AuthProvider');
    return context;
};
