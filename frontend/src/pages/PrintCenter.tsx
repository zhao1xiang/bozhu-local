import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Select, Button, message, Space, Descriptions, Empty } from 'antd';
import { PrinterOutlined, ReloadOutlined } from '@ant-design/icons';
import { Patient, Appointment } from '@/types';
import { apiClient } from '@/api/client';
import dayjs from 'dayjs';

interface AppTitem {
  id?: string;
  appointment_date?: string;
  injection_count?: number;
  condition_status?: string;
  drug_name?: string;
  doctor?: string;
}

// ============================================================
// 切换打印模式：true = HTML模板，false = 图片覆盖文字
// ============================================================
const USE_HTML_TEMPLATE = true;

const PrintCenter: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [printPhoneNumber, setPrintPhoneNumber] = useState<string>('');
  const [previewHtml, setPreviewHtml] = useState<string>('');

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

  useEffect(() => { fetchPatients(); fetchPrintPhone(); }, []);

  useEffect(() => {
    const patientIdParam = searchParams.get('patient_id');
    if (patientIdParam) setSelectedPatientId(patientIdParam);
  }, [searchParams]);

  useEffect(() => {
    if (selectedPatientId) fetchAppointments(selectedPatientId);
    else setAppointments([]);
  }, [selectedPatientId]);

  const getApptByCount = (n: number): AppTitem | undefined =>
    appointments.find(a => a.injection_count === n);

  const fmt = (d?: string) => d ? dayjs(d).format('YYYY年M月D日') : '';

  const buildPrintData = () => {
    if (!selectedPatient) return null;
    const sorted = [...appointments].sort((a, b) => (b.injection_count || 0) - (a.injection_count || 0));
    const drug = sorted.find(a => a.drug_name)?.drug_name || selectedPatient.drug_type || '';
    const doctor = sorted.find(a => a.doctor)?.doctor || '';
    const visionParts = [];
    if (selectedPatient.right_vision) visionParts.push(`右眼：${selectedPatient.right_vision}`);
    if (selectedPatient.left_vision) visionParts.push(`左眼：${selectedPatient.left_vision}`);
    const vision = visionParts.join('  ');

    const stable = (n: number) => {
      const a = getApptByCount(n);
      if (!a?.appointment_date) return '';
      return (a.condition_status === '趋差' || a.condition_status === '不稳定') ? '' : fmt(a.appointment_date);
    };
    const unstable = (n: number) => {
      const a = getApptByCount(n);
      if (!a?.appointment_date) return '';
      return (a.condition_status === '趋差' || a.condition_status === '不稳定') ? fmt(a.appointment_date) : '';
    };

    return {
      name: selectedPatient.name || '', phone: selectedPatient.phone || '',
      leftEye: selectedPatient.left_eye, rightEye: selectedPatient.right_eye,
      diagnosis: selectedPatient.diagnosis || '', drug, vision, doctor,
      clinicPhone: printPhoneNumber,
      d1: fmt(getApptByCount(1)?.appointment_date), d2: fmt(getApptByCount(2)?.appointment_date),
      d3: fmt(getApptByCount(3)?.appointment_date), d4: fmt(getApptByCount(4)?.appointment_date),
      s5: stable(5), s6: stable(6), s7: stable(7), s8: stable(8), s9: stable(9),
      u5: unstable(5), u6: unstable(6), u7: unstable(7), u8: unstable(8), u9: unstable(9),
    };
  };

  const buildFilledHtml = async (): Promise<string> => {
    const pd = buildPrintData();
    if (!pd) return '';
    const res = await fetch(`/print-template.html?t=${Date.now()}`);
    let html = await res.text();
    // 把相对路径图片替换为绝对 URL，解决 iframe srcDoc 无法加载相对路径的问题
    const baseUrl = window.location.origin;
    html = html.replace(/src="(?!http|data:)([^"]+)"/g, `src="${baseUrl}/$1"`);

    // 预加载 HTML 里的所有图片，确保 iframe 渲染时图片已缓存
    const imgMatches = html.match(/src="(https?:\/\/[^"]+)"/g) || [];
    await Promise.all(imgMatches.map((m: string) => {
      const url = m.replace(/^src="/, '').replace(/"$/, '');
      return new Promise<void>(resolve => {
        const img = new Image();
        img.onload = img.onerror = () => resolve();
        img.src = url;
      });
    }));

    return html
      .replace('{{姓名}}', pd.name).replace('{{联系方式}}', pd.phone)
      .replace('{{左眼勾}}', pd.leftEye ? '✓' : '').replace('{{右眼勾}}', pd.rightEye ? '✓' : '')
      .replace('{{诊断}}', pd.diagnosis).replace('{{治疗药物}}', pd.drug)
      .replace('{{视力}}', pd.vision).replace('{{医生}}', pd.doctor)
      .replace('{{复诊电话}}', pd.clinicPhone)
      .replace('{{第1次}}', pd.d1).replace('{{第2次}}', pd.d2)
      .replace('{{第3次}}', pd.d3).replace('{{第4次}}', pd.d4)
      .replace('{{第5次稳定}}', pd.s5).replace('{{第6次稳定}}', pd.s6)
      .replace('{{第7次稳定}}', pd.s7).replace('{{第8次稳定}}', pd.s8).replace('{{第9次稳定}}', pd.s9)
      .replace('{{第5次不稳定}}', pd.u5).replace('{{第6次不稳定}}', pd.u6)
      .replace('{{第7次不稳定}}', pd.u7).replace('{{第8次不稳定}}', pd.u8).replace('{{第9次不稳定}}', pd.u9);
  };

  // 患者或预约数据变化时更新预览
  useEffect(() => {
    if (!selectedPatient || !USE_HTML_TEMPLATE) { setPreviewHtml(''); return; }
    buildFilledHtml().then(html => setPreviewHtml(html)).catch(() => setPreviewHtml(''));
  }, [selectedPatient, appointments, printPhoneNumber]);

  const injectAndPrint = (html: string) => {
    // 先清理可能残留的旧打印区域
    document.getElementById('html-print-area')?.remove();
    document.getElementById('html-print-style')?.remove();
    const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
    const styleMatch = html.match(/<style[^>]*>([\s\S]*?)<\/style>/gi);
    const bodyContent = bodyMatch ? bodyMatch[1] : html;
    const rawStyles = styleMatch ? styleMatch.map((s: string) => s.replace(/<\/?style[^>]*>/gi, '')).join('\n') : '';

    const printDiv = document.createElement('div');
    printDiv.id = 'html-print-area';
    printDiv.innerHTML = bodyContent;
    document.body.appendChild(printDiv);

    const styleEl = document.createElement('style');
    styleEl.id = 'html-print-style';
    const scopedStyles = rawStyles.replace(/([^{}]+)\{/g, (match: string, selector: string) => {
      const trimmed = selector.trim();
      if (trimmed.startsWith('@') || trimmed.startsWith('from') || trimmed.startsWith('to')) return match;
      const scoped = trimmed.split(',').map((s: string) => `#html-print-area ${s.trim()}`).join(', ');
      return `${scoped} {`;
    });
    styleEl.textContent = `
      ${scopedStyles}
      #html-print-area { position: fixed; left: 0; top: 0; width: 100%; height: 100%; background: white; z-index: 99999; overflow: auto; font-family: "SimSun","宋体",serif; font-size: 14px; color: #000; padding: 8mm 10mm; box-sizing: border-box; }
      @media print {
        @page { size: A4 portrait; margin: 8mm; }
        body > *:not(#html-print-area):not(#html-print-style) { display: none !important; }
        #html-print-area { position: static !important; width: 194mm !important; height: auto !important; overflow: visible !important; padding: 0 !important; z-index: auto !important; }
      }
    `;
    document.head.appendChild(styleEl);

    // 等待所有图片加载完成后再打印
    const imgs = Array.from(printDiv.querySelectorAll('img')) as HTMLImageElement[];
    const waitAll = imgs.map(img => new Promise<void>(resolve => {
      if (img.complete && img.naturalWidth > 0) { resolve(); return; }
      img.onload = () => resolve();
      img.onerror = () => resolve();
    }));
    Promise.all(waitAll).then(() => {
      window.print();
      setTimeout(() => {
        document.getElementById('html-print-area')?.remove();
        document.getElementById('html-print-style')?.remove();
      }, 1000);
    });
  };

  const handlePrint = async () => {
    if (USE_HTML_TEMPLATE) {
      try {
        const html = await buildFilledHtml();
        if (!html) return;
        injectAndPrint(html);
      } catch (e) {
        message.error('加载打印模板失败');
      }
      return;
    }

    // ===== 图片覆盖文字打印（保留，切换 USE_HTML_TEMPLATE=false 即可恢复）=====
    const printArea = document.getElementById('print-area');
    if (!printArea) { message.error('打印区域未找到'); return; }
    try {
      const styleEl = document.createElement('style');
      styleEl.id = 'img-print-style';
      styleEl.textContent = `
        @media print { @page { size: A4 portrait; margin: 8mm; } * { -webkit-print-color-adjust: exact !important; } }
        html, body { width: 210mm; height: 297mm; margin: 0; padding: 0; overflow: hidden; }
        body * { visibility: hidden; }
        #print-area, #print-area * { visibility: visible; }
        #print-area { position: fixed; left: 0; top: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: flex-start; }
        .print-container { width: 194mm !important; position: relative; }
        .print-container img { width: 100% !important; display: block; }
        .overlay-text { position: absolute; font-family: "SimSun","宋体",serif; font-weight: bold; }
      `;
      document.head.appendChild(styleEl);
      window.print();
      setTimeout(() => { document.getElementById('img-print-style')?.remove(); }, 1000);
    } catch (error) {
      message.error('打印失败');
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

            {/* 预览区域 */}
            {USE_HTML_TEMPLATE ? (
              previewHtml ? (
                <iframe
                  srcDoc={previewHtml}
                  style={{ width: '100%', height: '900px', border: 'none', borderRadius: 8, background: '#f0f0f0' }}
                  title="打印预览"
                />
              ) : (
                <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>正在加载预览...</div>
              )
            ) : (
              <div id="print-area" style={{ display: 'flex', justifyContent: 'center', background: '#f0f0f0', padding: 20, borderRadius: 8, minHeight: 600 }}>
                <div className="print-container" style={{ position: 'relative', width: '420px', background: '#fff', boxShadow: '0 2px 8px rgba(0,0,0,0.15)' }}>
                  <img src="/print-template.png" alt="打印模板" style={{ width: '100%', display: 'block' }} />
                </div>
              </div>
            )}
          </>
        ) : (
          <Empty description="请选择患者以预览打印内容" />
        )}
      </Card>
    </div>
  );
};

export default PrintCenter;
