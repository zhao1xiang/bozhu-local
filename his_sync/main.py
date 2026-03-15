import time
import yaml
import signal
import sys
from sync.patient_sync import sync_patient
from core.logger import logger
from core.health_check import health_check


class SyncService:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """设置信号处理器，支持优雅关闭"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"接收到信号 {signum}，准备关闭服务...")
        self.running = False
        
    def run(self):
        """运行同步服务"""
        # 启动前进行健康检查
        if not health_check():
            logger.error("健康检查失败，服务无法启动")
            sys.exit(1)
        
        with open("config/config.yaml") as f:
            cfg = yaml.safe_load(f)

        interval = cfg["sync"]["interval"]
        logger.info(f"同步服务启动，同步间隔: {interval} 秒")

        while self.running:
            try:
                sync_patient()
                
            except Exception as e:
                logger.error(f"同步失败: {e}", exc_info=True)

            # 分段睡眠，以便能够响应关闭信号
            for _ in range(interval):
                if not self.running:
                    break
                time.sleep(1)
                
        logger.info("同步服务已关闭")


def main():
    service = SyncService()
    service.run()


if __name__ == "__main__":
    main()