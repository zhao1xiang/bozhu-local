import React from 'react';
import { Card, Descriptions, Tag } from 'antd';

const DebugInfo: React.FC = () => {
  const isTauri = window.__TAURI__ !== undefined;
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const href = window.location.href;
  
  return (
    <div style={{ padding: 24 }}>
      <Card title="环境调试信息">
        <Descriptions bordered column={1}>
          <Descriptions.Item label="Tauri API">
            {isTauri ? (
              <Tag color="green">✓ 已加载</Tag>
            ) : (
              <Tag color="red">✗ 未加载</Tag>
            )}
          </Descriptions.Item>
          
          <Descriptions.Item label="协议 (Protocol)">
            <Tag color="blue">{protocol}</Tag>
          </Descriptions.Item>
          
          <Descriptions.Item label="主机名 (Hostname)">
            <Tag color="blue">{hostname}</Tag>
          </Descriptions.Item>
          
          <Descriptions.Item label="完整URL">
            <code>{href}</code>
          </Descriptions.Item>
          
          <Descriptions.Item label="环境变量 VITE_SKIP_SPLASH">
            <Tag color={import.meta.env.VITE_SKIP_SPLASH === 'true' ? 'orange' : 'default'}>
              {import.meta.env.VITE_SKIP_SPLASH || '未设置'}
            </Tag>
          </Descriptions.Item>
          
          <Descriptions.Item label="环境变量 VITE_API_URL">
            <code>{import.meta.env.VITE_API_URL || '未设置'}</code>
          </Descriptions.Item>
          
          <Descriptions.Item label="开发模式">
            {import.meta.env.DEV ? (
              <Tag color="orange">是</Tag>
            ) : (
              <Tag color="green">否 (生产)</Tag>
            )}
          </Descriptions.Item>
          
          <Descriptions.Item label="User Agent">
            <code style={{ fontSize: 11 }}>{navigator.userAgent}</code>
          </Descriptions.Item>
        </Descriptions>
        
        <div style={{ marginTop: 24, padding: 16, background: '#f5f5f5', borderRadius: 4 }}>
          <h4>判断逻辑:</h4>
          <ul>
            <li>如果 window.__TAURI__ 存在 → Tauri 环境</li>
            <li>如果 protocol 是 'tauri:' → Tauri 环境</li>
            <li>如果 hostname 是 'tauri.localhost' → Tauri 环境</li>
            <li>如果不是 http://localhost:* 且不是 https:// → 可能是 Tauri</li>
          </ul>
          
          <h4 style={{ marginTop: 16 }}>当前判断结果:</h4>
          <p>
            <strong>是否显示 Splash 页面: </strong>
            {isTauri && import.meta.env.VITE_SKIP_SPLASH !== 'true' ? (
              <Tag color="green">是</Tag>
            ) : (
              <Tag color="red">否</Tag>
            )}
          </p>
        </div>
      </Card>
    </div>
  );
};

export default DebugInfo;
