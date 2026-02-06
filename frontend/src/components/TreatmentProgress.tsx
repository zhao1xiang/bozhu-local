import React, { useEffect, useState } from 'react';
import { Card, Steps, Table, Statistic, Empty } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { Patient, Appointment } from '@/types';
import { apiClient } from '@/api/client';
import dayjs from 'dayjs';

interface TreatmentProgressProps {
    patient: Patient;
}

const TreatmentProgress: React.FC<TreatmentProgressProps> = ({ patient }) => {
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchAppointments = async () => {
            setLoading(true);
            try {
                const response = await apiClient.get<Appointment[]>('/appointments');
                // Client-side filter for now
                const patientAppointments = response.data.filter(a => a.patient_id === patient.id);
                const sorted = patientAppointments.sort((a, b) => dayjs(a.appointment_date).valueOf() - dayjs(b.appointment_date).valueOf());
                setAppointments(sorted);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        if (patient) {
            fetchAppointments();
        }
    }, [patient]);

    const completedAppointments = appointments.filter(a => a.status === 'completed');
    const injectionCount = completedAppointments.length;

    // Helper to format improvement
    const formatImprovement = (left: number | undefined, right: number | undefined, baseLeft: number | undefined, baseRight: number | undefined) => {
        let text = [];
        if (left !== undefined && baseLeft !== undefined) {
            const diff = left - baseLeft;
            text.push(`L: ${diff > 0 ? '+' : ''}${diff}`);
        }
        if (right !== undefined && baseRight !== undefined) {
            const diff = right - baseRight;
            text.push(`R: ${diff > 0 ? '+' : ''}${diff}`);
        }
        return text.length > 0 ? text.join(' / ') : '-';
    };

    const cstRecords = appointments.filter(a => (a.pre_op_cst_left !== undefined || a.pre_op_cst_right !== undefined));
    let cstImprovement = '-';
    if (cstRecords.length >= 2) {
        const latest = cstRecords[cstRecords.length - 1];
        const baseline = cstRecords[0];
        cstImprovement = formatImprovement(latest.pre_op_cst_left, latest.pre_op_cst_right, baseline.pre_op_cst_left, baseline.pre_op_cst_right);
        if (cstImprovement !== '-') cstImprovement += ' μm';
    }

    const currentVision = (() => {
        if (appointments.length === 0) return '-';
        const last = appointments[appointments.length - 1];
        const left = last.pre_op_vision_left ?? patient.left_vision;
        const right = last.pre_op_vision_right ?? patient.right_vision;
        return `L:${left ?? '-'} / R:${right ?? '-'}`;
    })();

    const columns: ColumnsType<Appointment> = [
        {
            title: '序号',
            key: 'index',
            render: (_, __, index) => index + 1,
            width: 60,
        },
        {
            title: '实际日期',
            dataIndex: 'appointment_date',
            key: 'appointment_date',
        },
        {
            title: '治疗眼别',
            dataIndex: 'eye',
            key: 'eye',
            render: (text) => text || (patient.left_eye ? '左眼' : '右眼'),
        },
        {
            title: '所选药物',
            dataIndex: 'drug_name',
            key: 'drug_name',
            render: (text) => text || patient.drug_type,
        },
        {
            title: '术前视力',
            key: 'pre_op_vision',
            render: (_, record) => `L:${record.pre_op_vision_left ?? '-'} R:${record.pre_op_vision_right ?? '-'}`,
        },
        // {
        //     title: '术前CST',
        //     key: 'pre_op_cst',
        //     render: (_, record) => `L:${record.pre_op_cst_left ?? '-'} R:${record.pre_op_cst_right ?? '-'}`,
        // },
        {
            title: '备注',
            dataIndex: 'notes',
            key: 'notes',
        },
    ];

    return (
        <div className="treatment-progress">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
                <Card bordered={false} bodyStyle={{ padding: 16 }}>
                    <Statistic title="累计注射" value={injectionCount} suffix="次" valueStyle={{ fontWeight: 'bold' }} />
                </Card>
                <Card bordered={false} bodyStyle={{ padding: 16 }}>
                    <Statistic title="当前视力" value={currentVision} valueStyle={{ color: '#1677ff', fontWeight: 'bold', fontSize: 16 }} />
                </Card>
                {/* <Card bordered={false} bodyStyle={{ padding: 16 }}>
                    <Statistic title="CST 改善" value={cstImprovement} valueStyle={{ color: cstImprovement.includes('+') ? '#cf1322' : '#3f8600', fontWeight: 'bold', fontSize: 16 }} />
                </Card> */}
                <Card bordered={false} bodyStyle={{ padding: 16 }}>
                    <Statistic title="当前药物" value={patient.drug_type || '-'} valueStyle={{ fontSize: 16, fontWeight: 'bold' }} />
                </Card>
            </div>

            <Card title="注药计划与执行时间轴" className="mb-6" bordered={false}>
                <div style={{ overflowX: 'auto', paddingBottom: 20 }}>
                    <Steps
                        current={completedAppointments.length}
                        items={appointments.map(apt => ({
                            title: dayjs(apt.appointment_date).format('MM.DD'),
                            description: apt.status === 'completed' ? '已完成' : '计划',
                        }))}
                    />
                </div>
            </Card>

            <Card title="注药记录详情" bordered={false}>
                <Table
                    columns={columns}
                    dataSource={appointments}
                    rowKey="id"
                    pagination={false}
                    loading={loading}
                />
            </Card>
        </div>
    );
};

export default TreatmentProgress;
