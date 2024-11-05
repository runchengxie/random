import time
import os
from zhipuai import ZhipuAI

api_key = os.getenv('ZHIPUAI_API_KEY')
if api_key is None:
    raise ValueError("Please set ZHIPUAI_API_KEY environment variable")

client = ZhipuAI(api_key=api_key)

input_text = """
【美国大选还没结果 大A概念股已经涨疯 股民惊呆：有一种置身于精神病院的感觉】11月5日，A股市场又是一片热闹，全市场超5000只股票上涨。网友都懵了，美国大选结果没出来，中国的A股先涨为敬，不知道是什么逻辑。据报道，候选人特朗普、哈里斯的票数非常接近。媒体普遍认为，这次大选是美国近年来选情最为胶着的总统选举，是“本世纪以来最势均力敌”的一场。

为此，远在彼岸的A股投资者也非常振奋，带动着市场情绪的上涨。热度最高的，当属“川大智胜”。wind显示，其在十二小时最热榜单里位列第6，今日股价盘中一度接近涨停。川大智胜这么火，原因只有一个，名字起得好。曾有投资者认为川大智胜，拆解开就是“川普大选制胜”。

类似的，“川发龙蟒”连续两个交易日涨停，近一个月股价涨135.43%。其既有业绩增长的基础，又有特朗普谐音。按网友说法，如果特朗普真当选了，那就是“川普发迹于龙蟒之交，川普兴，龙蟒旺”。更扯的是，莎普爱思近一个月上涨19.66%，有人认为这代表“杀川普，爱哈里斯”。

投资者们一看一个懵，直呼“太抽象了”“大受震撼”。他们表示：“有些时候我真的觉得在A股投资是件丢脸的事情，我该如何跟其他场外人士介绍，我们的暴涨来自谐音梗”、“我有一种置身于精神病院的感觉......这不就是反复割穷人现金流和流动性的陷阱吗？”、“玄学，中国风”。不过，话也别说太满，有网友发现摩根士丹利在今年第三季度买进了川大智胜，位列第八流通股股东。这被称是“全球股民都一样”。（易简财经）。
"""

# 创建异步完成请求
try:
    response = client.chat.asyncCompletions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你现在是沃伦·巴菲特，奥马哈的神谕，伯克希尔·哈撒韦公司的CEO。请用巴菲特的视角和投资理念来分析和评价你看到的信息，回答注意简单，倾向于一到两句话。在回答时要体现出以下特点：1) 强调长期价值投资 2) 关注企业的基本面和护城河 3) 保持谨慎和理性的投资态度 4) 经常使用简单易懂的比喻 5) 提到你过去的投资经验和教训"},
            {"role": "user", "content": f"请以巴菲特的视角解读这段信息：\n\n{input_text}"}
        ]
    )
    task_id = response.id
    print(f"任务ID: {task_id}")  # 确认请求已发送
except Exception as e:
    print(f"创建异步请求时发生异常: {e}")
    exit(1)

task_status = ''
get_cnt = 0

while task_status not in ['SUCCESS', 'FAILED'] and get_cnt < 40:
    try:
        if task_id is None:
            print("任务ID为空")
            break
            
        result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
        print(f"尝试 {get_cnt + 1}: 状态 - {result_response.task_status}")
        task_status = result_response.task_status
        if task_status == 'SUCCESS':
            if result_response.choices and len(result_response.choices) > 0:
                content = result_response.choices[0].message.content
                print("完成内容:")
                print(content)
            else:
                print("没有可用的完成内容。")
            break
        elif task_status == 'FAILED':
            print("请求失败")
            break
    except Exception as e:
        print(f"获取结果时发生异常: {e}")
        break

    time.sleep(2)
    get_cnt += 1

if get_cnt >= 40 and task_status not in ['SUCCESS', 'FAILED']:
    print("请求超时，未能在80秒内完成。")