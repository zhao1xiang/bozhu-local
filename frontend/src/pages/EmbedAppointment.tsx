import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Select, DatePicker, InputNumber, Button,
  Row, Col, message, Spin, Alert, Tabs,
} from 'antd';
import { CheckCircleOutlined, PrinterOutlined, CloseOutlined } from '@ant-design/icons';
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
  is_new?: boolean;
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
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [printSaving, setPrintSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [activeTab, setActiveTab] = useState<string>('bozhu');
  const [savedOk, setSavedOk] = useState(false);
  const [printPhoneNumber, setPrintPhoneNumber] = useState<string>('');
  const [hasHistory, setHasHistory] = useState(false);
  const [successPage, setSuccessPage] = useState<'save' | 'print' | null>(null);

  const [bozhuAppts, setBozhuAppts] = useState<AppItem[]>([
    { injection_count: 1 },
    { injection_count: 2 },
    { injection_count: 3 },
    { injection_count: 4 },
  ]);
  const [periAppt, setPeriAppt] = useState<AppItem>({ injection_count: 1 });

  const [injectionWeekdays, setInjectionWeekdays] = useState<string[]>(['1']);
  const [injectionIntervalFirst4, setInjectionIntervalFirst4] = useState<number>(30);
  const [diagnoses, setDiagnoses] = useState<{label:string;value:string}[]>([]);
  const [drugs, setDrugs] = useState<{label:string;value:string}[]>([]);

  useEffect(() => {
    const dataParam = searchParams.get('data');
    const signParam = searchParams.get('sign');
    if (!dataParam || !signParam) {
      setError('缺少必要参数：data 或 sign');
      setLoading(false);
      return;
    }
    // 预加载打印模板和二维码图片，确保打印时已缓存
    fetch(`/print-template.html?t=${Date.now()}`).catch(() => {});
    const preloadImg = new Image();
    preloadImg.src = '/qrcode.png';
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

      // 获取复诊提醒电话
      apiClient.get('/system-settings/print_phone_number').then(r => setPrintPhoneNumber(r.data?.value || '')).catch(() => {});

      // 获取诊断和药物数据字典
      apiClient.get('/data-dictionary', { params: { category: 'diagnosis' } }).then(r => {
        setDiagnoses((r.data || []).filter((d: any) => d.is_active).map((d: any) => ({ label: d.label, value: d.value })));
      }).catch(() => {});
      apiClient.get('/data-dictionary', { params: { category: 'drug' } }).then(r => {
        setDrugs((r.data || []).filter((d: any) => d.is_active).map((d: any) => ({ label: d.label, value: d.value })));
      }).catch(() => {});

      const { patient, appointments, payload } = verifyRes.data;

      const cleanVal = (v: any) => (!v || v === '无' || v === 'null' || v === 'undefined') ? '' : String(v).trim();
      const eyeRaw = cleanVal(payload?.eye);

      const pd: PatientData = {
        id: patient?.id,
        name: cleanVal(payload?.name) || payload?.name,
        outpatient_number: payload?.outpatient_number,
        phone: cleanVal(payload?.phone) || undefined,
        diagnosis: cleanVal(payload?.diagnosis) || undefined,
        drug_name: cleanVal(payload?.drug_name) || undefined,
        eye: eyeRaw === '' ? '双眼' : eyeRaw,
        injection_count: typeof payload?.injection_count === 'number' ? payload.injection_count : (parseInt(payload?.injection_count) || 0),
        doctor: cleanVal(payload?.doctor) || undefined,
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

        if (bozhuList.length > 0) {
          // 有历史记录：只显示下一针（最大针次 + 1）
          setHasHistory(true);
          const maxCount = Math.max(...bozhuList.map((a: any) => a.injection_count || 0));
          const nextCount = maxCount + 1;
          const lastAppt = bozhuList[bozhuList.length - 1];
          const base = getNextAppointmentDate(
            lastAppt.appointment_date ? dayjs(lastAppt.appointment_date) : dayjs(),
            nextCount,
            interval
          );
          const nextDate = getNearestInjectionDate(base, wd);
          setBozhuAppts([{
            injection_count: nextCount,
            appointment_date: nextDate,
            follow_up_date: nextDate,
            treatment_phase: nextCount > 4 ? '巩固期' : '强化期',
            time_slot: '上午',
            condition_status: '稳定',
          }]);
        } else {
          setBozhuAppts([{ injection_count: 1 }, { injection_count: 2 }, { injection_count: 3 }, { injection_count: 4 }]);
        }

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
        const startCount = (pd.injection_count || 0) + 1;
        if (startCount > 1) {
          // 传入了 injection_count，从下一针开始生成
          if (startCount <= 4) {
            // 强化期内：生成从 startCount 到第4针的多条预约
            const appts: AppItem[] = [];
            let currentBase = dayjs();
            for (let cnt = startCount; cnt <= 4; cnt++) {
              const date = getNearestInjectionDate(currentBase, wd);
              appts.push({
                injection_count: cnt,
                appointment_date: date,
                follow_up_date: date,
                treatment_phase: '强化期',
                time_slot: '上午',
                condition_status: '稳定',
              });
              currentBase = getNextAppointmentDate(date, cnt + 1, interval);
            }
            setBozhuAppts(appts);
          } else {
            // 强化期后：只生成下一针
            const base = getNextAppointmentDate(dayjs(), startCount, interval);
            const nextDate = getNearestInjectionDate(base, wd);
            setBozhuAppts([{
              injection_count: startCount,
              appointment_date: nextDate,
              follow_up_date: nextDate,
              treatment_phase: '巩固期',
              time_slot: '上午',
              condition_status: '稳定',
            }]);
          }
        } else {
          const generated = generateDates(wd, interval);
          setBozhuAppts(generated);
        }
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
      navigate('/embed/success');
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
      renderAndPrint(saveRes.data?.patient, saveRes.data?.appointments || []);
      navigate('/embed/success');
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '保存失败，请重试');
    } finally {
      setPrintSaving(false);
    }
  };

  const renderAndPrint = (patient: any, appts: any[], onDone?: () => void) => {
    // ============================================================
    // 切换打印模式：true = HTML模板，false = 图片覆盖文字
    // ============================================================
    const USE_HTML_TEMPLATE = true;

    const sorted = [...(Array.isArray(appts) ? appts : [])].sort((a, b) => (a.injection_count || 0) - (b.injection_count || 0));
    const getApptByCount = (cnt: number) => sorted.find(a => a.injection_count === cnt);
    const fmtDate = (d?: string) => d ? dayjs(d).format('YYYY年M月D日') : '';
    const pd = patientData;

    if (USE_HTML_TEMPLATE) {
      const getStable = (n: number) => {
        const a = getApptByCount(n);
        if (!a?.appointment_date) return '';
        return (a.condition_status === '趋差' || a.condition_status === '不稳定') ? '' : fmtDate(a.appointment_date);
      };
      const getUnstable = (n: number) => {
        const a = getApptByCount(n);
        if (!a?.appointment_date) return '';
        return (a.condition_status === '趋差' || a.condition_status === '不稳定') ? fmtDate(a.appointment_date) : '';
      };
      fetch(`/print-template.html?t=${Date.now()}`).then(r => r.text()).then(html => {
        // 把相对路径图片替换为绝对 URL，解决打印时无法加载相对路径的问题
        html = html.replace(/src="(?!http|data:)([^"]+)"/g, `src="${window.location.origin}/$1"`);
        html = html
          .replace('{{姓名}}', pd?.name || '')
          .replace('{{联系方式}}', pd?.phone || '')
          .replace('{{左眼勾}}', (pd?.eye === '左眼' || pd?.eye === '双眼') ? '✓' : '')
          .replace('{{右眼勾}}', (pd?.eye === '右眼' || pd?.eye === '双眼') ? '✓' : '')
          .replace('{{诊断}}', pd?.diagnosis || '')
          .replace('{{治疗药物}}', pd?.drug_name || '')
          .replace('{{视力}}', '')
          .replace('{{医生}}', sorted[0]?.doctor || pd?.doctor || '')
          .replace('{{复诊电话}}', printPhoneNumber)
          .replace('{{第1次}}', fmtDate(getApptByCount(1)?.appointment_date))
          .replace('{{第2次}}', fmtDate(getApptByCount(2)?.appointment_date))
          .replace('{{第3次}}', fmtDate(getApptByCount(3)?.appointment_date))
          .replace('{{第4次}}', fmtDate(getApptByCount(4)?.appointment_date))
          .replace('{{第5次稳定}}', getStable(5)).replace('{{第6次稳定}}', getStable(6))
          .replace('{{第7次稳定}}', getStable(7)).replace('{{第8次稳定}}', getStable(8))
          .replace('{{第9次稳定}}', getStable(9))
          .replace('{{第5次不稳定}}', getUnstable(5)).replace('{{第6次不稳定}}', getUnstable(6))
          .replace('{{第7次不稳定}}', getUnstable(7)).replace('{{第8次不稳定}}', getUnstable(8))
          .replace('{{第9次不稳定}}', getUnstable(9));

        // 用 iframe 加载完整 HTML，等 onload 后打印，确保图片渲染完成
        document.getElementById('html-print-iframe')?.remove();
        const iframe = document.createElement('iframe');
        iframe.id = 'html-print-iframe';
        iframe.style.cssText = 'position:fixed;left:0;top:0;width:100%;height:100%;border:none;z-index:99999;background:white;';
        document.body.appendChild(iframe);
        iframe.onload = () => {
          const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
          const imgs = iframeDoc ? Array.from(iframeDoc.querySelectorAll('img')) as HTMLImageElement[] : [];
          const waitAll = imgs.map(img => new Promise<void>(resolve => {
            if (img.complete && img.naturalWidth > 0) { resolve(); return; }
            img.onload = () => resolve();
            img.onerror = () => resolve();
          }));
          Promise.all(waitAll).then(() => {
            iframe.contentWindow?.print();
            onDone?.();
            setTimeout(() => { document.getElementById('html-print-iframe')?.remove(); }, 1000);
          });
        };
        iframe.srcdoc = html;
      }).catch(() => message.error('加载打印模板失败'));
      return;
    }

    // ===== 图片覆盖文字打印（保留，切换 USE_HTML_TEMPLATE=false 即可恢复）=====
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
        .overlay-text.ot-name, .overlay-text.ot-phone, .overlay-text.ot-doctor, .overlay-text.ot-clinicphone { font-size: 22.7px !important; }
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
      .overlay-text.ot-name, .overlay-text.ot-phone, .overlay-text.ot-doctor, .overlay-text.ot-clinicphone { font-size: 22.7px !important; }
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
        <span class="overlay-text ot-phone" style="top:19%;left:51.9%">${pd?.phone || ''}</span>
        ${(pd?.eye === '左眼' || pd?.eye === '双眼') ? '<span class="overlay-text ot-checkmark" style="top:19%;left:73%">✓</span>' : ''}
        ${(pd?.eye === '右眼' || pd?.eye === '双眼') ? '<span class="overlay-text ot-checkmark" style="top:19%;left:86%">✓</span>' : ''}
        <span class="overlay-text ot-diagnosis" style="top:23.3%;left:16%">${pd?.diagnosis || ''}</span>
        <span class="overlay-text ot-drug" style="top:23.5%;left:51%">${pd?.drug_name || ''}</span>
        <span class="overlay-text ot-doctor" style="top:26.5%;left:16%">${sorted[0]?.doctor || pd?.doctor || ''}</span>
        ${printPhoneNumber ? `<span class="overlay-text ot-clinicphone" style="top:26.5%;left:63%">${printPhoneNumber}</span>` : ''}
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

        {/* 患者信息表单 */}
        {patientData && (
          <div style={{ background: '#f8faff', borderRadius: 8, padding: '12px 16px', marginBottom: 12, border: '1px solid #d6e4ff' }}>
            <div style={{ fontSize: 13, fontWeight: 'bold', color: colors.blue, marginBottom: 8 }}>患者信息</div>
            <Row gutter={12}>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>姓名</div>
                <input style={{ width: '100%', border: '1px solid #d9d9d9', borderRadius: 4, padding: '3px 8px', fontSize: 13 }}
                  value={patientData.name || ''} onChange={e => setPatientData(prev => ({ ...prev, name: e.target.value }))} />
              </Col>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>联系方式</div>
                <input style={{ width: '100%', border: '1px solid #d9d9d9', borderRadius: 4, padding: '3px 8px', fontSize: 13 }}
                  value={patientData.phone || ''} onChange={e => setPatientData(prev => ({ ...prev, phone: e.target.value }))} />
              </Col>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>诊断</div>
                <Select
                  size="small"
                  style={{ width: '100%' }}
                  value={patientData.diagnosis || undefined}
                  placeholder="请选择诊断"
                  onChange={v => setPatientData(prev => ({ ...prev, diagnosis: v }))}
                  options={[
                    ...(patientData.diagnosis && !diagnoses.find(d => d.value === patientData.diagnosis)
                      ? [{ label: patientData.diagnosis, value: patientData.diagnosis }] : []),
                    ...diagnoses,
                  ]}
                  showSearch
                  filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())}
                  allowClear
                />
              </Col>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>用药</div>
                <Select
                  size="small"
                  style={{ width: '100%' }}
                  value={patientData.drug_name || undefined}
                  placeholder="请选择药物"
                  onChange={v => setPatientData(prev => ({ ...prev, drug_name: v }))}
                  options={[
                    ...(patientData.drug_name && !drugs.find(d => d.value === patientData.drug_name)
                      ? [{ label: patientData.drug_name, value: patientData.drug_name }] : []),
                    ...drugs,
                  ]}
                  showSearch
                  filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())}
                  allowClear
                />
              </Col>
            </Row>
            <Row gutter={12} style={{ marginTop: 8 }}>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>治疗眼</div>
                <Select
                  size="small"
                  style={{ width: '100%' }}
                  value={patientData.eye || '双眼'}
                  onChange={v => setPatientData(prev => ({ ...prev, eye: v }))}
                  options={[
                    { label: '左眼', value: '左眼' },
                    { label: '右眼', value: '右眼' },
                    { label: '双眼', value: '双眼' },
                  ]}
                />
              </Col>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>注药医生</div>
                <input style={{ width: '100%', border: '1px solid #d9d9d9', borderRadius: 4, padding: '3px 8px', fontSize: 13 }}
                  value={patientData.doctor || ''} onChange={e => setPatientData(prev => ({ ...prev, doctor: e.target.value }))} />
              </Col>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>住院号</div>
                <input style={{ width: '100%', border: '1px solid #d9d9d9', borderRadius: 4, padding: '3px 8px', fontSize: 13 }}
                  value={patientData.outpatient_number || ''} onChange={e => setPatientData(prev => ({ ...prev, outpatient_number: e.target.value }))} />
              </Col>
              <Col span={6}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>已完成针数</div>
                <InputNumber 
                  style={{ width: '100%' }}
                  min={0}
                  value={patientData.injection_count || 0}
                  onChange={v => {
                    const oldCount = patientData.injection_count || 0;
                    const newCount = v || 0;
                    setPatientData(prev => ({ ...prev, injection_count: newCount }));
                    
                    // 如果针数改变，重新生成预约
                    if (newCount !== oldCount) {
                      const startCount = newCount + 1;
                      if (startCount > 1) {
                        if (startCount <= 4) {
                          const appts: AppItem[] = [];
                          let currentBase = dayjs();
                          for (let cnt = startCount; cnt <= 4; cnt++) {
                            const date = getNearestInjectionDate(currentBase, injectionWeekdays);
                            appts.push({
                              injection_count: cnt,
                              appointment_date: date,
                              follow_up_date: date,
                              treatment_phase: '强化期',
                              time_slot: '上午',
                              condition_status: '稳定',
                            });
                            currentBase = getNextAppointmentDate(date, cnt + 1, injectionIntervalFirst4);
                          }
                          setBozhuAppts(appts);
                        } else {
                          const base = getNextAppointmentDate(dayjs(), startCount, injectionIntervalFirst4);
                          const nextDate = getNearestInjectionDate(base, injectionWeekdays);
                          setBozhuAppts([{
                            injection_count: startCount,
                            appointment_date: nextDate,
                            follow_up_date: nextDate,
                            treatment_phase: '巩固期',
                            time_slot: '上午',
                            condition_status: '稳定',
                          }]);
                        }
                      } else {
                        const generated = generateDates(injectionWeekdays, injectionIntervalFirst4);
                        setBozhuAppts(generated);
                      }
                    }
                  }}
                />
              </Col>
            </Row>
          </div>
        )}

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
              <div key={idx} style={{ background: '#fafafa', borderRadius: 8, padding: '10px 16px', marginBottom: 8, border: '1px solid #e8e8e8', position: 'relative' }}>
                {/* 右上角删除按钮：
                    - 新增的行（is_new=true）：总是显示删除按钮
                    - 初始自动生成的行：只有无历史记录且第3针及以后才显示
                */}
                {appt.is_new || (!hasHistory && (appt.injection_count || 0) >= 3) ? (
                 <Button
                  type="text"
                  icon={<CloseOutlined style={{ fontSize: 14 }} />}
                  onClick={() => setBozhuAppts(prev => prev.filter((_, i) => i !== idx))}
                  style={{ position: 'absolute', top: 2, right: 2, color: '#ff4d4f', zIndex: 10, width: 32, height: 32 }}
                />
                ) : null}
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
                  <Col span={4}>
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
            {/* 添加按钮 */}
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
                    is_new: true,
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
                    is_new: true,
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
          {activeTab === 'bozhu' ? (
            <>
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
            </>
          ) : (
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
          )}
        </div>
      </div>
    </div>
  );
};

export default EmbedAppointment;
