import React from 'react';
import { CheckCircleFilled } from '@ant-design/icons';

const colors = {
  blue: '#1677f7',
  blueBg: '#f0f5ff',
  blueBorder: '#adcf6',
};

const EmbedSuccess: React.FC = () => {
  return (
    <div style={{
      background: colors.blueBg,
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 16,
    }}>
      <div style={{
        background: '#fff',
        borderRadius: 16,
        padding: '48px 40px',
        boxShadow: '0 2px 12px rgba(0,0,0,0.10)',
        border: `1px solid ${colors.blueBorder}`,
        textAlign: 'center',
        maxWidth: 400,
        width: '100%',
      }}>
        <CheckCircleFilled style={{ fontSize: 64, color: '#52c41a', marginBottom: 20 }} />
        <div style={{ fontSize: 22, fontWeight: 'bold', color: '#1d2939', marginBottom: 10 }}>
          预约成功
        </div>
        <div style={{ fontSize: 15, color: '#6b7280', lineHeight: 1.8 }}>
          您的玻注预约已成功提交<br />
        </div>
      </div>
    </div>
  );
};

export default EmbedSuccess;
