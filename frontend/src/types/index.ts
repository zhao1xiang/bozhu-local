export interface Patient {
  id: string;
  name: string;
  outpatient_number?: string;
  phone?: string;
  diagnosis?: string;
  drug_type?: string;
  left_vision?: number;
  right_vision?: number;
  left_eye: boolean;
  right_eye: boolean;
  status: string;
  patient_type?: string;
  injection_count?: number;
  created_at: string;
  updated_at: string;
}

export interface PatientBase {
  name: string;
  outpatient_number?: string;
  phone?: string;
  diagnosis?: string;
  drug_type?: string;
  left_vision?: number;
  right_vision?: number;
  left_eye: boolean;
  right_eye: boolean;
  status: string;
  patient_type?: string;
  injection_count?: number;
}

export interface Appointment {
  id: string;
  patient_id: string;
  appointment_date: string;
  time_slot?: string;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  injection_number?: string;
  injection_count?: number;
  eye?: string;
  drug_name?: string;
  cost_type?: string;
  doctor?: string;
  next_follow_up_date?: string;
  follow_up_date?: string;
  diagnosis?: string;
  created_at: string;
  updated_at: string;
  patient?: Patient;
  pre_op_vision_left?: number;
  pre_op_vision_right?: number;
  pre_op_cst_left?: number;
  pre_op_cst_right?: number;
  treatment_phase?: string;
}

export interface AppointmentBase {
  patient_id: string;
  appointment_date: string;
  time_slot?: string;
  status: string;
  notes?: string;
  is_te_scheme: boolean;
  injection_number?: string;
  injection_count?: number;
  eye?: string;
  drug_name?: string;
  cost_type?: string;
  doctor?: string;
  next_follow_up_date?: string;
  pre_op_vision_left?: number;
  pre_op_vision_right?: number;
  treatment_phase?: string;
}

export interface InjectionScheme {
  id: string;
  name: string;
  drug_type: string;
  scheme_type: string;
  scheme_config?: string;
  status: string;
  created_at: string;
}

export interface InjectionSchemeBase {
  name: string;
  drug_type: string;
  scheme_type: string;
  scheme_config?: string;
  status: string;
}

export interface DataDictionaryItem {
  id: string;
  category: string;
  value: string;
  label: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
}
