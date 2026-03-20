import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import {
  TeamOutlined, MedicineBoxOutlined, CalendarOutlined,
  BellOutlined, LineChartOutlined, SafetyOutlined
} from '@ant-design/icons';
import { apiClient } from '@/api/client';

const C = {
  purple: '#7b2cbf',
  purpleLight: '#9d4edd',
  purpleSoft: '#c77dff',
  text1: '#2d1b4d',
  text2: '#5c4d7d',
  gridLine: 'rgba(123, 44, 191, 0.08)',
  border: 'rgba(123, 44, 191, 0.15)',
};

function useCountUp(target: number, duration = 900) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (target === 0) { setValue(0); return; }
    const start = Date.now();
    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(target * ease));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [target]);
  return value;
}

const KpiCard: React.FC<{
  icon: React.ReactNode; label: string; value: number;
  suffix?: string; iconBg?: string; iconColor?: string;
}> = ({ icon, label, value, suffix = '', iconBg = 'rgba(123,44,191,0.1)', iconColor = C.purple }) => {
  const display = useCountUp(value);
  return (
    <div style={{
      background: '#fff', border: '1px solid rgba(0,0,0,0.06)', borderRadius: 12,
      boxShadow: '0 2px 8px rgba(0,0,0,0.05)', padding: '10px 14px',
      display: 'flex', alignItems: 'center', gap: 12, flex: 1,
      cursor: 'default', transition: 'box-shadow 0.2s',
    }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10, background: iconBg,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        fontSize: 18, color: iconColor,
      }}>
        {icon}
      </div>
      <div>
        <div style={{ fontSize: 11, color: C.text2, marginBottom: 3 }}>{label}</div>
        <div style={{ fontFamily: 'monospace', fontSize: 22, fontWeight: 700, color: C.text1, lineHeight: 1 }}>
          {display}{suffix}
        </div>
      </div>
    </div>
  );
};

