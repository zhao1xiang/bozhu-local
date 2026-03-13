import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Input, Space, Modal, Form, Select, Checkbox, InputNumber, message, DatePicker, Tag, Radio, Upload } from 'antd';
import { PlusOutlined, SearchOutlined, EditOutlined, ProjectOutlined, CalendarOutlined, DownloadOutlined, UploadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { Patient, DataDictionaryItem, Appointment } from '@/types';
import { apiClient } from '@/api/client';
import TreatmentProgress from '@/components/TreatmentProgress';
import dayjs from 'dayjs';
import ExcelJS from 'exceljs';

const Patients: React.FC = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [drugs, setDrugs] = useState<DataDictionaryItem[]>([]);
  const [diagnoses, setDiagnoses] = useState<DataDictionaryItem[]>([]);
  const [searchText, setSearchText] = useState('');
  const [diagnosisFilter, setDiagnosisFilter] = useState<string | undefined>(undefined);
  const [drugFilter, setDrugFilter] = useState<string | undefined>(undefined);
  const [eyeFilter, setEyeFilter] = useState<string | undefined>(undefined);

  // Patient Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);

  // Treatment Progress State
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false);
  const [selectedPatientForProgress, setSelectedPatientForProgress] = useState<Patient | null>(null);

  // Import Modal State
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [importing, setImporting] = useState(false);

  const [form] = Form.useForm();
  
  // 监听患者类型变化
  const patientType = Form.useWatch('patient_type', form);
  // 监听诊断和药物选择
  const diagnosis = Form.useWatch('diagnosis', form);
  const drugType = Form.useWatch('drug_type', form);

  // 检查患者是否重复
  const checkPatientDuplicate = async (field: 'outpatient_number' | 'phone', value: string) => {
    if (!value || !value.trim()) return;
    
    // 如果是编辑模式，跳过检查
    if (editingPatient) return;
    
    try {
      // 在现有患者列表中查找重复
      const existingPatient = patients.find(p => 
        field === 'outpatient_number' ? p.outpatient_number === value : p.phone === value
      );
      
      if (existingPatient) {
        Modal.confirm({
          title: '发现重复患者',
          content: `${field === 'outpatient_number' ? '门诊号' : '联系方式'}已存在，患者：${existingPatient.name} (${existingPatient.outpatient_number})`,
          okText: '跳转到预约',
          cancelText: '加载信息继续编辑',
          onOk: () => {
            // 跳转到预约页面
            setIsModalOpen(false);
            navigate(`/app/appointments?patient_id=${existingPatient.id}`);
          },
          onCancel: () => {
            // 加载患者信息继续编辑
            setEditingPatient(existingPatient);
            form.setFieldsValue({
              ...existingPatient,
            });
            message.info('已加载患者信息，你可以继续编辑');
          }
        });
      }
    } catch (error) {
      console.error('检查重复患者失败:', error);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [patientsRes, drugsRes, diagnosesRes] = await Promise.all([
        apiClient.get<Patient[]>('/patients'),
        apiClient.get<DataDictionaryItem[]>('/data-dictionary', { params: { category: 'drug' } }),
        apiClient.get<DataDictionaryItem[]>('/data-dictionary', { params: { category: 'diagnosis' } }),
      ]);
      setPatients(Array.isArray(patientsRes.data) ? patientsRes.data : []);
      setDrugs(Array.isArray(drugsRes.data) ? drugsRes.data.filter(d => d.is_active) : []);
      setDiagnoses(Array.isArray(diagnosesRes.data) ? diagnosesRes.data.filter(d => d.is_active) : []);
    } catch (error) {
      console.error(error);
      message.error('获取患者数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAdd = () => {
    setEditingPatient(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (record: Patient) => {
    setEditingPatient(record);
    // 将诊断和药物字符串转换为数组（兼容旧数据）
    const formData = {
      ...record,
      diagnosis: record.diagnosis ? record.diagnosis.split(',').map(s => s.trim()) : [],
      drug_type: record.drug_type ? record.drug_type.split(',').map(s => s.trim()) : [],
    };
    form.setFieldsValue(formData);
    setIsModalOpen(true);
  };

  const handleDeletePatient = (record: Patient) => {
    Modal.confirm({
      title: '确认删除患者',
      content: (
        <div>
          <p>确定要删除患者 <strong>{record.name}</strong> 吗？</p>
          <p style={{ color: '#ff4d4f' }}>此操作将同时删除该患者的所有预约记录！</p>
          <p style={{ color: '#999', fontSize: '12px' }}>注：删除后数据仍保留在数据库中，不会真正删除。</p>
        </div>
      ),
      okText: '确认删除',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          await apiClient.delete(`/patients/${record.id}`);
          message.success('患者及相关预约已删除');
          fetchData();
        } catch (error) {
          console.error(error);
          message.error('删除失败');
        }
      }
    });
  };

  const savePatient = async () => {
    const values = await form.validateFields();
    
    if (values.patient_type === '经治') {
      const { left_eye, right_eye } = values;
      if (!left_eye && !right_eye) {
        message.error('请至少选择一个治疗眼');
        throw new Error('请至少选择一个治疗眼');
      }
    }
    
    // 将诊断和药物数组转换为逗号分隔的字符串
    const patientData = {
      ...values,
      diagnosis: Array.isArray(values.diagnosis) ? values.diagnosis.join(',') : values.diagnosis || '',
      drug_type: Array.isArray(values.drug_type) ? values.drug_type.join(',') : values.drug_type || '',
    };
    
    try {
      if (editingPatient) {
        await apiClient.put(`/patients/${editingPatient.id}`, patientData);
        message.success('更新成功');
        return editingPatient.id;
      } else {
        const response = await apiClient.post('/patients', patientData);
        message.success('添加成功');
        return response.data.id;
      }
    } catch (error: any) {
      console.error(error);
      message.error('操作失败');
      throw error;
    }
  };

  const handleOk = async () => {
    setLoading(true);
    try {
      const patientId = await savePatient();
      if (patientId === null) {
        // Info was loaded, don't close modal yet
        return;
      }
      setIsModalOpen(false);
      fetchData();
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAndAppointment = async () => {
    setLoading(true);
    try {
      const patientId = await savePatient();
      if (patientId === null) {
        // Info was loaded, don't navigate yet
        return;
      }
      setIsModalOpen(false);
      fetchData();
      navigate(`/app/appointments?patient_id=${patientId}`);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 患者列表导出：以患者为主表，针数(右眼/左眼)从预约表统计
  const handleExport = async () => {
    const filtered = searchText
      ? patients.filter(
          (p) =>
            p.name.includes(searchText) ||
            (p.phone?.includes(searchText) ?? false) ||
            (p.outpatient_number?.includes(searchText) ?? false)
        )
      : patients;

    let appointments: Appointment[] = [];
    try {
      const res = await apiClient.get<Appointment[]>('/appointments', { params: { limit: 10000 } });
      appointments = res.data;
    } catch (e) {
      console.error(e);
      message.error('获取预约数据失败');
      return;
    }

    const byPatient = new Map<string, Appointment[]>();
    for (const a of appointments) {
      if (a.status === 'cancelled') continue;
      const list = byPatient.get(a.patient_id) ?? [];
      list.push(a);
      byPatient.set(a.patient_id, list);
    }
    for (const list of byPatient.values()) {
      list.sort((a, b) =>
        dayjs(a.appointment_date || 0).valueOf() - dayjs(b.appointment_date || 0).valueOf()
      );
    }

    const countRight = (list: Appointment[]) =>
      list.filter((a) => a.eye === '右眼' || a.eye === '双眼').length;
    const countLeft = (list: Appointment[]) =>
      list.filter((a) => a.eye === '左眼' || a.eye === '双眼').length;

    const PATIENT_HEADERS = ['姓名', '门诊号', '就诊卡号', '联系方式', '患者类型', '针数(右眼)', '针数(左眼)', '眼底病诊断'];
    const TREATMENT_SUB_HEADERS = [
      '治疗日期', '注药号', '治疗眼', '治疗药物', '费别', '治疗阶段',
      '针数（右眼）', '针数（左眼）', '裸眼视力（右眼）', '裸眼视力（左眼）', 
      '左眼压', '右眼压', '血压', '血糖', '冲眼结果', '病毒报告',
      '复诊日期', '注药医生', '管床医生'
    ];
    const SUB_COLS = TREATMENT_SUB_HEADERS.length;

    const allPatientLists = filtered.map((p) => byPatient.get(p.id) ?? []);
    const maxTreatments = Math.max(4, ...allPatientLists.map((list) => list.length));

    const headerStyle = {
      font: { bold: true, size: 11, name: 'Microsoft YaHei' },
      alignment: { horizontal: 'center' as const, vertical: 'middle' as const, wrapText: true },
      fill: { type: 'pattern' as const, pattern: 'solid' as const, fgColor: { argb: 'FFE8F4FC' } },
      border: {
        top: { style: 'thin' as const },
        left: { style: 'thin' as const },
        bottom: { style: 'thin' as const },
        right: { style: 'thin' as const }
      }
    };
    const subHeaderStyle = {
      ...headerStyle,
      fill: { type: 'pattern' as const, pattern: 'solid' as const, fgColor: { argb: 'FFF0F7FF' } }
    };
    const dataCellStyle = {
      font: { size: 10, name: 'Microsoft YaHei' },
      alignment: { vertical: 'middle' as const },
      border: {
        top: { style: 'thin' as const },
        left: { style: 'thin' as const },
        bottom: { style: 'thin' as const },
        right: { style: 'thin' as const }
      }
    };

    const wb = new ExcelJS.Workbook();
    const ws = wb.addWorksheet('患者列表', { views: [{ state: 'frozen', ySplit: 2 }] });

    const row1Data: (string | undefined)[] = [...PATIENT_HEADERS];
    for (let n = 1; n <= maxTreatments; n++) {
      row1Data.push(`第${n}次治疗`);
      for (let i = 1; i < SUB_COLS; i++) row1Data.push(undefined);
    }
    const row2Data: (string | undefined)[] = new Array(PATIENT_HEADERS.length).fill(undefined);
    for (let n = 0; n < maxTreatments; n++) {
      row2Data.push(...TREATMENT_SUB_HEADERS);
    }

    const r1 = ws.addRow(row1Data);
    r1.height = 24;
    r1.eachCell((cell, colNumber) => {
      cell.style = headerStyle;
      if (colNumber <= PATIENT_HEADERS.length) {
        cell.alignment = { ...headerStyle.alignment, horizontal: 'center' as const };
      }
    });
    for (let n = 0; n < maxTreatments; n++) {
      ws.mergeCells(1, PATIENT_HEADERS.length + n * SUB_COLS + 1, 1, PATIENT_HEADERS.length + (n + 1) * SUB_COLS);
    }

    const r2 = ws.addRow(row2Data);
    r2.height = 22;
    r2.eachCell((cell, colNumber) => {
      if (colNumber > PATIENT_HEADERS.length) {
        cell.style = subHeaderStyle;
      }
    });

    filtered.sort((a, b) => {
      const listA = byPatient.get(a.id) ?? [];
      const listB = byPatient.get(b.id) ?? [];
      const dateA = listA[0]?.appointment_date ?? '';
      const dateB = listB[0]?.appointment_date ?? '';
      return dayjs(dateA).valueOf() - dayjs(dateB).valueOf();
    });

    for (const p of filtered) {
      const list = byPatient.get(p.id) ?? [];
      const patientCountRight = countRight(list);
      const patientCountLeft = countLeft(list);
      const rowData: (string | number)[] = [
        p.name ?? '',
        p.outpatient_number ?? '',
        p.medical_card_number ?? '',
        p.phone ?? '',
        p.patient_type ?? '',
        p.right_eye ? patientCountRight : '',
        p.left_eye ? patientCountLeft : '',
        p.diagnosis ?? ''
      ];

      for (let i = 0; i < maxTreatments; i++) {
        const a = list[i];
        if (!a) {
          rowData.push(...new Array(SUB_COLS).fill(''));
          continue;
        }
        const eye = a.eye || '';
        const count = a.injection_count ?? '';
        const countRightVal = (eye === '右眼' || eye === '双眼') ? count : '';
        const countLeftVal = (eye === '左眼' || eye === '双眼') ? count : '';
        rowData.push(
          a.appointment_date ? dayjs(a.appointment_date).format('YYYY-MM-DD') : '',
          a.injection_number ?? '',
          eye,
          a.drug_name ?? '',
          a.cost_type ?? '',
          a.treatment_phase ?? '',
          countRightVal,
          countLeftVal,
          a.pre_op_vision_right ?? '',
          a.pre_op_vision_left ?? '',
          a.left_eye_pressure ?? '',
          a.right_eye_pressure ?? '',
          a.blood_pressure ?? '',
          a.blood_sugar ?? '',
          a.eye_wash_result ?? '',
          a.virus_report ?? '',
          a.follow_up_date ? dayjs(a.follow_up_date).format('YYYY-MM-DD') : '',
          a.doctor ?? '',
          a.attending_doctor ?? ''
        );
      }

      const dataRow = ws.addRow(rowData);
      dataRow.height = 20;
      dataRow.eachCell((cell) => {
        cell.style = dataCellStyle;
      });
    }

    const colWidths: number[] = [10, 12, 12, 14, 10, 10, 10, 18];
    for (let n = 0; n < maxTreatments; n++) {
      for (let i = 0; i < SUB_COLS; i++) {
        if (i === 6 || i === 7 || i === 8 || i === 9) {
          // 针数（右/左）+ 裸眼视力（右/左）
          colWidths.push(18);
        } else if (i === 0 || i === 16) {
          // 治疗日期 / 复诊日期
          colWidths.push(12);
        } else if (i === 10 || i === 11 || i === 12 || i === 13 || i === 14 || i === 15) {
          // 左眼压、右眼压、血压、血糖、冲眼结果、病毒报告
          colWidths.push(12);
        } else {
          // 其它列
          colWidths.push(10);
        }
      }
    }
    colWidths.forEach((w, i) => {
      ws.getColumn(i + 1).width = w;
    });

    const buffer = await wb.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `患者导出_${dayjs().format('YYYY-MM-DD_HHmm')}.xlsx`;
    link.click();
    URL.revokeObjectURL(url);
    message.success('导出成功');
  };

  // 下载导入模板
  const handleDownloadTemplate = async () => {
    try {
      const response = await apiClient.get('/patients/template/download', {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = '患者批量导入模板.xlsx';
      link.click();
      URL.revokeObjectURL(url);
      message.success('模板下载成功');
    } catch (error) {
      console.error(error);
      message.error('模板下载失败');
    }
  };

  // 批量导入患者
  const handleImport = async (file: File) => {
    setImporting(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post('/patients/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const result = response.data;
      
      // 显示导入结果
      Modal.info({
        title: '导入完成',
        width: 600,
        content: (
          <div>
            <p>成功导入: {result.success_count} 条</p>
            <p>失败: {result.error_count} 条</p>
            
            {result.duplicates && result.duplicates.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <p style={{ fontWeight: 'bold', color: '#ff4d4f' }}>重复的患者:</p>
                <ul style={{ maxHeight: 200, overflow: 'auto' }}>
                  {result.duplicates.map((dup: any, idx: number) => (
                    <li key={idx}>
                      第{dup.row}行: {dup.name} ({dup.phone}) - 已存在患者: {dup.existing_name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {result.errors && result.errors.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <p style={{ fontWeight: 'bold', color: '#ff4d4f' }}>错误信息:</p>
                <ul style={{ maxHeight: 200, overflow: 'auto' }}>
                  {result.errors.map((err: any, idx: number) => (
                    <li key={idx}>第{err.row}行: {err.error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ),
        onOk: () => {
          setIsImportModalOpen(false);
          fetchData(); // 刷新患者列表
        }
      });
    } catch (error: any) {
      console.error(error);
      message.error(error.response?.data?.detail || '导入失败');
    } finally {
      setImporting(false);
    }

    return false; // 阻止自动上传
  };

  const columns: ColumnsType<Patient> = [
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      filteredValue: searchText ? [searchText] : null,
      onFilter: (value, record) =>
        record.name.includes(value as string) ||
        (record.phone?.includes(value as string) ?? false) ||
        (record.outpatient_number?.includes(value as string) ?? false),
    },
    {
      title: '门诊号',
      dataIndex: 'outpatient_number',
      key: 'outpatient_number',
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
    },
    {
      title: '诊断',
      dataIndex: 'diagnosis',
      key: 'diagnosis',
      filteredValue: diagnosisFilter ? [diagnosisFilter] : null,
      onFilter: (value, record) => record.diagnosis?.includes(value as string) ?? false,
      render: (text) => {
        if (!text) return '-';
        const items = text.split(',').map((s: string) => s.trim()).filter(Boolean);
        return (
          <Space size={[0, 4]} wrap>
            {items.map((item: string, idx: number) => (
              <Tag key={idx} color="blue">{item}</Tag>
            ))}
          </Space>
        );
      },
    },
    {
      title: '药物',
      dataIndex: 'drug_type',
      key: 'drug_type',
      filteredValue: drugFilter ? [drugFilter] : null,
      onFilter: (value, record) => record.drug_type?.includes(value as string) ?? false,
      render: (text) => {
        if (!text) return '-';
        const items = text.split(',').map((s: string) => s.trim()).filter(Boolean);
        return (
          <Space size={[0, 4]} wrap>
            {items.map((item: string, idx: number) => (
              <Tag key={idx} color={item === '法瑞西单抗' ? 'purple' : 'default'}>{item}</Tag>
            ))}
          </Space>
        );
      },
    },
    {
      title: '患者类型',
      dataIndex: 'patient_type',
      key: 'patient_type',
      render: (text, record) => (
        <span>
          <Tag color={text === '初治' ? 'blue' : 'orange'}>{text || '-'}</Tag>
          {text === '经治' && record.injection_count && (
            <Tag color="purple">已完成{record.injection_count}针</Tag>
          )}
        </span>
      ),
    },
    {
      title: '治疗眼',
      key: 'eye',
      filteredValue: eyeFilter ? [eyeFilter] : null,
      onFilter: (value, record) => {
        if (value === 'left') return !!record.left_eye;
        if (value === 'right') return !!record.right_eye;
        if (value === 'both') return !!(record.left_eye && record.right_eye);
        return true;
      },
      render: (_, record) => (
        <span>
          {record.left_eye ? '左眼' : ''} {record.right_eye ? '右眼' : ''}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button 
            type="primary" 
            icon={<CalendarOutlined />} 
            onClick={() => navigate(`/app/appointments?patient_id=${record.id}`)}
          >
            预约
          </Button>
          <Button
            type="primary"
            ghost
            icon={<ProjectOutlined />}
            onClick={() => {
              setSelectedPatientForProgress(record);
              setIsProgressModalOpen(true);
            }}
          >
            治疗进度
          </Button>
          <Button
            danger
            onClick={() => handleDeletePatient(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Input
            placeholder="搜索姓名/电话/门诊号"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Select
            placeholder="诊断"
            style={{ width: 150 }}
            allowClear
            value={diagnosisFilter}
            onChange={(value) => setDiagnosisFilter(value)}
          >
            {diagnoses.map(d => (
              <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
            ))}
          </Select>
          <Select
            placeholder="药物"
            style={{ width: 150 }}
            allowClear
            value={drugFilter}
            onChange={(value) => setDrugFilter(value)}
          >
            {drugs.map(d => (
              <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
            ))}
          </Select>
          <Select
            placeholder="治疗眼"
            style={{ width: 120 }}
            allowClear
            value={eyeFilter}
            onChange={(value) => setEyeFilter(value)}
          >
            <Select.Option value="left">左眼</Select.Option>
            <Select.Option value="right">右眼</Select.Option>
            <Select.Option value="both">双眼</Select.Option>
          </Select>
        </Space>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出
          </Button>
          <Button icon={<UploadOutlined />} onClick={() => setIsImportModalOpen(true)}>
            批量导入
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加患者
          </Button>
        </Space>
      </div>
      <Table columns={columns} dataSource={patients} rowKey="id" loading={loading} />

      {/* Add/Edit Patient Modal */}
      <Modal
        title={editingPatient ? '编辑患者' : '添加患者'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsModalOpen(false)}>
            取消
          </Button>,
          <Button key="save" type="primary" loading={loading} onClick={handleOk}>
            {editingPatient ? '更新' : '新增'}
          </Button>,
          !editingPatient && (
            <Button key="save-appt" type="primary" loading={loading} onClick={handleSaveAndAppointment}>
              新增并开始预约
            </Button>
          ),
        ].filter(Boolean)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="outpatient_number" label="门诊号">
            <Input placeholder="请输入门诊号" />
          </Form.Item>
          <Form.Item name="medical_card_number" label="就诊卡号">
            <Input placeholder="请输入就诊卡号" />
          </Form.Item>
          <Form.Item name="phone" label="联系方式" rules={[{ required: true, message: '请输入联系方式' }]}>
            <Input 
              onBlur={(e) => checkPatientDuplicate('phone', e.target.value)}
            />
          </Form.Item>
          <Form.Item name="diagnosis" label="诊断">
            <Select 
              mode="multiple" 
              placeholder="请选择诊断（可多选）" 
              showSearch
              maxTagCount="responsive"
            >
              {diagnoses.filter(d => d.value !== '其他').map(d => (
                <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="diagnosis_other" label="诊断其他说明">
            <Input placeholder="如有其他诊断，请在此输入" />
          </Form.Item>
          <Form.Item name="drug_type" label="治疗药物">
            <Select 
              mode="multiple" 
              placeholder="请选择治疗药物（可多选）"
              maxTagCount="responsive"
            >
              {drugs.filter(d => d.value !== '其他').map(d => (
                <Select.Option key={d.id} value={d.value}>{d.label}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="drug_type_other" label="药物其他说明">
            <Input placeholder="如有其他药物，请在此输入" />
          </Form.Item>
          <Form.Item name="patient_type" label="患者类型">
            <Radio.Group>
              <Radio value="初治">初治</Radio>
              <Radio value="经治">经治</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item 
            label="治疗眼"
            required={patientType === '经治'}
          >
            <Space>
              <Form.Item name="left_eye" valuePropName="checked" noStyle>
                <Checkbox>左眼</Checkbox>
              </Form.Item>
              <Form.Item name="right_eye" valuePropName="checked" noStyle>
                <Checkbox>右眼</Checkbox>
              </Form.Item>
            </Space>
          </Form.Item>
          {patientType === '经治' && (
            <Form.Item 
              name="injection_count" 
              label="已完成针数" 
              rules={[{ required: true, message: '请输入已完成针数' }]}
            >
              <InputNumber min={1} max={50} placeholder="例如：3" />
            </Form.Item>
          )}
          <div style={{ marginBottom: 16 }}>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>裸眼视力</div>
            <Space>
              <Form.Item name="left_vision" label="左眼" style={{ marginBottom: 0 }}>
                <Input placeholder="例: 0.5 或 手动" />
              </Form.Item>
              <Form.Item name="right_vision" label="右眼" style={{ marginBottom: 0 }}>
                <Input placeholder="例: 0.5 或 手动" />
              </Form.Item>
            </Space>
          </div>
          <div style={{ marginBottom: 16 }}>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>矫正视力</div>
            <Space>
              <Form.Item name="left_vision_corrected" label="左眼" style={{ marginBottom: 0 }}>
                <Input placeholder="例: 0.8 或 手动" />
              </Form.Item>
              <Form.Item name="right_vision_corrected" label="右眼" style={{ marginBottom: 0 }}>
                <Input placeholder="例: 0.8 或 手动" />
              </Form.Item>
            </Space>
          </div>
          <Form.Item name="remarks" label="备注">
            <Input.TextArea 
              rows={3} 
              placeholder="请输入备注信息（选填）" 
              maxLength={500}
              showCount
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Treatment Progress Modal */}
      <Modal
        title={selectedPatientForProgress ? `${selectedPatientForProgress.name} - 治疗进度` : '治疗进度'}
        open={isProgressModalOpen}
        onCancel={() => setIsProgressModalOpen(false)}
        footer={null}
        width={1000}
      >
        {selectedPatientForProgress && <TreatmentProgress patient={selectedPatientForProgress} />}
      </Modal>

      {/* Import Modal */}
      <Modal
        title="批量导入患者"
        open={isImportModalOpen}
        onCancel={() => setIsImportModalOpen(false)}
        footer={null}
        width={600}
      >
        <div style={{ padding: '20px 0' }}>
          <div style={{ marginBottom: 24 }}>
            <h4>导入步骤：</h4>
            <ol>
              <li>下载Excel模板</li>
              <li>按照模板格式填写患者信息</li>
              <li>上传填写好的Excel文件</li>
            </ol>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Button 
              icon={<DownloadOutlined />} 
              onClick={handleDownloadTemplate}
              block
              size="large"
            >
              下载导入模板
            </Button>
          </div>

          <div>
            <Upload.Dragger
              accept=".xlsx,.xls"
              beforeUpload={handleImport}
              showUploadList={false}
              disabled={importing}
            >
              <p className="ant-upload-drag-icon">
                <UploadOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              </p>
              <p className="ant-upload-text">
                {importing ? '正在导入...' : '点击或拖拽Excel文件到此区域'}
              </p>
              <p className="ant-upload-hint">
                支持 .xlsx 和 .xls 格式
              </p>
            </Upload.Dragger>
          </div>

          <div style={{ marginTop: 16, padding: 12, background: '#fff7e6', borderRadius: 4, border: '1px solid #ffd591' }}>
            <p style={{ margin: 0, fontSize: 12, color: '#ad6800' }}>
              <strong>注意事项：</strong>
            </p>
            <ul style={{ margin: '8px 0 0 0', paddingLeft: 20, fontSize: 12, color: '#ad6800' }}>
              <li>姓名和手机号为必填项</li>
              <li>手机号不能重复</li>
              <li>患者类型必须是"初治"或"经治"</li>
              <li>左眼注射/右眼注射填写"是"或"否"</li>
            </ul>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Patients;
