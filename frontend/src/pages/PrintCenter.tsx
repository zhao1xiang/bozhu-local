import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Select, Button, message, Space, Descriptions, Empty } from 'antd';
import { PrinterOutlined, ReloadOutlined } from '@ant-design/icons';
import { Patient, Appointment } from '@/types';
import { apiClient } from '@/api/client';
import dayjs from 'dayjs';

const colors = {
  blue: '#1677f7',
  blueBg: '#f0f5ff',
  blueBorder: '#adcf6',
  text1: '#1d2939',
  text2: '#6b7280',
};

interface AppTitem {
  id?: string;
  appointment_date?: string;
  follow_up_date?: string;
  injection_count?: number;
  treatment_phase?: string;
  time_slot?: string;
  condition_status?: string;
  eye?: string;
  drug_name?: string;
  doctor?: string;
  status?: string;
  source?: string;
  is_new?: boolean;
}

const PrintCenter: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [printPhoneNumber, setPrintPhoneNumber] = useState<string>('');
  const autoPrintRef = useRef(false);

  const selectedPatient = patients?.find(p => p.id === selectedPatientId);

  const fetchPatients = async () => {
    try {
      const response = await apiClient.get<Patient[]>('/patients');
      setPatients(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error(error);
      message.error('获取患者列表失败');
      setPatients([]);
    }
  };

  const fetchAppointments = async (patientId: string) => {
    setLoading(true);
    try {
      const response = await apiClient.get<Appointment[]>('/appointments', {
        params: { patient_id: patientId, limit: 100 },
      });
      const data = Array.isArray(response.data) ? response.data : [];
      const sorted = data
        .filter(a => a.patient_id === patientId)
        .sort((a, b) => (a.injection_count || 0) - (b.injection_count || 0));
      setAppointments(sorted);
    } catch (error) {
      console.error(error);
      message.error('获取预约列表失败');
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrintPhone = async () => {
    try {
      const response = await apiClient.get('/system-settings/print_phone_number');
      setPrintPhoneNumber(response.data.value || '');
    } catch (error) {
      console.error('获取打印电话号码失败', error);
    }
  };

  useEffect(() => {
    fetchPatients();
    fetchPrintPhone();
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

  const getAppointmentByCount = (appts: Appointment[], count: number): AppTitem | undefined => {
    return appts?.find(a => a.injection_count === count);
  };

  const formatDate = (dateStr?: string): string => {
    if (!dateStr) return '';
    return dayjs(dateStr).format('M月D日');
  };

  const handlePrint = () => {
    const printArea = document.getElementById('print-area');
    if (!printArea) {
      message.error('打印区域未找到，请先选择患者');
      return;
    }

    try {
      message.info('正在准备打印...');

      // 创建打印样式
      const styleEl = document.createElement('style');
      styleEl.id = 'embed-print-style';
      styleEl.textContent = `
        @media print {
          @page { size: A4 portrait; margin: 8mm; }
          * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        }
        html, body { width: 210mm; height: 297mm; margin: 0; padding: 0; overflow: hidden; }
        body * { visibility: hidden; }
        #print-area, #print-area * { visibility: visible; }
        #print-area { position: fixed; left: 0; top: 0; width: 100%; height: 100%; margin: 0; padding: 0; display: flex; justify-content: center; align-items: flex-start; page-break-inside: avoid; page-break-after: avoid; }
        .print-container { width: 194mm !important; max-width: 194mm !important; height: auto !important; margin: 0 !important; padding: 0 !important; box-shadow: none !important; background: white !important; page-break-inside: avoid; page-break-after: avoid; position: relative; }
        .print-container img { width: 100% !important; max-width: 100% !important; height: auto !important; display: block; page-break-inside: avoid; }
        .overlay-text { position: absolute; font-family: "SimSun", "宋体", "SC", serif; font-weight: bold; }
        .overlay-text.name, .overlay-text.phone { font-size: 22.7px !important; /* 13px * 1.745 */ }
        .overlay-text.checkmark { font-size: 24.4px !important; /* 14px * 1.745 */ }
        .overlay-text.diagnosis { font-size: 20.9px !important; /* 12px * 1.745 */ }
        .overlay-text.drug { font-size: 20.9px !important; /* 12px * 1.745 */ }
        .overlay-text.vision { font-size: 19.2px !important; /* 11px * 1.745 */ }
        .overlay-text.doctor { font-size: 22.7px !important; /* 13px * 1.745 */ }
        .overlay-text.time-1, .overlay-text.time-2, .overlay-text.time-3, .overlay-text.time-4, .overlay-text.time-5, .overlay-text.time-6, .overlay-text.time-7, .overlay-text.time-8, .overlay-text.time-9 { font-size: 20.9px !important; /* 12px * 1.745 */ }
        .overlay-text.phone-row3 { font-size: 22.7px !important; }
      `;
      document.head.appendChild(styleEl);

      window.print();

      setTimeout(() => {
        const el = document.getElementById('embed-print-style');
        if (el) el.remove();
      }, 1000);
    } catch (error) {
      console.error('打印失败', error);
      message.error('打印失败：' + (error as Error).message);
    }
  };

  return (
    <div>
      <Card
        title="打印中心 - 玻注预约单"
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
                label: `${p.name} (${p.phone ? ` ${p.phone}` : ''})`,
                value: p.id,
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
            <Button icon={<ReloadOutlined />} onClick={fetchPatients} />
          </Space>
        }
      >
        {selectedPatient ? (
          <>
            <Descriptions bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="姓名">{selectedPatient.name}</Descriptions.Item>
              <Descriptions.Item label="电话">{selectedPatient.phone || '-'}</Descriptions.Item>
              <Descriptions.Item label="诊断">{selectedPatient.diagnosis || '-'}</Descriptions.Item>
              <Descriptions.Item label="用药">{selectedPatient.drug_type || '-'}</Descriptions.Item>
              <Descriptions.Item label="眼别">
                {selectedPatient.left_eye ? '左眼' : ''}{selectedPatient.right_eye ? '右眼' : ''}
              </Descriptions.Item>
              <Descriptions.Item label="预约数量">{appointments.length}</Descriptions.Item>
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
                minHeight: 600,
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
                  overflow: 'hidden',
                }}
              >
                <img
                  src="/print-template.png"
                  alt="打印模板"
                  style={{ width: '100%', display: 'block', height: 'auto' }}
                  onError={(e) => {
                    console.error('打印模板图片加载失败');
                    e.currentTarget.style.display = 'none';
                    const parent = e.currentTarget.parentElement;
                    if (parent) {
                      const errorDiv = document.createElement('div');
                      errorDiv.style.cssText = 'padding: 40px; text-align: center; color: #999;';
                      errorDiv.innerHTML = '打印模板图片加载失败<br/>请确认 print-template.png 存在于前端目录';
                      parent.appendChild(errorDiv);
                    }
                  }}
                />

                {/* Patient Info Overlay - Row 1: 姓名、电话、左眼✓、右眼✓ */}
                <span className="overlay-text name" style={{ position: 'absolute', top: '19.3%', left: '16%', fontSize: '13px', fontWeight: 'bold' }}>
                  {selectedPatient.name}
                </span>
                <span className="overlay-text phone" style={{ position: 'absolute', top: '19%', left: '52%', fontSize: '13px', fontWeight: 'bold' }}>
                  {selectedPatient.phone || ''}
                </span>
                {selectedPatient.left_eye && (
                  <span className="overlay-text checkmark" style={{ position: 'absolute', top: '19%', left: '73%', fontSize: '14px', fontWeight: 'bold' }}>
                    ✓
                  </span>
                )}
                {selectedPatient.right_eye && (
                  <span className="overlay-text checkmark" style={{ position: 'absolute', top: '19%', left: '86%', fontSize: '14px', fontWeight: 'bold' }}>
                    ✓
                  </span>
                )}

                {/* Patient Info Overlay - Row 2: 诊断、用药、视力 */}
                <span className="overlay-text diagnosis" style={{ position: 'absolute', top: '23.3%', left: '16%', fontSize: '12px', fontWeight: 'bold' }}>
                  {selectedPatient.diagnosis || ''}
                </span>
                <span className="overlay-text drug" style={{ position: 'absolute', top: '23.6%', left: '51%', fontSize: '12px', fontWeight: 'bold' }}>
                  {(() => {
                    const sorted = [...appointments].sort((a, b) => (b.injection_count || 0) - (a.injection_count || 0));
                    const found = sorted.find(a => a.drug_name);
                    return found?.drug_name || selectedPatient.drug_type || '';
                  })()}
                </span>
                <span className="overlay-text vision" style={{ position: 'absolute', top: '23.7%', left: '79%', fontSize: '11px', fontWeight: 'bold' }}>
                  {selectedPatient.left_vision || selectedPatient.right_vision
                    ? `${selectedPatient.left_vision || '-'}/${selectedPatient.right_vision || '-'}`
                    : ''}
                </span>

                {/* Patient Info Overlay - Row 3: 医生、复诊电话 */}
                <span className="overlay-text doctor" style={{ position: 'absolute', top: '26.5%', left: '16%', fontSize: '13px', fontWeight: 'bold' }}>
                  {(() => {
                    const sorted = [...appointments].sort((a, b) => (b.injection_count || 0) - (a.injection_count || 0));
                    return sorted.find(a => a.doctor)?.doctor || '';
                  })()}
                </span>
                <span className="overlay-text phone-row3" style={{ position: 'absolute', top: '26.5%', left: '63%', fontSize: '13px', fontWeight: 'bold' }}>
                  {printPhoneNumber}
                </span>

                {/* 第1-4次：横向，治疗时间行 */}
                <span className="overlay-text time-1" style={{ position: 'absolute', top: '40.5%', left: '28%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(appointments, 1)?.appointment_date)}
                </span>
                <span className="overlay-text time-2" style={{ position: 'absolute', top: '40.5%', left: '46%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(appointments, 2)?.appointment_date)}
                </span>
                <span className="overlay-text time-3" style={{ position: 'absolute', top: '40.5%', left: '64%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(appointments, 3)?.appointment_date)}
                </span>
                <span className="overlay-text time-4" style={{ position: 'absolute', top: '40.5%', left: '82%', fontSize: '12px', fontWeight: 'bold' }}>
                  {formatDate(getAppointmentByCount(appointments, 4)?.appointment_date)}
                </span>

                {/* 第5-9次：根据 condition_status 分左右列
                    稳定 → 左侧"治疗时间"列 left: 39%
                    不稳定/趋差 → 右侧"治疗时间"列 left: 83%
                */}
                {[5, 6, 7, 8, 9].map((n, idx) => {
                  const app = getAppointmentByCount(appointments, n);
                  if (!app?.appointment_date) return null;
                  const isUnstable = app.condition_status === '趋差' || app.condition_status === '不稳定';
                  const topPct = 60.3 + idx * 3.5;
                  const leftPct = isUnstable ? 83 : 39;
                  return (
                    <span key={n} className={`overlay-text time-${n}`} style={{ position: 'absolute', top: `${topPct}%`, left: `${leftPct}%`, fontSize: '12px', fontWeight: 'bold' }}>
                      {formatDate(app.appointment_date)}
                    </span>
                  );
                })}
              </div>
            </div>
          </>
        ) : (
          <Empty description="请选择患者以预览打印内容" />
        )}
      </Card>
    </div>
  );
};

export default PrintCenter;
