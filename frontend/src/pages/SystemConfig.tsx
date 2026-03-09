import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, Switch, message, Card, Tabs, Select} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiClient } from '@/api/client';

interface DataDictionaryItem {
  id: string;
  category: string;
  value: string;
  label: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
}

const DictionaryTable: React.FC<{ category: string, title: string }> = ({ category, title }) => {
  const [items, setItems] = useState<DataDictionaryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<DataDictionaryItem | null>(null);
  const [form] = Form.useForm();

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<DataDictionaryItem[]>('/data-dictionary', {
        params: { category }
      });
      setItems(response.data);
    } catch (error) {
      console.error(error);
      message.error('获取列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [category]);

  const handleAdd = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({
      category,
      sort_order: 0,
      is_active: true
    });
    setIsModalOpen(true);
  };

  const handleEdit = (item: DataDictionaryItem) => {
    setEditingItem(item);
    form.setFieldsValue(item);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/data-dictionary/${id}`);
      message.success('删除成功');
      fetchItems();
    } catch (error) {
      console.error(error);
      message.error('删除失败');
    }
  };



  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingItem) {
        await apiClient.put(`/data-dictionary/${editingItem.id}`, values);
        message.success('更新成功');
      } else {
        await apiClient.post('/data-dictionary', values);
        message.success('创建成功');
      }
      setIsModalOpen(false);
      fetchItems();
    } catch (error) {
      console.error(error);
      message.error('操作失败');
    }
  };

  // 根据类别获取示例文本
  const getPlaceholderText = (field: 'label' | 'value') => {
    const examples = {
      doctor: { label: '例如：张三医生', value: '例如：张三' },
      cost_type: { label: '例如：自费', value: '例如：自费' },
      drug: { label: '例如：雷珠单抗', value: '例如：雷珠单抗' },
      diagnosis: { label: '例如：糖尿病性黄斑水肿', value: '例如：糖尿病性黄斑水肿' }
    };
    return examples[category as keyof typeof examples]?.[field] || `例如：${title}名称`;
  };

  const columns = [
    {
      title: '显示名称',
      dataIndex: 'label',
      key: 'label',
    },
    {
      title: '值',
      dataIndex: 'value',
      key: 'value',
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Switch checked={isActive} disabled />
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: DataDictionaryItem) => (
        <span>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>删除</Button>
        </span>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          添加{title}
        </Button>
      </div>
      <Table columns={columns} dataSource={items} rowKey="id" loading={loading} />

      <Modal
        title={editingItem ? `编辑${title}` : `添加${title}`}
        open={isModalOpen}
        onOk={handleOk}
        onCancel={() => setIsModalOpen(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="category" hidden>
            <Input />
          </Form.Item>
          <Form.Item name="label" label="显示名称" rules={[{ required: true }]}>
            <Input placeholder={getPlaceholderText('label')} />
          </Form.Item>
          <Form.Item name="value" label="值" rules={[{ required: true }]}>
            <Input placeholder={getPlaceholderText('value')} />
          </Form.Item>
          <Form.Item name="sort_order" label="排序 (越小越靠前)">
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="is_active" label="启用状态" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

const GeneralSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSetting();
  }, []);

  const fetchSetting = async () => {
    setLoading(true);
    try {
      const [reminderResp, weekdayResp, intervalResp, phoneResp] = await Promise.all([
        apiClient.get('/system-settings/reminder_days_advance'),
        apiClient.get('/system-settings/injection_weekday'),
        apiClient.get('/system-settings/injection_interval_first_4'),
        apiClient.get('/system-settings/print_phone_number'),
      ]);

      form.setFieldsValue({
        reminder_days_advance: Number(reminderResp.data.value),
        // 玻注日：后端以逗号分隔字符串存储，这里还原为多选数组
        injection_weekday: weekdayResp.data.value
          ? String(weekdayResp.data.value).split(',').filter(Boolean)
          : [],
        injection_interval_first_4: Number(intervalResp.data.value) || 30,
        print_phone_number: phoneResp.data.value || '',
      });
    } catch (error) {
      console.error(error);
      form.setFieldsValue({
        reminder_days_advance: 3,
        injection_weekday: ['1'], // 默认周一
        injection_interval_first_4: 30,
        print_phone_number: '',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    try {
      await Promise.all([
        apiClient.put('/system-settings/reminder_days_advance', {
          value: values.reminder_days_advance.toString(),
          description: '提前提醒天数'
        }),
        apiClient.put('/system-settings/injection_weekday', {
          // 多选的玻注日使用逗号分隔字符串进行存储，例如 "1,3,5"
          value: Array.isArray(values.injection_weekday)
            ? values.injection_weekday.join(',')
            : values.injection_weekday?.toString() || '',
          description: '玻注日（1-7 表示周一到周日，可多选，逗号分隔）'
        }),
        apiClient.put('/system-settings/injection_interval_first_4', {
          value: values.injection_interval_first_4.toString(),
          description: '前4针注射间隔（天）'
        }),
        apiClient.put('/system-settings/print_phone_number', {
          value: values.print_phone_number,
          description: '打印页面显示的联系电话'
        })
      ]);

      message.success('保存成功');
    } catch (error) {
      console.error(error);
      message.error('保存失败');
    }
  };


  //玻注日
  const WEEKDAY_OPTIONS = [
    { label: '周一', value: '1' },
    { label: '周二', value: '2' },
    { label: '周三', value: '3' },
    { label: '周四', value: '4' },
    { label: '周五', value: '5' },
    { label: '周六', value: '6' },
    { label: '周日', value: '7' },
  ];

  return (
    <div style={{ maxWidth: 600 }}>
      <Form form={form} layout="vertical" onFinish={handleSave}>
        <Form.Item
          name="reminder_days_advance"
          label="复诊提醒提前天数"
          extra="设置在复诊日期前几天出现在提醒列表中"
          rules={[{ required: true, message: '请输入天数' }]}
        >
          <InputNumber min={1} max={30} style={{ width: 200 }} suffix="天" />
        </Form.Item>

        <Form.Item
          name="injection_weekday"
          label="玻注日"
          extra="可多选，批量预约时默认选择的注药星期"
          rules={[{ required: true, message: '请选择玻注日' }]}
        >
          <Select
            style={{ width: 200 }}
            mode="multiple"
            placeholder="请选择玻注日（可多选）"
            options={WEEKDAY_OPTIONS}
            optionLabelProp="label"
          />
        </Form.Item>

        <Form.Item
          name="injection_interval_first_4"
          label="前4针注射间隔"
          extra="设置前4针注射的间隔天数（第5针及以后按固定规则：2个月、3个月、4个月）"
          rules={[{ required: true, message: '请输入间隔天数' }]}
        >
          <InputNumber min={1} max={365} style={{ width: 200 }} suffix="天" />
        </Form.Item>

        <Form.Item
          name="print_phone_number"
          label="打印联系电话"
          extra="打印页面显示的联系电话号码（可选）"
          rules={[{ required: false }]}
        >
          <Input style={{ width: 200 }} placeholder="例如：13608685716" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            保存配置
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

const ChangePassword: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handlePasswordChange = async (values: any) => {
    setLoading(true);
    try {
      if (values.new_password !== values.confirm_password) {
        message.error('两次输入的密码不一致');
        setLoading(false);
        return;
      }

      await apiClient.post('/auth/change-password', {
        old_password: values.old_password,
        new_password: values.new_password
      });

      message.success('密码修改成功');
      form.resetFields();
    } catch (error: any) {
      console.error(error);
      message.error(error.response?.data?.detail || '密码修改失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400 }}>
      <Form form={form} layout="vertical" onFinish={handlePasswordChange}>
        <Form.Item name="old_password" label="旧密码" rules={[{ required: true, message: '请输入旧密码' }]}>
          <Input.Password />
        </Form.Item>
        <Form.Item name="new_password" label="新密码" rules={[{ required: true, message: '请输入新密码' }]}>
          <Input.Password />
        </Form.Item>
        <Form.Item name="confirm_password" label="确认新密码" rules={[{ required: true, message: '请再次输入新密码' }]}>
          <Input.Password />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>修改密码</Button>
        </Form.Item>
      </Form>
    </div>
  );
};

const SystemConfig: React.FC = () => {
  return (
    <Card title="系统配置">
      <Tabs items={[
        {
          key: 'doctor',
          label: '注药医生管理',
          children: <DictionaryTable category="doctor" title="医生" />
        },
        {
          key: 'cost_type',
          label: '费别管理',
          children: <DictionaryTable category="cost_type" title="费别" />
        },
        {
          key: 'drug',
          label: '药品管理',
          children: <DictionaryTable category="drug" title="药品" />
        },
        {
          key: 'diagnosis',
          label: '疾病诊断管理',
          children: <DictionaryTable category="diagnosis" title="疾病诊断" />
        },
        {
          key: 'general',
          label: '通用设置',
          children: <GeneralSettings />
        },
        {
          key: 'security',
          label: '安全设置',
          children: <ChangePassword />
        }
      ]} />
    </Card>
  );
};

export default SystemConfig;
