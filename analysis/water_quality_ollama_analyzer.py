import os
import pandas as pd
import ollama
from datetime import datetime

# ====================== 配置 ======================
# 修改为水质监测根目录
ROOT_FOLDER = r"C:\Users\93478\Desktop\水质监测"
preprocessed_folder = os.path.join(ROOT_FOLDER, "预处理", "预处理后")

OLLAMA_MODEL = "qwen2.5:14b"

AVAILABLE_YEARS = ["2021年", "2022年", "2023年", "2024年", "2025年"]


# ====================== 数据加载 ======================
def load_and_clean_data(year_name):
    file_path = os.path.join(preprocessed_folder, f"{year_name}_预处理后.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ {year_name} 文件不存在")
        return None
    
    df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
    print(f"✅ 已加载 {year_name} 数据 ({len(df):,} 行)")
    
    numeric_cols = [
        "水温(℃)", "pH(无量纲)", "溶解氧(mg/L)", "电导率(μS/cm)", "浊度(NTU)",
        "高锰酸盐指数(mg/L)", "氨氮(mg/L)", "总磷(mg/L)", "总氮(mg/L)",
        "叶绿素α(mg/L)", "藻密度(cells/L)"
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['未检出', '—', '-', '＜', '<', '>', '以下', 'ND'], '', regex=True)
            df[col] = df[col].str.extract(r'([-+]?\d*\.?\d+)')[0]
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if "监测时间" in df.columns:
        df["监测时间"] = pd.to_datetime(df["监测时间"], errors='coerce')
    
    return df


# ====================== 预计时间 ======================
def estimate_analysis_time(num_rows):
    if num_rows < 50000:
        return "15-25秒"
    elif num_rows < 150000:
        return "25-40秒"
    elif num_rows < 300000:
        return "40-60秒"
    else:
        return "60-90秒"


# ====================== 多维度分析 ======================
def multi_year_analysis(selected_years, region=None, column=None, custom_question=None):
    print("\n🚀 开始进行水质分析...")
    
    data_dict = {}
    total_rows = 0
    
    for year in selected_years:
        df = load_and_clean_data(year)
        if df is not None:
            data_dict[year] = df
            total_rows += len(df)
    
    if not data_dict:
        print("❌ 没有加载到任何数据")
        return
    
    full_df = pd.concat(data_dict.values(), ignore_index=True)
    est_time = estimate_analysis_time(total_rows)
    
    print(f"🎉 总共加载 {total_rows:,} 条记录 | 年份：{', '.join(selected_years)}")
    print(f"⏱️  预计分析耗时：{est_time}\n")
    
    # ==================== 保存路径修改为根目录下的“分析报告” ====================
    report_dir = os.path.join(ROOT_FOLDER, "分析报告")
    os.makedirs(report_dir, exist_ok=True)
    
    years_str = "、".join(selected_years)
    
    # 生成提示词
    prompt = f"""你是一位资深水质监测数据专家。
请对以下年份的水质数据进行综合分析：{years_str}。

总记录数：{total_rows:,}
涉及年份：{years_str}
"""

    if region:
        prompt += f"指定分析地区：{region}\n"
    if column:
        prompt += f"重点关注指标：{column}\n"
    if custom_question:
        prompt += f"用户具体问题：{custom_question}\n"

    prompt += "\n请从以下角度进行专业分析：\n1. 总体水质状况及趋势\n2. 重点指标变化情况\n3. 区域差异（如果指定）\n4. 提出1-2条实用建议"

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt}]
        )
        answer = response['message']['content']
        
        print("\n🤖 Qwen2.5-14B 分析结果：\n")
        print(answer)
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        report_path = os.path.join(report_dir, f"水质分析报告_{timestamp}.txt")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"分析时间：{datetime.now()}\n")
            f.write(f"模型：{OLLAMA_MODEL}\n")
            f.write(f"年份：{years_str}\n")
            f.write(f"地区：{region or '全国'}   指标：{column or '综合'}\n\n")
            f.write(answer)
            
        print(f"\n✅ 报告已保存至：")
        print(f"   {report_path}")
        
    except Exception as e:
        print(f"❌ Ollama 调用失败: {e}")


# ====================== 年份选择 ======================
def select_years():
    print("\n=== 可选年份 ===")
    for i, year in enumerate(AVAILABLE_YEARS, 1):
        print(f"{i}. {year}")
    
    print("\n请选择年份（支持多选）:")
    print("输入编号（如 1,3,5），输入 'all' 或直接回车 = 全选")
    
    choice = input("你的选择: ").strip()
    
    if choice.lower() == 'all' or choice == '':
        return AVAILABLE_YEARS.copy()
    
    selected = []
    try:
        indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
        for idx in indices:
            if 1 <= idx <= len(AVAILABLE_YEARS):
                selected.append(AVAILABLE_YEARS[idx-1])
    except:
        print("输入有误，已默认选择全部年份")
        return AVAILABLE_YEARS.copy()
    
    return selected if selected else AVAILABLE_YEARS.copy()


# ====================== 主程序 ======================
if __name__ == "__main__":
    print("=== 水质监测多维度分析工具 ===\n")
    
    selected_years = select_years()
    print(f"已选择年份：{', '.join(selected_years)}\n")
    
    region = input("请输入地区/省份（直接回车=全国）: ").strip() or None
    column = input("请输入重点指标（如氨氮(mg/L)、溶解氧(mg/L)，直接回车=综合）: ").strip() or None
    question = input("请输入具体问题（直接回车=自动分析）: ").strip() or None
    
    multi_year_analysis(selected_years, region, column, question)