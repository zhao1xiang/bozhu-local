"""
添加时间段字段的数据迁移脚本
为已有的预约记录添加默认时间段
"""
from sqlmodel import Session, select
from database import engine
from models import Appointment

def migrate_time_slot():
    """为已有预约添加默认时间段"""
    with Session(engine) as session:
        # 查询所有没有时间段的预约
        try:
            appointments = session.exec(
                select(Appointment).where(
                    (Appointment.time_slot == None) | (Appointment.time_slot == '')
                )
            ).all()
        except Exception as e:
            # 如果查询失败，可能是因为字段不存在，直接返回
            print(f"查询失败（可能是新数据库）: {e}")
            print("跳过迁移")
            return
        
        count = 0
        for appointment in appointments:
            # 设置默认为上午
            appointment.time_slot = '上午'
            session.add(appointment)
            count += 1
        
        if count > 0:
            session.commit()
            print(f"成功为 {count} 条预约记录添加默认时间段（上午）")
        else:
            print("没有需要迁移的记录")

if __name__ == "__main__":
    print("开始迁移时间段数据...")
    migrate_time_slot()
    print("迁移完成！")
