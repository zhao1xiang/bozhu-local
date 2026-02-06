import React, { useEffect, useState } from 'react';
import { UserOutlined, CalendarOutlined, CheckCircleOutlined, BellOutlined, HistoryOutlined, LineChartOutlined } from '@ant-design/icons';
import { Row, Col, Card, Statistic, Table, Tag, List, Tabs, Spin, Radio, Space } from 'antd';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, PieChart, Pie, Cell } from 'recharts';
import dayjs from 'dayjs';
import { apiClient } from '@/api/client';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_patients: 0,
    total_injections: 0,
    today_appointments: 0,
    due_follow_ups: 0
  });
  const [trendData, setTrendData] = useState([]);
  const [trendDimension, setTrendDimension] = useState<'month' | 'week'>('month');
  const [drugData, setDrugData] = useState([]);
  const [eyeData, setEyeData] = useState([]);
  const [diseaseData, setDiseaseData] = useState([]);
  const [doctorData, setDoctorData] = useState([]);
  const [reinjectionRates, setReinjectionRates] = useState({ 强化期: 0, 巩固期: 0 });

  const fetchTrendData = async (dim: string) => {
    try {
      const res = await apiClient.get(`/dashboard/charts/trend?dimension=${dim}`);
      setTrendData(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [statsRes, distRes, docRes, rateRes] = await Promise.all([
          apiClient.get('/dashboard/stats'),
          apiClient.get('/dashboard/charts/distribution'),
          apiClient.get('/dashboard/charts/doctors'),
          apiClient.get('/dashboard/charts/reinjection-rate')
        ]);

        setStats(statsRes.data);
        setDrugData(distRes.data.drugs);
        setEyeData(distRes.data.eyes);
        setDiseaseData(distRes.data.diseases);
        setDoctorData(docRes.data);
        setReinjectionRates(rateRes.data);

        await fetchTrendData(trendDimension);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleTrendDimensionChange = async (e: any) => {
    const dim = e.target.value;
    setTrendDimension(dim);
    await fetchTrendData(dim);
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 24 }}>管理工作台</h2>

      {/* KPI Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card bordered={false}>
            <Statistic
              title="累计及在管患者"
              value={stats.total_patients}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card bordered={false}>
            <Statistic
              title="累计完成注药"
              value={stats.total_injections}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card bordered={false}>
            <Statistic
              title="今日预约"
              value={stats.today_appointments}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card bordered={false}>
            <Statistic
              title="复诊提醒 (待办)"
              value={stats.due_follow_ups}
              prefix={<BellOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card bordered={false}>
            <Statistic
              title="强化期约针率"
              value={reinjectionRates.强化期}
              suffix="%"
              prefix={<LineChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ fontSize: 12, color: '#8c8c8c', marginTop: 8 }}>定义：强化期已注药患者中，已约/完成下一针的比例</div>
          </Card>
        </Col>
        <Col span={12}>
          <Card bordered={false}>
            <Statistic
              title="巩固期约针率"
              value={reinjectionRates.巩固期}
              suffix="%"
              prefix={<HistoryOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ fontSize: 12, color: '#8c8c8c', marginTop: 8 }}>定义：巩固期已注药患者中，已约/完成下一针的比例</div>
          </Card>
        </Col>
      </Row>

      {/* Charts Row 1: Trend & Doctor Workload */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card
            title={`注药量趋势 (${trendDimension === 'month' ? '月度' : '周度'})`}
            bordered={false}
            extra={
              <Radio.Group value={trendDimension} onChange={handleTrendDimensionChange} size="small">
                <Radio.Button value="month">按月</Radio.Button>
                <Radio.Button value="week">按周</Radio.Button>
              </Radio.Group>
            }
          >
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#8884d8" fill="#8884d8" name="注药量" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="医生工作量 (Top 10)" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={doctorData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={80} />
                <Tooltip />
                <Bar dataKey="value" fill="#82ca9d" name="注药人次" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Charts Row 2: Distributions */}
      <Row gutter={16}>
        <Col span={8}>
          <Card title="药品使用分布" bordered={false}>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={drugData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {drugData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="眼别分布" bordered={false}>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={eyeData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#82ca9d"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {eyeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="疾病类型分布" bordered={false}>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={diseaseData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#ffc658"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {diseaseData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
