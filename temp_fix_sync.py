with open('his_sync/sync/patient_sync.py', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

# 找到重复的 patient_type 块并修复
old = """            # patient_type \u4e3a\u7a7a\u65f6\u4e0d\u66f4\u65b0
            if patient_type:
                update_fields.append("patient_type=?")
                update_values.append(patient_type)
            if patient_type:
                update_fields.append("patient_type=?")
                update_values.append(patient_type)"""

new = """            # patient_type \u4e3a\u7a7a\u65f6\u4e0d\u66f4\u65b0
            if patient_type:
                update_fields.append("patient_type=?")
                update_values.append(patient_type)"""

content = content.replace(old, new)

# 加 diagnosis 日志
old2 = """            # diagnosis \u4e3a\u7a7a\u65f6\u4e0d\u66f4\u65b0
            if diagnosis:
                update_fields.append("diagnosis=?")
                update_values.append(diagnosis)"""

new2 = """            # diagnosis \u4e3a\u7a7a\u65f6\u4e0d\u66f4\u65b0
            if diagnosis:
                update_fields.append("diagnosis=?")
                update_values.append(diagnosis)
                logger.debug(f"diagnosis \u6709\u5024\uff0c\u66f4\u65b0: {diagnosis}")
            else:
                logger.debug(f"diagnosis \u4e3a\u7a7a ({repr(diagnosis)})\uff0c\u8df3\u8fc7\u66f4\u65b0")"""

content = content.replace(old2, new2)

with open('his_sync/sync/patient_sync.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('done')