const GlassCard: React.FC<{ title: string; children: React.ReactNode; style?: React.CSSProperties; extra?: React.ReactNode }> = ({ title, children, style, extra }) => (
  <div style={{
    background: '#fff', border: '1px solid rgba(0,0,0,0.06)', borderRadius: 12,
    boxShadow: '0 2px 12px rgba(0,0,0,0.06)', padding: '14px 16px',
    display: 'flex', flexDirection: 'column', overflow: 'hidden', ...style
  }}>
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, flexShrink: 0 }}>
      <div style={{ fontSize: 13, fontWeight: 600, color: C.text2, display: 'flex', alignItems: 'center', gap: 7 }}>
        <span style={{ display: 'inline-block', width: 3, height: 14, background: C.purple, borderRadius: 2 }} />
        {title}
      </div>
      {extra}
    </div>
    {children}
  </div>
);

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({ total_patients: 0, total_injections: 0, today_appointments: 0, due_follow_ups: 0 });
  const [trendData, setTrendData] = useState<{ date: string; count: number }[]>([]);
  const [trendDim, setTrendDim] = useState<'month' | 'week'>('month');
  const [eyeData, setEyeData] = useState<{ name: string; value: number }[]>([]);
  const [diseaseData, setDiseaseData] = useState<{ name: string; value: number }[]>([]);
  const [doctorData, setDoctorData] = useState<{ name: string; value: number }[]>([]);
  const [rates, setRates] = useState({ 强化期: 0, 巩固期: 0 });

  const fetchTrend = async (dim: string) => {
    try {
      const res = await apiClient.get(`/dashboard/charts/trend?dimension=${dim}`);
      setTrendData(res.data || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    (async () => {
      try {
        const [statsRes, distRes, docRes, rateRes] = await Promise.all([
          apiClient.get('/dashboard/stats'),
          apiClient.get('/dashboard/charts/distribution'),
          apiClient.get('/dashboard/charts/doctors'),
          apiClient.get('/dashboard/charts/reinjection-rate'),
        ]);
        setStats(statsRes.data || {});
        setEyeData(distRes.data?.eyes || []);
        setDiseaseData(distRes.data?.diseases || []);
        setDoctorData(docRes.data || []);
        setRates(rateRes.data || { 强化期: 0, 巩固期: 0 });
        await fetchTrend('month');
      } catch (e) { console.error(e); }
    })();
  }, []);

  const donutOption = (value: number, color: string) => ({
    animation: true,
    series: [{
      type: 'pie', radius: ['58%', '76%'], silent: true, startAngle: 90,
      label: {
        show: true, position: 'center',
        formatter: `${value}%`,
        fontSize: 18, fontWeight: 700, fontFamily: 'monospace', color: C.text1
      },
      data: [
        { value, itemStyle: { color } },
        { value: 100 - value, itemStyle: { color: 'rgba(0,0,0,0.07)' } }
      ]
    }]
  });

  const trendOption = {
    animation: true,
    grid: { top: 16, left: 40, right: 16, bottom: 28 },
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: C.purple, textStyle: { color: C.text1, fontSize: 12 } },
    xAxis: {
      type: 'category', data: trendData.map(d => d.date),
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: C.text2, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: C.text2, fontSize: 11 },
      splitLine: { lineStyle: { color: C.gridLine } }
    },
    series: [{
      name: '注射量', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
      label: { show: true, position: 'top', fontSize: 11, color: C.text2 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(123,44,191,0.22)' }, { offset: 1, color: 'rgba(123,44,191,0)' }]
        }
      },
      lineStyle: { color: C.purple, width: 2.5 },
      itemStyle: { color: C.purple },
      data: trendData.map(d => d.count)
    }]
  };

  const pieColors = [C.purple, C.purpleLight, C.purpleSoft, '#e0aaff', '#6a0dad', '#5e19a6'];

  const eyeOption = {
    animation: true,
    legend: { bottom: 0, textStyle: { color: C.text2, fontSize: 11 }, icon: 'circle', itemWidth: 8, itemHeight: 8 },
    series: [{
      type: 'pie', radius: ['42%', '65%'], center: ['50%', '44%'],
      label: { show: true, fontSize: 11, color: C.text1, formatter: '{b}\n{d}%' },
      labelLine: { length: 8, length2: 6 },
      emphasis: { label: { fontSize: 13, fontWeight: 700 } },
      data: eyeData.map((d, i) => ({ ...d, itemStyle: { color: pieColors[i % pieColors.length] } }))
    }]
  };

  const diseaseOption = {
    animation: true,
    legend: { bottom: 0, textStyle: { color: C.text2, fontSize: 10 }, icon: 'circle', itemWidth: 8, itemHeight: 8, type: 'scroll' },
    series: [{
      type: 'pie', radius: ['42%', '65%'], center: ['50%', '44%'],
      label: { show: true, fontSize: 10, color: C.text1, formatter: '{b}\n{d}%' },
      labelLine: { length: 6, length2: 4 },
      emphasis: { label: { fontSize: 12, fontWeight: 700 } },
      data: diseaseData.map((d, i) => ({ ...d, itemStyle: { color: pieColors[i % pieColors.length] } }))
    }]
  };

  const doctorOption = doctorData.length > 0 ? {
    animation: true,
    grid: { top: 8, left: 72, right: 40, bottom: 8 },
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: C.purple, textStyle: { color: C.text1, fontSize: 12 } },
    xAxis: {
      type: 'value',
      axisLabel: { color: C.text2, fontSize: 10 },
      splitLine: { lineStyle: { color: C.gridLine } }
    },
    yAxis: {
      type: 'category',
      data: [...doctorData].reverse().map(d => d.name),
      axisLabel: { color: C.text2, fontSize: 11 },
      axisLine: { show: false }, axisTick: { show: false }
    },
    series: [{
      type: 'bar', barMaxWidth: 16,
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: C.purple }, { offset: 1, color: C.purpleSoft }] }
      },
      label: { show: true, position: 'right', fontSize: 11, color: C.text2 },
      data: [...doctorData].reverse().map(d => d.value)
    }]
  } : null;

  const trendExtra = (
    <div style={{ display: 'flex', gap: 4 }}>
      {(['month', 'week'] as const).map(dim => (
        <button key={dim} onClick={async () => { setTrendDim(dim); await fetchTrend(dim); }} style={{
          padding: '3px 10px', fontSize: 11, borderRadius: 6,
          border: `1px solid ${C.border}`, cursor: 'pointer',
          background: trendDim === dim ? C.purple : '#fff',
          color: trendDim === dim ? '#fff' : C.text2,
          fontFamily: 'inherit', transition: 'all 0.2s',
        }}>
          {dim === 'month' ? '按月' : '按周'}
        </button>
      ))}
    </div>
  );

  return (
    <div style={{
      width: '100%', height: '100%', display: 'flex', flexDirection: 'column',
      padding: '16px 20px', gap: 12, background: '#fdfbff', boxSizing: 'border-box',
      backgroundImage: 'radial-gradient(circle at 15% 10%, rgba(123,44,191,0.05) 0%, transparent 45%), radial-gradient(circle at 85% 90%, rgba(157,78,221,0.04) 0%, transparent 45%)',
    }}>

      {/* KPI 行 */}
      <div style={{ display: 'flex', gap: 10, flexShrink: 0 }}>
        <KpiCard icon={<TeamOutlined />} label="累计患者数" value={stats.total_patients} />
        <KpiCard icon={<MedicineBoxOutlined />} label="累计完成注药" value={stats.total_injections} />
        <KpiCard icon={<CalendarOutlined />} label="今日预约" value={stats.today_appointments} iconBg="rgba(157,78,221,0.1)" iconColor={C.purpleLight} />
        <KpiCard icon={<BellOutlined />} label="复诊提醒" value={stats.due_follow_ups} iconBg="rgba(217,79,53,0.1)" iconColor="#d94f35" />
        <KpiCard icon={<LineChartOutlined />} label="强化期约针率" value={rates.强化期} suffix="%" />
        <KpiCard icon={<SafetyOutlined />} label="巩固期约针率" value={rates.巩固期} suffix="%" iconBg="rgba(199,125,255,0.15)" iconColor={C.purpleSoft} />
      </div>

      {/* 中间行 */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 12, flex: 1, minHeight: 0 }}>
        <GlassCard title="医院整体 DOT（约针率）">
          <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', flex: 1, minHeight: 0 }}>
            {[
              { label: '四针率', value: rates.强化期, color: C.purple },
              { label: '五针率', value: Math.round((rates.强化期 + rates.巩固期) / 2), color: C.purpleLight },
              { label: '六针率', value: rates.巩固期, color: C.purpleSoft },
            ].map(item => (
              <div key={item.label} style={{ textAlign: 'center' }}>
                <ReactECharts option={donutOption(item.value, item.color)} style={{ width: 130, height: 130 }} />
                <div style={{ fontSize: 12, color: C.text2, marginTop: 4 }}>{item.label}</div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard title="医生工作量 Top 10">
          {doctorOption
            ? <ReactECharts option={doctorOption} style={{ flex: 1, minHeight: 0, height: '100%' }} />
            : <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.text2, fontSize: 13 }}>暂无数据</div>
          }
        </GlassCard>
      </div>

      {/* 底部行 */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 12, flex: 1, minHeight: 0 }}>
        <GlassCard title="注射量趋势" extra={trendExtra}>
          <ReactECharts option={trendOption} style={{ flex: 1, minHeight: 0, height: '100%' }} />
        </GlassCard>

        <GlassCard title="眼别分布">
          {eyeData.length > 0
            ? <ReactECharts option={eyeOption} style={{ flex: 1, minHeight: 0, height: '100%' }} />
            : <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.text2, fontSize: 13 }}>暂无数据</div>
          }
        </GlassCard>

        <GlassCard title="病种分布">
          {diseaseData.length > 0
            ? <ReactECharts option={diseaseOption} style={{ flex: 1, minHeight: 0, height: '100%' }} />
            : <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.text2, fontSize: 13 }}>暂无数据</div>
          }
        </GlassCard>
      </div>
    </div>
  );
};

export default Dashboard;
