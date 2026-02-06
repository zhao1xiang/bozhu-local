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

  const selectedPatient = patients.find(p => p.id === selectedPatientId);

  const fetchPatients = async () => {
    try {
      const response = await apiClient.get<Patient[]>('/patients');
      setPatients(response.data);
    } catch (error) {
      console.error(error);
      message.error('获取患者列表失败');
    }
  };

  const fetchAppointments = async (patientId: string) => {
    setLoading(true);
    try {
      const response = await apiClient.get<Appointment[]>('/appointments', {
        params: { patient_id: patientId, limit: 100 }
      });
      // Sort by injection_count
      const sorted = response.data
        .filter(a => a.patient_id === patientId)
        .sort((a, b) => (a.injection_count || 0) - (b.injection_count || 0));
      setAppointments(sorted);
    } catch (error) {
      console.error(error);
      message.error('获取预约列表失败');
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
    if (!printArea) return;

    // Clone the node to manipulate/clean it if necessary, though innerHTML is usually enough
    // We want to ensure the print window uses the exact same styles as the preview

    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>打印注射卡 - ${selectedPatient?.name}</title>
            <style>
              @page {
                size: A5;
                margin: 0;
              }
              body {
                margin: 0;
                padding: 0;
                font-family: "SimSun", "Songti SC", serif;
                display: flex;
                justify-content: center;
                align-items: flex-start;
              }
              /* Use the same container logic as preview */
              .print-container {
                position: relative !important;
                width: 100% !important; /* Fill the A5 page width */
                max-width: 148mm;
                /* Height auto to maintain aspect ratio same as preview */
                height: auto !important; 
              }
              img {
                width: 100%;
                display: block;
              }
              .overlay-text {
                position: absolute;
                font-family: inherit;
                font-weight: bold;
                /* Font size adjustment for print sharpness if needed, 
                   but percentages will be relative to container */
              }
            </style>
          </head>
          <body>
            <!-- We wrap inner content in a way that matches the structure -->
            ${printArea.querySelector('.print-container')?.outerHTML || ''}
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.focus();
      // Wait for image to load before printing
      setTimeout(() => {
        printWindow.print();
        printWindow.close();
      }, 500);
    }
  };

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
                borderRadius: 8
              }}
            >
              <div
                className="print-container"
                style={{
                  position: 'relative',
                  width: '420px',
                  background: '#fff',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                }}
              >
                <img src="/print-template.png" alt="打印模板" style={{ width: '100%' }} />

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
