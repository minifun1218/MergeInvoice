"""
OCR 识别服务 - 使用 RapidOCR
"""
import re
import io
from typing import Dict, Optional
from PIL import Image


class OCRService:
    """OCR识别服务"""

    _ocr_instance = None

    @classmethod
    def get_ocr(cls):
        """获取OCR实例（单例模式）"""
        if cls._ocr_instance is None:
            from rapidocr_onnxruntime import RapidOCR
            cls._ocr_instance = RapidOCR()
            print("✅ RapidOCR 初始化完成")
        return cls._ocr_instance

    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> str:
        """从图片中提取文字"""
        try:
            import numpy as np

            # 加载图片
            image = Image.open(io.BytesIO(image_bytes))

            # 转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 转换为numpy数组
            image_array = np.array(image)

            # 获取OCR实例
            ocr = OCRService.get_ocr()

            # 执行识别
            result, elapse = ocr(image_array)

            # 提取所有文本
            # RapidOCR返回格式：[[[box], text, confidence], ...]
            if result:
                texts = [line[1] for line in result if line and len(line) > 1]
                full_text = "\n".join(texts)
                print(f"✅ RapidOCR识别耗时: {elapse}秒")
                return full_text
            return ""
        except Exception as e:
            print(f"❌ OCR识别失败: {e}")
            import traceback
            traceback.print_exc()
            return ""

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """从PDF中提取文字（转换第一页为图片后识别）"""
        try:
            import fitz  # PyMuPDF

            # 打开PDF
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = pdf_document[0]  # 第一页

            # 渲染为图片（200 DPI）
            pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72))

            # 转换为PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pdf_document.close()

            # 转换为bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            # 使用OCR识别
            return OCRService.extract_text_from_image(img_bytes)
        except Exception as e:
            print(f"❌ PDF识别失败: {e}")
            return ""

    @staticmethod
    def parse_invoice_info(text: str) -> Dict:
        """从OCR文本中解析发票信息（简化版 - 只识别金额）"""
        import uuid
        from datetime import datetime

        info = {
            "seller_name": "发票供应商",
            "buyer_name": "我的公司",
            "amount": 0.0,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "code": "",
            "number": "",
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        if not text:
            print("⚠️ 未提取到文本，使用默认金额")
            return info

        lines = text.split('\n')
        print(f"📝 OCR识别到 {len(lines)} 行文本")

        # 策略1: 查找"价税合计"关键词，然后在后续几行中查找金额
        amount_keywords = ['价税合计', '合计金额', '总金额', '合计', '总额']
        for i, line in enumerate(lines):
            if any(kw in line for kw in amount_keywords):
                print(f"🔍 找到关键词: {line}")
                # 在当前行和后续3行中查找金额
                search_lines = lines[i:min(i+4, len(lines))]
                for search_line in search_lines:
                    # 格式1: ¥123.45 或 ￥123.45
                    amount_matches = re.findall(r'[¥￥]\s*([\d,]+\.?\d*)', search_line)
                    if amount_matches:
                        amount_str = amount_matches[-1].replace(',', '')
                        try:
                            amount = float(amount_str)
                            if amount > 0:
                                info["total_amount"] = amount
                                print(f"✅ 识别到金额（格式1）: ¥{info['total_amount']} 从行: {search_line.strip()}")
                                break
                        except:
                            pass

                if info["total_amount"] > 0:
                    break

        # 策略2: 如果策略1失败，直接搜索所有包含¥符号的金额，取最大的
        if info["total_amount"] == 0.0:
            print("🔍 策略1失败，尝试策略2：查找所有¥金额")
            all_amounts = []
            for line in lines:
                amount_matches = re.findall(r'[¥￥]\s*([\d,]+\.?\d*)', line)
                for match in amount_matches:
                    try:
                        amount = float(match.replace(',', ''))
                        if amount > 0:
                            all_amounts.append(amount)
                            print(f"  找到金额: ¥{amount} 从行: {line.strip()}")
                    except:
                        pass

            if all_amounts:
                # 取最大的金额作为总金额
                info["total_amount"] = max(all_amounts)
                print(f"✅ 识别到金额（策略2-最大值）: ¥{info['total_amount']}")

        # 策略3: 如果还是失败，查找纯数字格式（至少有2位小数）
        if info["total_amount"] == 0.0:
            print("🔍 策略2失败，尝试策略3：查找纯数字")
            for line in lines:
                if any(kw in line for kw in ['价税合计', '合计金额', '总金额', '小写']):
                    # 在当前行和后续3行查找
                    search_index = lines.index(line)
                    search_lines = lines[search_index:min(search_index+4, len(lines))]
                    for search_line in search_lines:
                        amount_matches = re.findall(r'([\d,]+\.\d{2})', search_line)
                        if amount_matches:
                            amount_str = amount_matches[-1].replace(',', '')
                            try:
                                amount = float(amount_str)
                                if amount > 0:
                                    info["total_amount"] = amount
                                    print(f"✅ 识别到金额（策略3）: ¥{info['total_amount']}")
                                    break
                            except:
                                pass
                    if info["total_amount"] > 0:
                        break

        # 如果识别到金额，计算税额和不含税金额
        if info["total_amount"] > 0:
            info["amount"] = round(info["total_amount"] / 1.13, 2)
            info["tax_amount"] = round(info["total_amount"] - info["amount"], 2)
            print(f"💡 按13%税率计算 - 金额: ¥{info['amount']}, 税额: ¥{info['tax_amount']}")
        else:
            print(f"⚠️ 未识别到金额")

        # 打印最终结果
        print(f"\n📊 最终解析结果:")
        print(f"   供应商: {info['seller_name']}")
        print(f"   金额: ¥{info['total_amount']}")
        print(f"   日期: {info['date']}")

        return info

    @staticmethod
    def recognize_invoice(file_content: bytes, file_type: str) -> Dict:
        """识别发票（统一接口）"""
        print(f"🔍 开始OCR识别，文件类型: {file_type}")

        # 提取文字
        if file_type == "pdf":
            text = OCRService.extract_text_from_pdf(file_content)
        else:
            text = OCRService.extract_text_from_image(file_content)

        print(f"📄 识别到文本（前200字）:\n{text[:2500]}")

        # 解析发票信息
        invoice_info = OCRService.parse_invoice_info(text)

        print(f"✅ 解析结果: {invoice_info}")

        return invoice_info
