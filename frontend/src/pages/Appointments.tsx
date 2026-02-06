import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Table, Badge, Modal, Form, Select, DatePicker, Input, message, Button, InputNumber, Radio, Row, Col, Card, Tag, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import { PlusOutlined, PrinterOutlined, CloseOutlined } from '@ant-design/icons';
import { Appointment, Patient, DataDictionaryItem } from '@/types';
import { apiClient } from '@/api/client';

const Appointments: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<DataDictionaryItem[]>([]);
  const [drugs, setDrugs] = useState<DataDictionaryItem[]>([]);
  const [costTypes, setCostTypes] = useState<DataDictionaryItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showBatchHint, setShowBatchHint] = useState(false);
  // 玻注日配置（1-7 表示周一到周日），默认周一
  const [injectionWeekdays, setInjectionWeekdays] = useState<string[]>(['1']);

  // 根据系统配置的玻注日，从给定日期开始向后寻找最近的一个玻注日
  const getNearestInjectionDate = (baseDate: Dayjs, weekdays: string[]): Dayjs => {
    if (!weekdays || weekdays.length === 0) {
      return baseDate;
    }

    const allowed = weekdays
      .map((w) => parseInt(w, 10))
      .filter((n) => !Number.isNaN(n));

    if (allowed.length === 0) {
      return baseDate;
    }

    // 理论上 7 天内一定能找到一个匹配的星期，这里给 14 天冗余
    for (let i = 0; i < 14; i++) {
      const candidate = baseDate.add(i, 'day');
      const day = candidate.day(); // 0-6，周日为 0
      const weekday = day === 0 ? 7 : day; // 转为 1-7
      if (allowed.includes(weekday)) {
        return candidate;
      }
    }

    return baseDate;
  };

  const startBatchGeneration = () => {
    const base = getNearestInjectionDate(dayjs(), injectionWeekdays);
    const batchList = [];
    for (let i = 0; i < 4; i++) {
      const monthBase = base.add(i, 'month');
      const date = getNearestInjectionDate(monthBase, injectionWeekdays);
      batchList.push({
        appointment_date: date,
        follow_up_date: date,
        injection_count: i + 1,
        treatment_phase: '强化期'
      });
    }
    form.setFieldsValue({ appointment_list: batchList });
    setShowBatchHint(false);
  };



  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();
  const drugName = Form.useWatch('drug_name', form);
  const injectionCount = Form.useWatch('injection_count', form);
  const appointmentDate = Form.useWatch('appointment_date', form);
  const [loading, setLoading] = useState(false);

  const fetchAppointments = async (filters: any = {}) => {
    setLoading(true);
    try {
      const params: any = { limit: 1000, ...filters };
      if (params.dateRange) {
        params.start_date = params.dateRange[0].format('YYYY-MM-DD');
        params.end_date = params.dateRange[1].format('YYYY-MM-DD');
        delete params.dateRange;
      }
      const response = await apiClient.get<Appointment[]>('/appointments', { params });
      setAppointments(response.data);
    } catch (error) {
      console.error(error);
      message.error('获取预约列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    const values = await searchForm.validateFields();
    fetchAppointments(values);
  };

  const handleReset = () => {
    searchForm.resetFields();
    fetchAppointments();
  };

  const fetchPatients = async () => {
    try {
      const response = await apiClient.get<Patient[]>('/patients');
      setPatients(response.data);
      return response.data;
    } catch (error) {
      console.error(error);
      return [];
    }
  };


  const fetchDoctors = async () => {
    try {
      const response = await apiClient.get<DataDictionaryItem[]>('/data-dictionary', {
        params: { category: 'doctor' }
      });
      setDoctors(response.data.filter(d => d.is_active));
    } catch (error) {
      console.error(error);
    }
  };

  const fetchDrugs = async () => {
    try {
      const response = await apiClient.get<DataDictionaryItem[]>('/data-dictionary', {
        params: { category: 'drug' }
      });
      setDrugs(response.data.filter(d => d.is_active));
    } catch (error) {
      console.error(error);
    }
  };

  const fetchCostTypes = async () => {
    try {
      const response = await apiClient.get<DataDictionaryItem[]>('/data-dictionary', {
        params: { category: 'cost_type' }
      });
      setCostTypes(response.data.filter(d => d.is_active));
    } catch (error) {
      console.error(error);
    }
  };

  // 获取系统配置的玻注日
  const fetchInjectionWeekdays = async () => {
    try {
      const response = await apiClient.get('/system-settings/injection_weekday');
      const rawValue = response.data?.value ?? '';
      const list = rawValue
        ? String(rawValue)
            .split(',')
            .map((v: string) => v.trim())
            .filter(Boolean)
        : [];
      setInjectionWeekdays(list.length ? list : ['1']);
    } catch (error) {
      console.error(error);
      // 如果还没有配置，默认周一
      setInjectionWeekdays(['1']);
    }
  };

  useEffect(() => {
    const init = async () => {
      const results = await Promise.all([
        fetchAppointments(),
        fetchPatients(),
        fetchDoctors(),
        fetchDrugs(),
        fetchCostTypes(),
        fetchInjectionWeekdays()
      ]);
      const patientData = results[1] as Patient[];

      const patientId = searchParams.get('patient_id');
      if (patientId) {
        handleAdd(patientId, patientData);
      }
    };
    init();
  }, [searchParams]);


  const handleAdd = (preSelectedPatientId?: string, patientsList?: Patient[]) => {
    form.resetFields();
    const now = dayjs();
    const firstInjectionDate = getNearestInjectionDate(now, injectionWeekdays);

    let initialValues: any = {
      appointment_date: firstInjectionDate,
      follow_up_date: firstInjectionDate,
      injection_count: 1,
      appointment_list: [
        { appointment_date: firstInjectionDate, follow_up_date: firstInjectionDate, injection_count: 1 }
      ]
    };

    if (preSelectedPatientId) {
      initialValues.patient_id = preSelectedPatientId;
      // Use provided list or state
      const listToUse = patientsList || patients;
      const patient = listToUse.find(p => p.id === preSelectedPatientId);
      if (patient) {
        initialValues.drug_name = patient.drug_type;
        initialValues.eye = patient.left_eye && patient.right_eye ? '双眼' : (patient.left_eye ? '左眼' : (patient.right_eye ? '右眼' : undefined));
        
        // 如果是经治患者且有针数记录，从针数+1开始
        if (patient.patient_type === '经治' && patient.injection_count) {
          const nextInjectionCount = patient.injection_count + 1;
          initialValues.injection_count = nextInjectionCount;
          initialValues.appointment_list = [{ 
            appointment_date: firstInjectionDate, 
            follow_up_date: firstInjectionDate, 
            injection_count: nextInjectionCount 
          }];
        }
        
        setShowBatchHint(patient.drug_type === '法瑞西单抗');
      } else {
        setShowBatchHint(false);
      }
    } else {
      setShowBatchHint(false);
    }

    form.setFieldsValue(initialValues);
    setEditingId(null);
    setIsModalOpen(true);
  };

  const handleEdit = (record: Appointment) => {
    form.resetFields();
    form.setFieldsValue({
      ...record,
      appointment_date: dayjs(record.appointment_date),
      follow_up_date: record.follow_up_date ? dayjs(record.follow_up_date) : undefined,
      next_follow_up_date: record.next_follow_up_date ? dayjs(record.next_follow_up_date) : undefined,
    });
    // Handle scheme related logic if needed, but for edit usually we just edit fields
    setEditingId(record.id);
    setIsModalOpen(true);
  };

  const handlePatientChange = (patientId: string) => {
    const patient = patients.find(p => p.id === patientId);
    if (patient) {
      const updateValues: any = {
        drug_name: patient.drug_type,
        eye: patient.left_eye && patient.right_eye ? '双眼' : (patient.left_eye ? '左眼' : (patient.right_eye ? '右眼' : undefined)),
      };
      
      // 如果是经治患者且有针数记录，从针数+1开始
      if (patient.patient_type === '经治' && patient.injection_count) {
        const nextInjectionCount = patient.injection_count + 1;
        updateValues.injection_count = nextInjectionCount;
        
        // 更新预约列表中的针数
        const currentList = form.getFieldValue('appointment_list') || [];
        if (currentList.length > 0) {
          const updatedList = currentList.map((item: any, index: number) => ({
            ...item,
            injection_count: nextInjectionCount + index
          }));
          updateValues.appointment_list = updatedList;
        }
      }
      
      form.setFieldsValue(updateValues);
      setShowBatchHint(patient.drug_type === '法瑞西单抗');
    }
  };

  const saveAppointment = async () => {
    const values = await form.validateFields();

    const commonFields = {
      patient_id: values.patient_id,
      injection_number: values.injection_number,
      eye: values.eye,
      drug_name: values.drug_name,
      cost_type: values.cost_type,
      doctor: values.doctor,
      pre_op_vision_left: values.pre_op_vision_left,
      pre_op_vision_right: values.pre_op_vision_right,
      treatment_phase: values.treatment_phase,
    };

    if (editingId) {
      // Update existing appointment
      const payload = {
        ...values,
        ...commonFields,
        appointment_date: values.appointment_date ? values.appointment_date.format('YYYY-MM-DD') : undefined,
        follow_up_date: values.follow_up_date ? values.follow_up_date.format('YYYY-MM-DD') : undefined,
        next_follow_up_date: values.next_follow_up_date ? values.next_follow_up_date.format('YYYY-MM-DD') : undefined,
      };
      // Remove old fields if they somehow persist in values
      delete payload.pre_op_vision;

      await apiClient.patch(`/appointments/${editingId}`, payload);
      message.success('预约更新成功');
    } else {
      const appointment_list = values.appointment_list || [];
      if (appointment_list.length === 0) {
        // Fallback to single if list is empty for some reason
        const payload = {
          ...commonFields,
          appointment_date: values.appointment_date ? values.appointment_date.format('YYYY-MM-DD') : undefined,
          follow_up_date: values.follow_up_date ? values.follow_up_date.format('YYYY-MM-DD') : undefined,
          injection_count: values.injection_count,
          injection_number: values.injection_number,
          treatment_phase: values.treatment_phase,
          next_follow_up_date: values.next_follow_up_date ? values.next_follow_up_date.format('YYYY-MM-DD') : undefined,
          status: 'scheduled',
        };
        await apiClient.post('/appointments', payload);
      } else {
        const batchPayload = appointment_list.map((item: any) => ({
          ...commonFields,
          appointment_date: item.appointment_date ? item.appointment_date.format('YYYY-MM-DD') : undefined,
          follow_up_date: item.follow_up_date ? item.follow_up_date.format('YYYY-MM-DD') : undefined,
          injection_count: item.injection_count,
          injection_number: item.injection_number,
          treatment_phase: item.treatment_phase,
          next_follow_up_date: item.next_follow_up_date ? item.next_follow_up_date.format('YYYY-MM-DD') : undefined,
          status: 'scheduled',
        }));
        await apiClient.post('/appointments/batch', batchPayload);
      }
      message.success('预约创建成功');
    }

    // Preserve filters after refresh
    const searchValues = searchForm.getFieldsValue();
    fetchAppointments(searchValues);

    return values.patient_id;
  };

  const handleOk = async () => {
    setLoading(true);
    try {
      await saveAppointment();
      setIsModalOpen(false);
    } catch (error) {
      console.error(error);
      message.error('保存失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAndPrint = async () => {
    setLoading(true);
    try {
      const patientId = await saveAppointment();
      setIsModalOpen(false);
      navigate(`/print-center?patient_id=${patientId}`);
    } catch (error) {
      console.error(error);
      message.error('保存并跳转失败');
    } finally {
      setLoading(false);
    }
  };
  const handlePrintClick = (record: Appointment) => {
    navigate(`/print-center?patient_id=${record.patient_id}`);
  };

  const handleCancelAppointment = async (record: Appointment) => {
    Modal.confirm({
      title: '确认取消预约',
      content: `确定要取消患者 ${patients.find(p => p.id === record.patient_id)?.name || '未知'} 的预约吗？`,
      okText: '确认取消',
      cancelText: '保留预约',
      okType: 'danger',
      onOk: async () => {
        try {
          await apiClient.patch(`/appointments/${record.id}`, {
            ...record,
            status: 'cancelled'
          });
          message.success('预约已取消');
          // 刷新列表，保持当前筛选条件
          const searchValues = searchForm.getFieldsValue();
          fetchAppointments(searchValues);
        } catch (error) {
          console.error(error);
          message.error('取消预约失败');
        }
      }
    });
  };

  const columns: ColumnsType<Appointment> = [
    {
      title: '玻注日期',
      dataIndex: 'appointment_date',
      key: 'appointment_date',
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD') : '-',
      sorter: (a, b) => {
        const dateA = a.appointment_date ? dayjs(a.appointment_date).unix() : 0;
        const dateB = b.appointment_date ? dayjs(b.appointment_date).unix() : 0;
        return dateA - dateB;
      },
    },
    {
      title: '注药号',
      dataIndex: 'injection_number',
      key: 'injection_number',
    },

    {
      title: '患者姓名',
      dataIndex: 'patient_id',
      key: 'patient_name',
      render: (patientId) => {
        const patient = patients.find(p => p.id === patientId);
        return patient ? `${patient.name} (${patient.outpatient_number || '-'})` : '未知患者';
      }
    },
    {
      title: '药品',
      dataIndex: 'drug_name',
      key: 'drug_name',
    },
    {
      title: '眼别',
      dataIndex: 'eye',
      key: 'eye',
    },
    {
      title: '针次',
      dataIndex: 'injection_count',
      key: 'injection_count',
      render: (text) => `第${text}针`,
    },
    {
      title: '治疗周期',
      dataIndex: 'treatment_phase',
      key: 'treatment_phase',
      render: (text) => <Tag color={text === '强化期' ? 'blue' : 'green'}>{text || '-'}</Tag>,
    },
    {
      title: '医生',
      dataIndex: 'doctor',
      key: 'doctor',
    },
    {
      title: '费别',
      dataIndex: 'cost_type',
      key: 'cost_type',
      render: (text) => <Tag>{text}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        let color = 'default';
        let text = '未知';
        switch (status) {
          case 'scheduled': color = 'processing'; text = '已预约'; break;
          case 'confirmed': color = 'success'; text = '已确认'; break;
          case 'completed': color = 'green'; text = '已完成'; break;
          case 'cancelled': color = 'error'; text = '已取消'; break;
        }
        return <Badge status={color as any} text={text} />;
      }
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<PrinterOutlined />}
            onClick={() => handlePrintClick(record)}
          >
            打印
          </Button>
          {record.status !== 'completed'  && (
            <Button
              type="link"
              onClick={() => handleEdit(record)}
            >
              编辑
            </Button>
          )}
          {record.status !== 'completed' && record.status !== 'cancelled' && (
            <Button
              type="link"
              danger
              icon={<CloseOutlined />}
              onClick={() => handleCancelAppointment(record)}
            >
              取消
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Form form={searchForm} layout="inline">
          <Form.Item name="dateRange" label="日期范围">
            <DatePicker.RangePicker />
          </Form.Item>
          <Form.Item name="patient_name" label="姓名">
            <Input placeholder="患者姓名" style={{ width: 120 }} />
          </Form.Item>
          <Form.Item name="doctor" label="医生">
            <Select placeholder="选择医生" style={{ width: 120 }} allowClear>
              {doctors.map(d => (
                <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="injection_number" label="注药号">
            <Input placeholder="注药号" style={{ width: 120 }} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" onClick={handleSearch}>搜索</Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card
        title="预约管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => handleAdd()}>
            新建预约
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={appointments}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>

      <Modal
        title={editingId ? "编辑预约" : "新建预约"}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        width={800}
        footer={[
          <Button key="save" type="primary" loading={loading} onClick={handleOk}>
            确定预约
          </Button>,
          <Button key="print" type="primary" loading={loading} onClick={handleSaveAndPrint}>
            确定预约并打印
          </Button>,
        ]}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="patient_id" label="选择患者" rules={[{ required: true }]}>
                <Select
                  showSearch
                  placeholder="搜索患者姓名/电话"
                  optionFilterProp="children"
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  onChange={handlePatientChange}
                  options={patients.map(p => ({ label: `${p.name}${p.phone ? ` (${p.phone})` : ''}`, value: p.id }))}
                />
              </Form.Item>
            </Col>
          </Row>

          {!editingId && (
            <Card size="small" title="玻注预约日期列表" style={{ marginBottom: 16 }}>
              <Form.List name="appointment_list">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <Row gutter={8} key={key} align="middle">
                        <Col span={5}>
                          <Form.Item
                            {...restField}
                            name={[name, 'follow_up_date']}
                            label="复诊日期"
                          >
                            <DatePicker style={{ width: '100%' }} />
                          </Form.Item>
                        </Col>
                        <Col span={5}>
                          <Form.Item
                            {...restField}
                            name={[name, 'appointment_date']}
                            label="玻注日期"
                          >
                            <DatePicker style={{ width: '100%' }} />
                          </Form.Item>
                        </Col>
                        <Col span={3}>
                          <Form.Item
                            {...restField}
                            name={[name, 'injection_count']}
                            label="针次"
                          >
                            <InputNumber min={1} style={{ width: '100%' }} />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item
                            {...restField}
                            name={[name, 'injection_number']}
                            label="注药号"
                          >
                            <Input placeholder="号" />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item
                            {...restField}
                            name={[name, 'treatment_phase']}
                            label="阶段"
                          >
                            <Select placeholder="阶段">
                              <Select.Option value="强化期">强化期</Select.Option>
                              <Select.Option value="巩固期">巩固期</Select.Option>
                            </Select>
                          </Form.Item>
                        </Col>
                        <Col span={3}>
                          <Button
                            type="link"
                            danger
                            onClick={() => remove(name)}
                            style={{ padding: 0, marginTop: 12 }}
                          >
                            移除
                          </Button>
                        </Col>
                      </Row>
                    ))}
                    <Form.Item>
                      <Button type="dashed" onClick={() => {
                        const currentList = form.getFieldValue('appointment_list') || [];
                        const lastItem = currentList[currentList.length - 1];
                        const base = lastItem ? dayjs(lastItem.appointment_date).add(1, 'month') : dayjs();
                        const nextDate = getNearestInjectionDate(base, injectionWeekdays);
                        add({
                          appointment_date: nextDate,
                          follow_up_date: nextDate,
                          injection_count: lastItem ? (lastItem.injection_count || 0) + 1 : 1,
                          treatment_phase: lastItem ? lastItem.treatment_phase : '强化期'
                        });
                      }} block icon={<PlusOutlined />}>
                        添加玻注预约日期
                      </Button>
                    </Form.Item>
                  </>
                )}
              </Form.List>
              {showBatchHint && !editingId && (
                <div style={{ padding: '8px 12px', background: '#e6f7ff', border: '1px solid #91d5ff', borderRadius: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                  <span style={{ color: '#1677ff', fontSize: '13px' }}>检测到可使用批量生成后续预约，点击“启动批量生成”按钮后，可生成4次预约</span>
                  <Button type="primary" size="small" onClick={startBatchGeneration}>
                    启动批量生成
                  </Button>
                </div>
              )}
            </Card>
          )}

          {editingId && (
            <>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="follow_up_date" label="复诊日期">
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="appointment_date" label="玻注日期">
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="injection_number" label="注药号">
                    <Input placeholder="例如：20231001-01" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="injection_count" label="注药次数" initialValue={1}>
                    <InputNumber min={1} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="treatment_phase" label="治疗周期">
                    <Radio.Group>
                      <Radio value="强化期">强化期</Radio>
                      <Radio value="巩固期">巩固期</Radio>
                    </Radio.Group>
                  </Form.Item>
                </Col>
              </Row>
            </>
          )}

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="pre_op_vision_left" label="左眼视力">
                <InputNumber step={0.01} style={{ width: '100%' }} placeholder="例: 0.5" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="pre_op_vision_right" label="右眼视力">
                <InputNumber step={0.01} style={{ width: '100%' }} placeholder="例: 0.5" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="drug_name" label="药品名称">
                <Select
                  placeholder="请选择药品"
                  onChange={(val) => setShowBatchHint(val === '法瑞西单抗')}
                >
                  {drugs.map(d => (
                    <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="eye" label="眼别">
                <Radio.Group>
                  <Radio value="左眼">左眼</Radio>
                  <Radio value="右眼">右眼</Radio>
                  <Radio value="双眼">双眼</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="cost_type" label="费别">
                <Select placeholder="选择费别">
                  {costTypes.map(d => (
                    <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="doctor" label="注药医生">
                <Select placeholder="选择医生">
                  {doctors.map(d => (
                    <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

    </div>
  );
};

export default Appointments;
