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
      message.error('鑾峰彇鎮ｈ€呭垪琛ㄥけ璐?);
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
      message.error('鑾峰彇棰勭害鍒楄〃澶辫触');
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
    return dayjs(dateStr).format('M鏈圖鏃?);
  };

  const handlePrint = () => {
    const printArea = document.getElementById('print-area');
    if (!printArea) {
      message.error('鎵撳嵃鍖哄煙鏈壘鍒帮紝璇峰埛鏂伴〉闈㈤噸璇?);
      return;
    }

    try {
      message.info('姝ｅ湪鍑嗗鎵撳嵃...');
      
      // 娣诲姞鎵撳嵃鏍峰紡 - 淇濇寔瀛椾綋澶у皬涓€鑷?      const style = document.createElement('style');
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
          
          /* 璋冩暣瀛椾綋澶у皬浠ュ尮閰嶆墦鍗扮缉鏀炬瘮渚?*/
          /* 鍘熷瀹瑰櫒瀹藉害 420px锛屾墦鍗板搴?194mm 鈮?733px */
          /* 缂╂斁姣斾緥锛?33 / 420 鈮?1.745 */
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
      
      // 鎵ц鎵撳嵃
      window.print();
      
      // 鎵撳嵃瀹屾垚鍚庣Щ闄ゆ牱寮?      setTimeout(() => {
        const styleEl = document.getElementById('print-style');
        if (styleEl) {
          styleEl.remove();
        }
      }, 1000);
    } catch (error) {
      console.error('鎵撳嵃杩囩▼涓彂鐢熼敊璇?', error);
      message.error('鎵撳嵃澶辫触: ' + (error as Error).message);
    }
  }

  return (
    <div>
      <Card
        title="鎵撳嵃涓績 - 鐜绘敞澶嶈瘖娉ㄥ皠鍗?
        extra={
          <Space>
            <Select
              showSearch
              style={{ width: 280 }}
              placeholder="璇烽€夋嫨鎮ｈ€?
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
              鎵撳嵃
            </Button>
          </Space>
        }
      >
        {selectedPatient ? (
          <>
            <Descriptions bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="濮撳悕">{selectedPatient.name}</Descriptions.Item>
              <Descriptions.Item label="鐢佃瘽">{selectedPatient.phone || '-'}</Descriptions.Item>
              <Descriptions.Item label="璇婃柇">{selectedPatient.diagnosis || '-'}</Descriptions.Item>
              <Descriptions.Item label="鑽墿">{selectedPatient.drug_type || '-'}</Descriptions.Item>
              <Descriptions.Item label="娌荤枟鐪?>
                {selectedPatient.left_eye ? '宸︾溂 ' : ''}{selectedPatient.right_eye ? '鍙崇溂' : ''}
              </Descriptions.Item>
              <Descriptions.Item label="棰勭害鏁?>{appointments.length} 娆?/Descriptions.Item>
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
                <img src="/print-template.png" alt="鎵撳嵃妯℃澘" style={{ width: '100%' }} />

                {/* Patient Info Overlay - Row 1: 濮撳悕銆佽仈绯绘柟寮忋€佸乏鐪煎彸鐪?*/}
                <span className="overlay-text name" style={{ position: 'absolute', top: '20%', left: '16%', fontSize: '13px', fontWeight: 'bold' }}>
                  {selectedPatient.name}
                </span>
                <span className="overlay-text phone" style={{ position: 'absolute', top: '20%', left: '53%', fontSize: '13px', fontWeight: 'bold' }}>
                  {selectedPatient.phone || ''}
                </span>
                {selectedPatient.left_eye && (
                  <span className="overlay-text checkmark" style={{ position: 'absolute', top: '20%', left: '73%', fontSize: '14px', fontWeight: 'bold' }}>
                    鉁?                  </span>
                )}
                {selectedPatient.right_eye && (
                  <span className="overlay-text checkmark" style={{ position: 'absolute', top: '20%', left: '86%', fontSize: '14px', fontWeight: 'bold' }}>
                    鉁?                  </span>
                )}

                {/* Patient Info Overlay - Row 2: 璇婃柇銆佹不鐤楄嵂鐗┿€佺溂瑙嗗姏 */}
                <span className="overlay-text diagnosis" style={{ position: 'absolute', top: '24%', left: '16%', fontSize: '12px', fontWeight: 'bold' }}>
                  {selectedPatient.diagnosis || ''}
                </span>
                <span className="overlay-text drug" style={{ position: 'absolute', top: '24%', left: '51%', fontSize: '12px', fontWeight: 'bold' }}>
                  {selectedPatient.drug_type || ''}
                </span>
                <span className="overlay-text vision" style={{ position: 'absolute', top: '24%', left: '79%', fontSize: '11px', fontWeight: 'bold' }}>
                  {selectedPatient.left_vision || selectedPatient.right_vision
                    ? `宸?{selectedPatient.left_vision || '-'} 鍙?{selectedPatient.right_vision || '-'}`
                    : ''}
                </span>

                {/* Initial Phase - 绗?-4娆℃不鐤楁椂闂?(娌荤枟鏃堕棿琛? */}
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

                {/* Maintenance Phase - 绗?-9娆?(宸﹀垪 娌荤枟鏃堕棿) */}
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
          <Empty description="璇峰厛閫夋嫨鎮ｈ€呬互棰勮鎵撳嵃鍐呭" />
        )}
      </Card>
    </div>
  );
};

export default PrintCenter;
