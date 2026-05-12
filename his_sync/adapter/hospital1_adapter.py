from core.logger import logger


def convert_patient(row, his_conn=None):
    """
    转换第一家医院的患者数据
    字段映射：
    BRXM  -> name (病人姓名)
    ZYH   -> outpatient_number (住院号，保持原有逻辑)
    mzbrid -> medical_card_number (门诊号，存入就诊卡号字段)
    zylsh  -> 住院流水号，暂不存库，仅日志输出
    """
    try:
        name = str(row["BRXM"]) if row.get("BRXM") is not None else None
        zyh = str(row["ZYH"]) if row.get("ZYH") is not None else None
        mzbrid = str(row["mzbrid"]) if row.get("mzbrid") is not None else None

        # zylsh 暂不存库，仅日志输出
        zylsh = str(row["zylsh"]) if row.get("zylsh") is not None else None
        logger.info(f"[新字段] mzbrid={mzbrid}, zylsh={zylsh}, ZYH={zyh}")

        # ZYH -> 住院号（outpatient_number），mzbrid -> 门诊号（medical_card_number）
        outpatient_number = zyh
        medical_card_number = mzbrid

        phone = str(row["LXDH"]) if row.get("LXDH") is not None else None
        diagnosis = None
        patient_type = None

        # 数据验证（只验证姓名，mzbrid 不一定有值不做验证）
        if not name or not name.strip():
            logger.warning(f"患者姓名为空，ZYH: {zyh}")

        # 查询视力视图 V_YDHL_SLJC（用 mzbrid 作为 brid 查询参数）
        left_vision = None
        right_vision = None
        left_vision_corrected = None
        right_vision_corrected = None

        if mzbrid and his_conn:
            try:
                vision_cursor = his_conn.cursor()
                vision_cursor.execute(
                    "SELECT LLYSL, RLYSL, LJZSL, RJZSL FROM V_YDHL_SLJC WHERE brid=?",
                    (mzbrid,)
                )
                vision_row = vision_cursor.fetchone()
                vision_cursor.close()
                if vision_row:
                    left_vision = str(vision_row[0]) if vision_row[0] is not None else None
                    right_vision = str(vision_row[1]) if vision_row[1] is not None else None
                    left_vision_corrected = str(vision_row[2]) if vision_row[2] is not None else None
                    right_vision_corrected = str(vision_row[3]) if vision_row[3] is not None else None
                    logger.info(
                        f"[视力] mzbrid={mzbrid} 左裸={left_vision} 右裸={right_vision} "
                        f"左矫={left_vision_corrected} 右矫={right_vision_corrected}"
                    )
                else:
                    logger.debug(f"[视力] mzbrid={mzbrid} 在 V_YDHL_SLJC 中无记录")
            except Exception as e:
                logger.warning(f"[视力] 查询 V_YDHL_SLJC 失败 mzbrid={mzbrid}: {e}")

        result = {
            "name": name.strip() if name else "",
            "outpatient_number": outpatient_number,
            "medical_card_number": medical_card_number,
            "phone": phone,
            "diagnosis": diagnosis,
            "patient_type": patient_type,
            "left_vision": left_vision,
            "right_vision": right_vision,
            "left_vision_corrected": left_vision_corrected,
            "right_vision_corrected": right_vision_corrected,
        }

        logger.debug(f"转换第一家医院患者数据: ZYH={outpatient_number}, mzbrid={medical_card_number}, name={name}")
        return result

    except Exception as e:
        logger.error(f"转换第一家医院患者数据失败: {e}, 原始数据: {dict(row)}")
        return {
            "name": "数据转换错误",
            "outpatient_number": None,
            "medical_card_number": None,
            "phone": None,
            "diagnosis": None,
            "patient_type": None,
            "left_vision": None,
            "right_vision": None,
            "left_vision_corrected": None,
            "right_vision_corrected": None,
        }
