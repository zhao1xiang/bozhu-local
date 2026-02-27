import React, { useEffect, useState } from 'react';
import { Card, DatePicker, Table, Button, Tag, message, Space, Modal, Tabs, Form, Select, Input, Switch } from 'antd';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import { CheckOutlined, CloseOutlined, PrinterOutlined, EditOutlined } from '@ant-design/icons';
import { Appointment, Patient } from '@/types';
import { apiClient } from '@/api/client';
import { useNavigate } from 'react-router-dom';

const { RangePicker } = DatePicker;

const DailyWork: React.FC = () => {
  const navigate = useNavigate();
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([dayjs(), dayjs()]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);

  // Reminder state
  const [reminders, setReminders] = useState<any[]>([]); // Use any because we enriched it with call_result
  const [showAllReminders, setShowAllReminders] = useState(false);
  const [reminderLoading, setReminderLoading] = useState(false);
  const [callResultModalOpen, setCallResultModalOpen] = useState(false);
  const [currentReminder, setCurrentReminder] = useState<Appointment | null>(null);
  const [callForm] = Form.useForm();

  // Reschedule state
  const [rescheduleModalOpen, setRescheduleModalOpen] = useState(false);
  const [currentReschedule, setCurrentReschedule] = useState<Appointment | null>(null);
  const [rescheduleForm] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    try {
      const startDate = dateRange[0].format('YYYY-MM-DD');
      const endDate = dateRange[1].format('YYYY-MM-DD');
      const [patientsRes, appointmentsRes] = await Promise.all([
        apiClient.get<Patient[]>('/patients'),
        apiClient.get<Appointment[]>('/appointments', {
          params: {
            start_date: startDate,
            end_date: endDate
          }
        })
      ]);
      setPatients(patientsRes.data);
      setAppointments(appointmentsRes.data);
    } catch (error) {
      console.error(error);
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchReminders = async () => {
    setReminderLoading(true);
    try {
      const response = await apiClient.get<any[]>('/follow-ups/reminders');
      setReminders(response.data);
    } catch (error) {
      console.error(error);
      message.error('获取提醒列表失败');
    } finally {
      setReminderLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchReminders();
  }, [dateRange]);

  const handleStatusUpdate = async (record: Appointment, status: string) => {
    try {
      const payload = {
        patient_id: record.patient_id,
        status: status,
        injection_number: record.injection_number,
        injection_count: record.injection_count,
        eye: record.eye,
        drug_name: record.drug_name,
        cost_type: record.cost_type,
        doctor: record.doctor,
        notes: record.notes
      };

      await apiClient.patch(`/appointments/${record.id}`, payload);
      message.success('状态更新成功');
      fetchData();
    } catch (error) {
      console.error(error);
      message.error('更新失败');
    }
  };

  const handlePrintClick = (record: Appointment) => {
    navigate(`/app/print-center?patient_id=${record.patient_id}`);
  };


  const openCallResultModal = (record: Appointment) => {
    setCurrentReminder(record);
    callForm.resetFields();
    setCallResultModalOpen(true);
  };

  const handleCallResultSubmit = async () => {
    try {
      const values = await callForm.validateFields();
      if (currentReminder) {
        await apiClient.post('/follow-ups/record', {
          appointment_id: currentReminder.id,
          patient_id: currentReminder.patient_id,
          status: values.status,
          notes: values.notes
        });
        message.success('记录成功');
        setCallResultModalOpen(false);
        fetchReminders(); // Refresh list to update status
      }
    } catch (error) {
      console.error(error);
      message.error('操作失败');
    }
  };

  const openRescheduleModal = (record: Appointment) => {
    setCurrentReschedule(record);
    rescheduleForm.setFieldsValue({
      appointment_date: record.appointment_date ? dayjs(record.appointment_date) : null,
      follow_up_date: record.follow_up_date ? dayjs(record.follow_up_date) : null,
    });
    setRescheduleModalOpen(true);
  };

  const handleRescheduleSubmit = async () => {
    try {
      const values = await rescheduleForm.validateFields();
      if (currentReschedule) {
        const payload = {
          patient_id: currentReschedule.patient_id,
          appointment_date: values.appointment_date ? values.appointment_date.format('YYYY-MM-DD') : currentReschedule.appointment_date,
          follow_up_date: values.follow_up_date ? values.follow_up_date.format('YYYY-MM-DD') : currentReschedule.follow_up_date,
          status: currentReschedule.status,
          injection_number: currentReschedule.injection_number,
          injection_count: currentReschedule.injection_count,
          eye: currentReschedule.eye,
          drug_name: currentReschedule.drug_name,
          cost_type: currentReschedule.cost_type,
          doctor: currentReschedule.doctor,
          treatment_phase: currentReschedule.treatment_phase,
          notes: currentReschedule.notes
        };

        await apiClient.patch(`/appointments/${currentReschedule.id}`, payload);
        message.success('预约时间修改成功');
        setRescheduleModalOpen(false);
        fetchData(); // Refresh list
      }
    } catch (error) {
      console.error(error);
      message.error('修改失败');
    }
  };

  const columns = [
    {
      title: '玻注日期',
      dataIndex: 'appointment_date',
      render: (text: string) => text ? dayjs(text).format('YYYY-MM-DD') : '-'
    },
    {
      title: '注药号',
      dataIndex: 'injection_number',
    },
    {
      title: '患者',
      dataIndex: 'patient_id',
      render: (id: string) => {
        const p = patients.find(p => p.id === id);
        return p ? `${p.name} (${p.phone || '-'})` : id;
      }
    },
    { title: '药品', dataIndex: 'drug_name' },
    { title: '眼别', dataIndex: 'eye' },
    { title: '医生', dataIndex: 'doctor' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: string) => {
        let color = 'default';
        let text = '未知';
        switch (status) {
          case 'scheduled': color = 'processing'; text = '待执行'; break;
          case 'confirmed': color = 'success'; text = '已确认'; break;
          case 'completed': color = 'green'; text = '已完成'; break;
          case 'cancelled': color = 'error'; text = '已取消'; break;
        }
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          {record.status !== 'completed' && record.status !== 'cancelled' && (
            <>
              <Button
                type="primary"
                size="small"
                icon={<CheckOutlined />}
                onClick={() => handleStatusUpdate(record, 'completed')}
              >
                完成
              </Button>
              <Button
                danger
                size="small"
                icon={<CloseOutlined />}
                onClick={() => handleStatusUpdate(record, 'cancelled')}
              >
                取消
              </Button>
            </>
          )}
          <Button
            size="small"
            icon={<PrinterOutlined />}
            onClick={() => handlePrintClick(record)}
          >
            打印
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => openRescheduleModal(record)}
          >
            修改预约时间
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="每日工作">
        <Tabs items={[
          {
            key: 'daily',
            label: '今日预约',
            children: (
              <div>
                <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
                  <RangePicker
                    value={dateRange}
                    onChange={(dates) => dates && setDateRange([dates[0]!, dates[1]!])}
                    allowClear={false}
                    format="YYYY-MM-DD"
                  />
                </div>
                <Table
                  dataSource={appointments}
                  columns={columns}
                  rowKey="id"
                  loading={loading}
                  pagination={false}
                />
              </div>
            )
          },
          {
            key: 'reminders',
            label: '复诊提醒',
            children: (
              <div>
                <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
                  <Space>
                    <Switch
                      checkedChildren="显示全部"
                      unCheckedChildren="仅显示未拨打"
                      checked={showAllReminders}
                      onChange={setShowAllReminders}
                    />
                  </Space>
                  <Button onClick={fetchReminders}>刷新</Button>
                </div>
                <Table
                  dataSource={reminders.filter(r => showAllReminders || !r.call_result)}
                  rowKey="id"
                  loading={reminderLoading}
                  pagination={false}
                  columns={[
                    {
                      title: '患者',
                      dataIndex: 'patient_id',
                      render: (id) => {
                        const p = patients.find(p => p.id === id);
                        return p ? `${p.name} (${p.phone || '-'})` : id;
                      }
                    },
                    {
                      title: '复诊日期',
                      dataIndex: 'follow_up_date',
                      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-'
                    },
                    {
                      title: '随访结果',
                      dataIndex: 'call_result',
                      render: (text) => {
                        if (!text) return <Tag>未拨打</Tag>;
                        const map: Record<string, any> = {
                          'confirmed': { color: 'success', text: '确认复诊' },
                          'rescheduled': { color: 'warning', text: '已改期' },
                          'no_answer': { color: 'error', text: '无人接听' },
                          'refused': { color: 'default', text: '拒绝/取消' },
                        };
                        const config = map[text] || { color: 'default', text: text };
                        return <Tag color={config.color}>{config.text}</Tag>;
                      }
                    },
                    {
                      title: '操作',
                      render: (_, record) => (
                        <Button size="small" onClick={() => openCallResultModal(record)}>
                          {record.call_result ? '更新结果' : '记录电话结果'}
                        </Button>
                      )
                    }
                  ]}
                />
              </div>
            )
          }
        ]} />
      </Card>


      <Modal
        title="记录电话随访结果"
        open={callResultModalOpen}
        onOk={handleCallResultSubmit}
        onCancel={() => setCallResultModalOpen(false)}
      >
        <Form form={callForm} layout="vertical">
          <Form.Item name="status" label="随访结果" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="confirmed">确认按时复诊</Select.Option>
              <Select.Option value="rescheduled">改期</Select.Option>
              <Select.Option value="no_answer">无人接听</Select.Option>
              <Select.Option value="refused">拒绝/取消</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="修改预约时间"
        open={rescheduleModalOpen}
        onOk={handleRescheduleSubmit}
        onCancel={() => setRescheduleModalOpen(false)}
      >
        <Form form={rescheduleForm} layout="vertical">
          <Form.Item name="appointment_date" label="玻注日期" rules={[{ required: true, message: '请选择玻注日期' }]}>
            <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="follow_up_date" label="复诊日期">
            <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DailyWork;
