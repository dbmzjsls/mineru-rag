import json
import subprocess
import sys
from pathlib import Path

from src.config import Config

class MinerUParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.pdf_name = self.pdf_path.stem
        # 默认输出目录
        self.output_dir = Config.DATA_OUT_DIR / self.pdf_name

    def parse_pdf(self):
        """将PDF转化为结构化 JSON"""
        print(f"[Parser]正在使用MinerU解析 PDF：{self.pdf_name}")
        mineru_exe = str(Path(sys.executable).parent / "mineru")
        cmd = f'{mineru_exe} -p "{self.pdf_path}" -o "{Config.DATA_OUT_DIR}"'
        subprocess.call(cmd, shell=True)
        print(f"[Parser]解析完成，输出目录为：{self.output_dir}")

    def load_json(self) ->list :
        """读取MinerU 输出的结构化内容"""
        json_files = list(self.output_dir.glob("*_content.json"))
        if not json_files:
            raise FileNotFoundError(f"未在{self.output_dir} 中找到 JSON 配置文件")

        target_json = json_files[0]
        with open(target_json, "r", encoding='utf-8') as f:
            data = json.load(f)
        print(f"[Parser] 成功加载实例化 JSON：{target_json.name}")
        return data