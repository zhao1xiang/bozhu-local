import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Select, Button, message, Space, Descriptions, Empty } from 'antd';
import { PrinterOutlined, ReloadOutlined } from '@ant-design/icons';
import { Patient, Appointment } from '@/types';
import { apiClient } from '@/api/client';
import dayjs from 'dayjs';

const PrintCenter: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);

  // 安全地查找选中的患者，防止 null 错误
  const selectedPatient = patients?.find(p => p.id === selectedPatientId);

  const fetchPatients = async () => {
    try {
      const response = await apiClient.get<Patient[]>('/patients');
      // 确保返回的是数组
      setPatients(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error(error);
      message.error('获取患者列表失败');
      setPatients([]); // 出错时设置为空数组
    }
  };

  const fetchAppointments = async (patientId: string) => {
    setLoading(true);
    try {
      const response = await apiClient.get<Appointment[]>('/appointments', {
        params: { patient_id: patientId, limit: 100 }
      });
      // 确保返回的是数组
      const data = Array.isArray(response.data) ? response.data : [];
      // Sort by injection_count
      const sorted = data
        .filter(a => a.patient_id === patientId)
        .sort((a, b) => (a.injection_count || 0) - (b.injection_count || 0));
      setAppointments(sorted);
    } catch (error) {
      console.error(error);
      message.error('获取预约列表失败');
      setAppointments([]); // 出错时设置为空数组
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  useEffect(() => {
    const patientIdParam = searchParams.get('patient_id');
    if (patientIdParam) {
      setSelectedPatientId(patientIdParam);
    }
  }, [searchParams]);

  useEffect(() => {
    if (selectedPatientId) {
      fetchAppointments(selectedPatientId);
    } else {
      setAppointments([]);
    }
  }, [selectedPatientId]);

  const getAppointmentByCount = (count: number) => {
    return appointments.find(a => a.injection_count === count);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    return dayjs(dateStr).format('M月D日');
  };

  const handlePrint = () => {
    const printArea = document.getElementById('print-area');
    if (!printArea) {
      message.error('打印区域未找到，请刷新页面重试');
      return;
    }

    try {
      message.info('正在准备打印...');
      
      // 添加打印样式 - 保持字体大小一致
      const style = document.createElement('style');
      style.id = 'print-style';
      style.textContent = `
        @media print {
          @page {
            size: A4 portrait;
            margin: 8mm;
          }
          
          * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          
          html, body {
            width: 210mm;
            height: 297mm;
            margin: 0;
            padding: 0;
            overflow: hidden;
          }
          
          body * {
            visibility: hidden;
          }
          
          #print-area, #print-area * {
            visibility: visible;
          }
          
          #print-area {
            position: fixed;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            page-break-inside: avoid;
            page-break-after: avoid;
          }
          
          .print-container {
            width: 194mm !important;
            max-width: 194mm !important;
            height: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
            background: white !important;
            page-break-inside: avoid;
            page-break-after: avoid;
            position: relative;
          }
          
          .print-container img {
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important;
            display: block;
            page-break-inside: avoid;
          }
          
          .overlay-text {
            position: absolute;
            font-family: "SimSun", "Songti SC", serif;
            font-weight: bold;
          }
          
          /* 调整字体大小以匹配打印缩放比例 */
          /* 原始容器宽度 420px，打印宽度 194mm ≈ 733px */
          /* 缩放比例：733 / 420 ≈ 1.745 */
          .overlay-text.name {
            font-size: 22.7px !important; /* 13px * 1.745 */
          }
          
          .overlay-text.phone {
            font-size: 22.7px !important; /* 13px * 1.745 */
          }
          
          .overlay-text.checkmark {
            font-size: 24.4px !important; /* 14px * 1.745 */
          }
          
          .overlay-text.diagnosis {
            font-size: 20.9px !important; /* 12px * 1.745 */
          }
          
          .overlay-text.drug {
            font-size: 20.9px !important; /* 12px * 1.745 */
          }
          
          .overlay-text.vision {
            font-size: 19.2px !important; /* 11px * 1.745 */
          }
          
          .overlay-text.time-1,
          .overlay-text.time-2,
          .overlay-text.time-3,
          .overlay-text.time-4,
          .overlay-text.time-5,
          .overlay-text.time-6,
          .overlay-text.time-7,
          .overlay-text.time-8,
          .overlay-text.time-9 {
            font-size: 20.9px !important; /* 12px * 1.745 */
          }
        }
      `;
      document.head.appendChild(style);
      
      // 执行打印
      window.print();
      
      // 打印完成后移除样式
      setTimeout(() => {
        const styleEl = document.getElementById('print-style');
        if (styleEl) {
          styleEl.remove();
        }
      }, 1000);
    } catch (error) {
      console.error('打印过程中发生错误:', error);
      message.error('打印失败: ' + (error as Error).message);
    }
  }

  return (
    <div>
      <Card
        title="打印中心 - 玻注复诊注射卡"
        extra={
          <Space>
            <Select
              showSearch
              style={{ width: 280 }}
              placeholder="请选择患者"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              onChange={(value) => setSelectedPatientId(value)}
              options={patients.map(p => ({
                label: `${p.name}${p.phone ? ` (${p.phone})` : ''}`,
                value: p.id
              }))}
              allowClear
            />
            <Button
              type="primary"
              icon={<PrinterOutlined />}
              onClick={handlePrint}
              disabled={!selectedPatient}
            >
              打印
            </Button>
          </Space>
        }
      >
        {selectedPatient ? (
          <>
            <Descriptions bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="姓名">{selectedPatient.name}</Descriptions.Item>
              <Descriptions.Item label="电话">{selectedPatient.phone || '-'}</Descriptions.Item>
              <Descriptions.Item label="诊断">{selectedPatient.diagnosis || '-'}</Descriptions.Item>
              <Descriptions.Item label="药物">{selectedPatient.drug_type || '-'}</Descriptions.Item>
              <Descriptions.Item label="治疗眼">
                {selectedPatient.left_eye ? '左眼 ' : ''}{selectedPatient.right_eye ? '右眼' : ''}
              </Descriptions.Item>
              <Descriptions.Item label="预约数">{appointments.length} 次</Descriptions.Item>
            </Descriptions>

            {/* Print Preview Area */}
            <div
              id="print-area"
              style={{
                display: 'flex',
                justifyContent: 'center',
                background: '#f0f0f0',
                padding: 20,
                borderRadius: 8,
                minHeight: 600
              }}
            >
              <div
                className="print-container"
                style={{
                  position: 'relative',
                  width: '420px',
                  maxWidth: '420px',
                  background: '#fff',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                  overflow: 'hidden'
                }}
              >
                <img 
                  src="/print-template.png" 
                  alt="打印模板" 
                  style={{ 
                    width: '100%',
                    display: 'block',
                    height: 'auto'
                  }}
                  onError={(e) => {
                    console.error('打印模板图片加载失败');
                    e.currentTarget.style.display = 'none';
                    const parent = e.currentTarget.parentElement;
                    if (parent) {
                      const errorDiv = document.createElement('div');
                      errorDiv.style.cssText = 'padding: 40px; text-align: center; color: #999;';
                      errorDiv.innerHTML = '⚠️ 打印模板图片加载失败<br/>请检查 print-template.png 文件是否存在';
                      parent.appendChild(errorDiv);
                    }
                  }}
                />

                {/* Patient Info Overlay - Row 1: 姓名、联系方式、左眼右眼 */}
                <span className="overlay-text name" style={{ position: 'absolute', top: '20%', left: '16%', fontSize: '13px', fontWeight: 'bold' }}>
                  {selectedPatient.name}
                </span>
                <span className="overlay-text phone" style={{ position: 'absolute', top: '20%', left: '53%', fontSize: '13px', fontWeight: 'bold' }}>
                  {selectedPatient.phone || ''}
                </span>
                {selectedPatient.left_eye && (
                  <span className="overlay-text checkmark" style={{ position: 'absolute', top: '20%', left: '73%', fontSize: '14px', fontWeight: 'bold' }}>
                    ✓
                  </span>
                )}
                {selectedPatient.right_eye && (
                  <span className="overlay-text checkmark" style={{ position: 'absolute', top: '20%', left: '86%', fontSize: '14px', fontWeight: 'bold' }}>
                    ✓
                  </span>
                )}

                {/* Patient Info Overlay - Row 2: 诊断、治疗药物、眼视力 */}
                <span className="overlay-text diagnosis" style={{ position: 'absolute', top: '24%', left: '16%', fontSize: '12px', fontWeight: 'bold' }}>
                  {selectedPatient.diagnosis || ''}
                </span>
                <span className="overlay-text drug" style={{ position: 'absolute', top: '24%', left: '51%', fontSize: '12px', fontWeight: 'bold' }}>
                  {selectedPatient.drug_type || ''}
                </span>
                <span className="overlay-text vision" style={{ position: 'absolute', top: '24%', left: '79%', fontSize: '11px', fontWeight: 'bold' }}>
                  {selectedPatient.left_vision || selectedPatient.right_vision
                    ? `左${selectedPatient.left_vision || '-'} 右${selectedPatient.right_vision || '-'}`
                    : ''}
                </span>

                {/* Initial Phase - 第1-4次治疗时间 (治疗时间行) */}
                <span className="overlay-text time-1" style={{ position: 'absolute', top: '38.8%', left: '28%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(1)?.appointment_date)}
                </span>
                <span className="overlay-text time-2" style={{ position: 'absolute', top: '38.8%', left: '46%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(2)?.appointment_date)}
                </span>
                <span className="overlay-text time-3" style={{ position: 'absolute', top: '38.8%', left: '64%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(3)?.appointment_date)}
                </span>
                <span className="overlay-text time-4" style={{ position: 'absolute', top: '38.8%', left: '82%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(4)?.appointment_date)}
                </span>

                {/* Maintenance Phase - 第5-9次 (左列 治疗时间) */}
                <span className="overlay-text time-5" style={{ position: 'absolute', top: '59%', left: '39%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(5)?.appointment_date)}
                </span>
                <span className="overlay-text time-6" style={{ position: 'absolute', top: '62.5%', left: '39%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(6)?.appointment_date)}
                </span>
                <span className="overlay-text time-7" style={{ position: 'absolute', top: '66%', left: '39%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(7)?.appointment_date)}
                </span>
                <span className="overlay-text time-8" style={{ position: 'absolute', top: '69.5%', left: '39%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(8)?.appointment_date)}
                </span>
                <span className="overlay-text time-9" style={{ position: 'absolute', top: '73%', left: '39%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(9)?.appointment_date)}
                </span>
              </div>
            </div>
          </>
        ) : (
          <Empty description="请先选择患者以预览打印内容" />
        )}
      </Card>
    </div>
  );
};

export default PrintCenter;
