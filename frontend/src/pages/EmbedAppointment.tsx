import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Select, DatePicker, InputNumber, Button,
  Row, Col, message, Spin, Alert, Tabs,
} from 'antd';
import { CheckCircleOutlined, PrinterOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { apiClient } from '@/api/client';

const colors = {
  blue: '#1677f7',
  blueBg: '#f0f5ff',
  blueBorder: '#adcf6',
};

interface AppItem {
  id?: string;
  appointment_date?: Dayjs | null;
  follow_up_date?: Dayjs | null;
  injection_count?: number;
  treatment_phase?: string;
  time_slot?: string;
  condition_status?: string;
  eye?: string;
  drug_name?: string;
  doctor?: string;
  source?: string;
}

interface PatientData {
  id?: string;
  name?: string;
  outpatient_number?: string;
  phone?: string;
  diagnosis?: string;
  drug_name?: string;
  eye?: string;
  injection_count?: number;
  doctor?: string;
  patient_type?: string;
}

// 从给定日期向后找最近的玻注日
const getNearestInjectionDate = (base: Dayjs, weekdays: string[]): Dayjs => {
  const allowed = weekdays.map(w => parseInt(w, 10)).filter(n => !isNaN(n));
  if (!allowed.length) return base;
  for (let i = 0; i < 14; i++) {
    const c = base.add(i, 'day');
    const wd = c.day() === 0 ? 7 : c.day();
    if (allowed.includes(wd)) return c;
  }
  return base;
};

// 根据针次计算下一次预约基准日期（与 Appointments.tsx 一致）
const getNextAppointmentDate = (base: Dayjs, injectionCount: number, intervalDays: number): Dayjs => {
  if (injectionCount <= 4) return base.add(intervalDays, 'day');
  if (injectionCount === 5) return base.add(2, 'month');
  if (injectionCount === 6) return base.add(3, 'month');
  return base.add(4, 'month');
};

const EmbedAppointment: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [printSaving, setPrintSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [activeTab, setActiveTab] = useState<string>('bozhu');
  const [savedOk, setSavedOk] = useState(false);

  const [bozhuAppts, setBozhuAppts] = useState<AppItem[]>([
    { injection_count: 1 },
    { injection_count: 2 },
    { injection_count: 3 },
    { injection_count: 4 },
  ]);
  const [periAppt, setPeriAppt] = useState<AppItem>({ injection_count: 1 });

  const [injectionWeekdays, setInjectionWeekdays] = useState<string[]>(['1']);
  const [injectionIntervalFirst4, setInjectionIntervalFirst4] = useState<number>(30);

  useEffect(() => {
    const dataParam = searchParams.get('data');
    const signParam = searchParams.get('sign');
    if (!dataParam || !signParam) {
      setError('缺少必要参数：data 或 sign');
      setLoading(false);
      return;
    }
    verifyAndLoad(dataParam, signParam);
  }, []);

  const verifyAndLoad = async (data: string, sign: string) => {
    try {
      // 并行获取系统配置和验证数据
      const [wdRes, intRes, verifyRes] = await Promise.all([
        apiClient.get('/system-settings/injection_weekday').catch(() => ({ data: { value: '1' } })),
        apiClient.get('/system-settings/injection_interval_first_4').catch(() => ({ data: { value: '30' } })),
        apiClient.get('/embed/verify', { params: { data, sign } }),
      ]);

      const wd = (wdRes.data?.value || '1').split(',').filter(Boolean);
      const interval = parseInt(intRes.data?.value || '30');
      setInjectionWeekdays(wd);
      setInjectionIntervalFirst4(interval);

      const { patient, appointments, payload } = verifyRes.data;

      const pd: PatientData = {
        id: patient?.id,
        name: payload?.name,
        outpatient_number: payload?.outpatient_number,
        phone: payload?.phone,
        diagnosis: payload?.diagnosis,
        drug_name: payload?.drug_name,
        eye: payload?.eye,
        injection_count: payload?.injection_count,
        doctor: payload?.doctor,
        patient_type: (payload?.injection_count >= 1) ? '经治' : '初治',
      };
      setPatientData(pd);

      // 如果有已有预约，填充；否则按系统逻辑自动生成
      if (Array.isArray(appointments) && appointments.length > 0) {
        // 填充玻注预约：直接用所有非围手术期预约，按针次排序
        const bozhuList = appointments
          .filter((a: any) => a.treatment_phase !== '围手术期')
          .sort((a: any, b: any) => (a.injection_count || 0) - (b.injection_count || 0))
          .map((a: any) => ({
            ...a,
            appointment_date: a.appointment_date ? dayjs(a.appointment_date) : null,
            follow_up_date: a.follow_up_date ? dayjs(a.follow_up_date) : null,
          }));
        setBozhuAppts(bozhuList.length > 0 ? bozhuList : [{ injection_count: 1 }, { injection_count: 2 }, { injection_count: 3 }, { injection_count: 4 }]);

        // 填充围手术期
        const periFound = appointments.find((a: any) => a.treatment_phase === '围手术期');
        if (periFound) {
          setPeriAppt({
            ...periFound,
            appointment_date: periFound.appointment_date ? dayjs(periFound.appointment_date) : null,
            follow_up_date: periFound.follow_up_date ? dayjs(periFound.follow_up_date) : null,
          });
        } else {
          // 没有围手术期记录，按系统逻辑生成默认值
          const periDate = getNearestInjectionDate(dayjs(), wd);
          setPeriAppt({
            injection_count: 1,
            appointment_date: periDate,
            follow_up_date: periDate,
            treatment_phase: '围手术期',
            time_slot: '上午',
            condition_status: '稳定',
          });
        }
      } else {
        // 没有已有预约，按系统逻辑自动生成4次玻注预约
        const generated = generateDates(wd, interval);
        setBozhuAppts(generated);
        // 围手术期默认找最近玻注日
        const periDate = getNearestInjectionDate(dayjs(), wd);
        setPeriAppt({
          injection_count: 1,
          appointment_date: periDate,
          follow_up_date: periDate,
          treatment_phase: '围手术期',
          time_slot: '上午',
          condition_status: '稳定',
        });
      }

      setLoading(false);
    } catch (e: any) {
      setError(e?.response?.data?.detail || '签名验证失败或请求已过期');
      setLoading(false);
    }
  };

  // 按系统逻辑生成4次预约日期
  const generateDates = (weekdays: string[], intervalDays: number): AppItem[] => {
    let currentBase = dayjs();
    const result: AppItem[] = [];
    for (let i = 0; i < 4; i++) {
      const cnt = i + 1;
      const date = getNearestInjectionDate(currentBase, weekdays);
      result.push({
        injection_count: cnt,
        appointment_date: date,
        follow_up_date: date,
        treatment_phase: '强化期',
        time_slot: '上午',
        condition_status: '稳定',
      });
      currentBase = getNextAppointmentDate(date, cnt + 1, intervalDays);
    }
    return result;
  };

  const updateBozhuAppt = (idx: number, field: string, value: any) => {
    setBozhuAppts(prev => prev.map((a, i) => i === idx ? { ...a, [field]: value } : a));
  };

  const updatePeriAppt = (field: string, value: any) => {
    setPeriAppt(prev => ({ ...prev, [field]: value }));
  };

  const validateRequired = (): string[] => {
    const missing: string[] = [];
    if (!patientData?.name) missing.push('姓名');
    if (!patientData?.outpatient_number) missing.push('住院号');
    if (!patientData?.phone) missing.push('联系方式');
    if (!patientData?.diagnosis) missing.push('诊断');
    if (!patientData?.drug_name) missing.push('用药');
    if (!patientData?.eye) missing.push('治疗眼');
    if (!patientData?.doctor) missing.push('注药医生');
    return missing;
  };

  const buildPayload = (source: string) => {
    const appts = activeTab === 'bozhu'
      ? bozhuAppts.map(a => ({
          ...a,
          appointment_date: a.appointment_date ? dayjs(a.appointment_date).format('YYYY-MM-DD') : undefined,
          follow_up_date: a.follow_up_date ? dayjs(a.follow_up_date).format('YYYY-MM-DD') : undefined,
          eye: patientData?.eye,
          drug_name: patientData?.drug_name,
          doctor: patientData?.doctor,
          source,
        }))
      : [{
          ...periAppt,
          appointment_date: periAppt.appointment_date ? dayjs(periAppt.appointment_date).format('YYYY-MM-DD') : undefined,
          follow_up_date: periAppt.follow_up_date ? dayjs(periAppt.follow_up_date).format('YYYY-MM-DD') : undefined,
          eye: patientData?.eye,
          drug_name: patientData?.drug_name,
          doctor: patientData?.doctor,
          source,
          treatment_phase: '围手术期',
        }];

    return {
      patient: {
        name: patientData?.name,
        outpatient_number: patientData?.outpatient_number,
        phone: patientData?.phone,
        diagnosis: patientData?.diagnosis,
        drug_name: patientData?.drug_name,
        eye: patientData?.eye,
        injection_count: patientData?.injection_count,
        doctor: patientData?.doctor,
        patient_type: patientData?.patient_type,
      },
      appointments: appts.filter(a => a.appointment_date),
    };
  };

  const handleSave = async () => {
    const missing = validateRequired();
    if (missing.length > 0) {
      setError(`以下必填参数未传入：${missing.join('、')}`);
      return;
    }
    setSaving(true);
    try {
      const saveRes = await apiClient.post('/embed/save', buildPayload('embed_direct'));
      if (saveRes.data?.patient?.id) setPatientData(prev => ({ ...prev, id: saveRes.data.patient.id }));
      setSavedOk(true);
      message.success('预约保存成功');
      setTimeout(() => setSavedOk(false), 3000);
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAndPrint = async () => {
    const missing = validateRequired();
    if (missing.length > 0) {
      setError(`以下必填参数未传入：${missing.join('、')}`);
      return;
    }
    setPrintSaving(true);
    try {
      const saveRes = await apiClient.post('/embed/save', buildPayload('embed_print'));
      if (saveRes.data?.patient?.id) setPatientData(prev => ({ ...prev, id: saveRes.data.patient.id }));
      message.success('预约保存成功，正在打印...');
      renderAndPrint(saveRes.data?.patient, saveRes.data?.appointments || []);
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '保存失败，请重试');
    } finally {
      setPrintSaving(false);
    }
  };

  const renderAndPrint = (patient: any, appts: any[]) => {
    const sorted = [...(Array.isArray(appts) ? appts : [])].sort((a, b) => (a.injection_count || 0) - (b.injection_count || 0));
    const getApptByCount = (cnt: number) => sorted.find(a => a.injection_count === cnt);
    const fmtDate = (d?: string) => d ? dayjs(d).format('M月D日') : '';
    // 用前端保存的 patientData（含原始 payload 字段），不用后端返回的 patient 对象
    const pd = patientData;

    const imgUrl = `${window.location.origin}/print-template.png`;

    const styleEl = document.createElement('style');
    styleEl.id = 'embed-print-style';
    styleEl.textContent = `
      @media print {
        @page { size: A4 portrait; margin: 8mm; }
        * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        html, body { width: 210mm; height: 297mm; margin: 0; padding: 0; overflow: hidden; }
        body * { visibility: hidden; }
        #embed-print-area, #embed-print-area * { visibility: visible; }
        #embed-print-area { position: fixed; left: 0; top: 0; width: 100%; height: 100%; margin: 0; padding: 0; display: flex; justify-content: center; align-items: flex-start; }
        .print-container { width: 194mm !important; max-width: 194mm !important; height: auto !important; margin: 0 !important; padding: 0 !important; box-shadow: none !important; background: white !important; position: relative; }
        .print-container img { width: 100% !important; height: auto !important; display: block; }
        .overlay-text { position: absolute; font-family: "SimSun","宋体","SC",serif; font-weight: bold; }
        .overlay-text.ot-name, .overlay-text.ot-phone, .overlay-text.ot-doctor { font-size: 22.7px !important; }
        .overlay-text.ot-checkmark { font-size: 24.4px !important; }
        .overlay-text.ot-diagnosis { font-size: 20.9px !important; }
        .overlay-text.ot-drug { font-size: 20.9px !important; }
        .overlay-text.ot-vision { font-size: 19.2px !important; }
        .overlay-text.ot-time { font-size: 20.9px !important; }
      }
      #embed-print-area { position: fixed; left: 0; top: 0; width: 100%; height: 100%; margin: 0; padding: 0; display: flex; justify-content: center; align-items: flex-start; z-index: 99999; background: white; }
      .print-container { width: 194mm !important; max-width: 194mm !important; position: relative; }
      .print-container img { width: 100% !important; height: auto !important; display: block; }
      .overlay-text { position: absolute; font-family: "SimSun","宋体","SC",serif; font-weight: bold; }
      .overlay-text.ot-name, .overlay-text.ot-phone, .overlay-text.ot-doctor { font-size: 22.7px !important; }
      .overlay-text.ot-checkmark { font-size: 24.4px !important; }
      .overlay-text.ot-diagnosis { font-size: 20.9px !important; }
      .overlay-text.ot-drug { font-size: 20.9px !important; }
      .overlay-text.ot-vision { font-size: 19.2px !important; }
      .overlay-text.ot-time { font-size: 20.9px !important; }
    `;
    document.head.appendChild(styleEl);

    const printDiv = document.createElement('div');
    printDiv.id = 'embed-print-area';
    printDiv.innerHTML = `
      <div class="print-container">
        <img src="${imgUrl}" alt="模板" />
        <span class="overlay-text ot-name" style="top:19.3%;left:16%">${pd?.name || ''}</span>
        <span class="overlay-text ot-phone" style="top:19%;left:52%">${pd?.phone || ''}</span>
        ${(pd?.eye === '左眼' || pd?.eye === '双眼') ? '<span class="overlay-text ot-checkmark" style="top:19%;left:73%">✓</span>' : ''}
        ${(pd?.eye === '右眼' || pd?.eye === '双眼') ? '<span class="overlay-text ot-checkmark" style="top:19%;left:86%">✓</span>' : ''}
        <span class="overlay-text ot-diagnosis" style="top:23.3%;left:16%">${pd?.diagnosis || ''}</span>
        <span class="overlay-text ot-drug" style="top:23.6%;left:51%">${pd?.drug_name || ''}</span>
        <span class="overlay-text ot-doctor" style="top:26.5%;left:16%">${sorted[0]?.doctor || pd?.doctor || ''}</span>
        <span class="overlay-text ot-time" style="top:40.5%;left:28%">${fmtDate(getApptByCount(1)?.appointment_date)}</span>
        <span class="overlay-text ot-time" style="top:40.5%;left:46%">${fmtDate(getApptByCount(2)?.appointment_date)}</span>
        <span class="overlay-text ot-time" style="top:40.5%;left:64%">${fmtDate(getApptByCount(3)?.appointment_date)}</span>
        <span class="overlay-text ot-time" style="top:40.5%;left:82%">${fmtDate(getApptByCount(4)?.appointment_date)}</span>
        ${[5,6,7,8,9].map((n, idx) => {
          const a = getApptByCount(n);
          if (!a?.appointment_date) return '';
          const isUnstable = a.condition_status === '趋差' || a.condition_status === '不稳定';
          const topPct = 60.3 + idx * 3.5;
          const leftPct = isUnstable ? 83 : 39;
          return `<span class="overlay-text ot-time" style="top:${topPct}%;left:${leftPct}%">${fmtDate(a.appointment_date)}</span>`;
        }).join('')}
      </div>
    `;
    document.body.appendChild(printDiv);

    // 等图片加载完成后再打印（静默方式）
    const img = printDiv.querySelector('img') as HTMLImageElement;
    const cleanup = () => {
      document.getElementById('embed-print-style')?.remove();
      document.getElementById('embed-print-area')?.remove();
    };
    const doPrint = () => {
      window.print();
      setTimeout(cleanup, 1000);
    };
    if (img.complete && img.naturalWidth > 0) {
      doPrint();
    } else {
      img.onload = doPrint;
      img.onerror = () => {
        message.error('打印模板图片加载失败，请检查网络');
        cleanup();
      };
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', background: colors.blueBg }}>
        <Spin size="large" />
        <div style={{ marginTop: 12, color: colors.blue }}>正在验证身份...</div>
      </div>
    );
  }

  if (error && !patientData) {
    return (
      <div style={{ padding: 24, maxWidth: 600, margin: '40px auto' }}>
        <Alert type="error" message="参数错误" description={error} showIcon style={{ borderRadius: 10 }} />
      </div>
    );
  }

  return (
    <div style={{ background: colors.blueBg, minHeight: '100vh', padding: '16px' }}>
      <div style={{ maxWidth: 860, margin: '0 auto', background: '#fff', borderRadius: 12, padding: '16px 24px', boxShadow: '0 1px 6px rgba(0,0,0,0.12)', border: `1px solid ${colors.blueBorder}` }}>

        {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 12, borderRadius: 8 }} />}
        {savedOk && <Alert type="success" message="预约保存成功" showIcon style={{ marginBottom: 12, borderRadius: 8 }} />}

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            { key: 'bozhu', label: '玻注预约' },
            { key: 'peri', label: '围手术期预约' },
          ]}
        />

        {activeTab === 'bozhu' && (
          <>
            {bozhuAppts.map((appt, idx) => (
              <div key={idx} style={{ background: '#fafafa', borderRadius: 8, padding: '10px 16px', marginBottom: 8, border: '1px solid #e8e8e8' }}>
                <Row gutter={12} align="middle">
                  <Col span={2}>
                    <span style={{ color: colors.blue, fontWeight: 'bold', fontSize: 13 }}>第{appt.injection_count}针</span>
                  </Col>
                  <Col span={5}>
                    <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>玻注日期</div>
                    <DatePicker
                      size="small"
                      style={{ width: '100%' }}
                      value={appt.appointment_date ? dayjs(appt.appointment_date) : undefined}
                      onChange={v => updateBozhuAppt(idx, 'appointment_date', v)}
                    />
                  </Col>
                  <Col span={4}>
                    <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>时间段</div>
                    <Select
                      size="small"
                      style={{ width: '100%' }}
                      value={appt.time_slot}
                      onChange={v => updateBozhuAppt(idx, 'time_slot', v)}
                      options={[{ label: '上午', value: '上午' }, { label: '下午', value: '下午' }]}
                    />
                  </Col>
                  <Col span={4}>
                    <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>针次</div>
                    <InputNumber
                      size="small"
                      min={1}
                      style={{ width: '100%' }}
                      value={appt.injection_count}
                      onChange={v => updateBozhuAppt(idx, 'injection_count', v)}
                    />
                  </Col>
                  <Col span={4}>
                    <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>状况</div>
                    <Select
                      size="small"
                      style={{ width: '100%' }}
                      value={appt.condition_status}
                      onChange={v => updateBozhuAppt(idx, 'condition_status', v)}
                      options={[{ label: '稳定', value: '稳定' }, { label: '不稳定', value: '不稳定' }]}
                    />
                  </Col>
                  <Col span={5}>
                    <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>阶段</div>
                    <Select
                      size="small"
                      style={{ width: '100%' }}
                      value={appt.treatment_phase}
                      onChange={v => updateBozhuAppt(idx, 'treatment_phase', v)}
                      options={[{ label: '强化期', value: '强化期' }, { label: '巩固期', value: '巩固期' }, { label: '维持期', value: '维持期' }]}
                    />
                  </Col>
                </Row>
              </div>
            ))}
            <Button
              type="dashed"
              block
              style={{ marginTop: 4 }}
              onClick={() => {
                const last = bozhuAppts[bozhuAppts.length - 1];
                if (last) {
                  const lastCount = last.injection_count || 0;
                  const nextCount = lastCount + 1;
                  const base = getNextAppointmentDate(
                    last.appointment_date ? dayjs(last.appointment_date) : dayjs(),
                    nextCount,
                    injectionIntervalFirst4
                  );
                  const nextDate = getNearestInjectionDate(base, injectionWeekdays);
                  setBozhuAppts(prev => [...prev, {
                    injection_count: nextCount,
                    appointment_date: nextDate,
                    follow_up_date: nextDate,
                    treatment_phase: nextCount > 4 ? '巩固期' : '强化期',
                    time_slot: '上午',
                    condition_status: '稳定',
                  }]);
                } else {
                  const nextDate = getNearestInjectionDate(dayjs(), injectionWeekdays);
                  setBozhuAppts(prev => [...prev, {
                    injection_count: 1,
                    appointment_date: nextDate,
                    follow_up_date: nextDate,
                    treatment_phase: '强化期',
                    time_slot: '上午',
                    condition_status: '稳定',
                  }]);
                }
              }}
            >
              + 添加玻注预约日期
            </Button>
          </>
        )}

        {activeTab === 'peri' && (
          <div style={{ background: '#fafafa', borderRadius: 8, padding: '10px 16px', border: '1px solid #e8e8e8' }}>
            <Row gutter={12} align="middle">
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>玻注日期</div>
                <DatePicker
                  size="small"
                  style={{ width: '100%' }}
                  value={periAppt.appointment_date ? dayjs(periAppt.appointment_date) : undefined}
                  onChange={v => updatePeriAppt('appointment_date', v)}
                />
              </Col>
              <Col span={4}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>时间段</div>
                <Select
                  size="small"
                  style={{ width: '100%' }}
                  value={periAppt.time_slot}
                  onChange={v => updatePeriAppt('time_slot', v)}
                  options={[{ label: '上午', value: '上午' }, { label: '下午', value: '下午' }]}
                />
              </Col>
              <Col span={4}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>针次</div>
                <InputNumber
                  size="small"
                  min={1}
                  style={{ width: '100%' }}
                  value={periAppt.injection_count}
                  onChange={v => updatePeriAppt('injection_count', v)}
                />
              </Col>
              <Col span={4}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>状况</div>
                <Select
                  size="small"
                  style={{ width: '100%' }}
                  value={periAppt.condition_status}
                  onChange={v => updatePeriAppt('condition_status', v)}
                  options={[{ label: '稳定', value: '稳定' }, { label: '不稳定', value: '不稳定' }]}
                />
              </Col>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>阶段</div>
                <Select
                  size="small"
                  style={{ width: '100%' }}
                  value={periAppt.treatment_phase}
                  onChange={v => updatePeriAppt('treatment_phase', v)}
                  options={[{ label: '围手术期', value: '围手术期' }, { label: '强化期', value: '强化期' }, { label: '巩固期', value: '巩固期' }]}
                />
              </Col>
            </Row>
          </div>
        )}

        <div style={{ marginTop: 16, display: 'flex', justifyContent: 'center', gap: 12 }}>
          <Button
            type="primary"
            size="large"
            icon={<CheckCircleOutlined />}
            loading={saving}
            onClick={handleSave}
            style={{ borderRadius: 8, height: 44, padding: '0 32px' }}
          >
            确认预约
          </Button>
          <Button
            size="large"
            icon={<PrinterOutlined />}
            loading={printSaving}
            onClick={handleSaveAndPrint}
            style={{ borderRadius: 8, height: 44, padding: '0 32px', borderColor: colors.blue, color: colors.blue }}
          >
            打印预约单
          </Button>
        </div>
      </div>
    </div>
  );
};

export default EmbedAppointment;
