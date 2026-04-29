with open('frontend/src/pages/Appointments.tsx', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# 修复乱码的中文字符
content = content.replace("'巩固\ufffd?", "'巩固期'")
content = content.replace("'强化\ufffd?", "'强化期'")
content = content.replace(": '强化\ufffd?", ": '强化期'")
content = content.replace(": '巩固\ufffd?", ": '巩固期'")

# 在 batchList.push 里加 condition_status
old = """      batchList.push({
        appointment_date: date,
        follow_up_date: date,
        injection_count: injectionCount,
        treatment_phase: injectionCount > 4 ? '巩固期' : '强化期',
        time_slot: '上午'
      });"""
new = """      batchList.push({
        appointment_date: date,
        follow_up_date: date,
        injection_count: injectionCount,
        treatment_phase: injectionCount > 4 ? '巩固期' : '强化期',
        time_slot: '上午',
        condition_status: '稳定',
      });"""
content = content.replace(old, new)

# 在 add({ 里加 condition_status（两处）
old1 = """                          add({
                            appointment_date: nextDate,
                            follow_up_date: nextDate,
                            injection_count: nextInjectionCount,
                            treatment_phase: nextInjectionCount > 4 ? '巩固期' : '强化期',
                            time_slot: '上午'
                          });"""
new1 = """                          add({
                            appointment_date: nextDate,
                            follow_up_date: nextDate,
                            injection_count: nextInjectionCount,
                            treatment_phase: nextInjectionCount > 4 ? '巩固期' : '强化期',
                            time_slot: '上午',
                            condition_status: '稳定',
                          });"""
content = content.replace(old1, new1)

old2 = """                          add({
                            appointment_date: nextDate,
                            follow_up_date: nextDate,
                            injection_count: 1,
                            treatment_phase: '强化期',
                            time_slot: '上午'
                          });"""
new2 = """                          add({
                            appointment_date: nextDate,
                            follow_up_date: nextDate,
                            injection_count: 1,
                            treatment_phase: '强化期',
                            time_slot: '上午',
                            condition_status: '稳定',
                          });"""
content = content.replace(old2, new2)

with open('frontend/src/pages/Appointments.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("done")
