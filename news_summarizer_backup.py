from zhipuai import ZhipuAI
import httpx
import concurrent.futures
import queue
import threading
import time
import re
from PIL import Image, ImageDraw, ImageFont
import svgwrite
from pypinyin import lazy_pinyin, Style
import os

input = """
上市券商首现在三季度现金分红。

　　根据相关公告，首创证券(21.130, -0.44, -2.04%)、山西证券(6.460, 0.10, 1.57%)、南京证券(8.880, -0.18, -1.99%)、财通证券(8.200, -0.07, -0.85%)、西部证券(8.060, -0.14, -1.71%)、西南证券(4.750, -0.06, -1.25%)拟进行前三季度利润分配，合计拟派发现金红利约8.93亿元。

　　虽然从业绩表现来看，上述6家券商中不乏“失速”者，但仍大方出手。其中，西部证券和西南证券均是在中报分红基础上，再推出了分红计划。

　　南开大学金融发展研究院院长田利辉对券商中国记者表示，券商分红并非越多越好，需要考量多种因素，兼顾公司长远发展与股东利益。

　　2家券商年内或实施三次现金分红

　　三季报收官，明显可见上市公司分红积极性显著提高，215家公司披露了三季度分红预案。其中多数公司都是首次三季度分红，里面也包括了6家券商，这开启了上市券商首次三季度分红的历史纪录。

　　其中，山西证券拟每10股派发现金红利0.50元，共派发1.79亿元；西南证券拟每10股派发0.1元，实际分配利润为0.66亿元；西部证券拟每10股派发0.20元，拟分配股利0.89亿元；财通证券拟每10股派发0.50元，共派发2.32亿元；首创证券拟每股派发0.055元，合计拟派发总额1.50亿元；南京证券拟每股派发0.048元，合计派发1.77亿元。以上拟派发现金红利金额均含税。

　　需要指出的是，上述6家券商均在今年完成了2023年度现金分红，并且西南证券和西部证券还实施了2024年年中分红，分别派发现金红利6645.11万元和4469.58万元。也就是说，算上2023年度分红，如果后续落地顺利，西南证券和西部证券年内将派发现金红利三次。

　　业绩“失速”，仍推出大手笔分红

　　实际上，从最新披露的三季报数据来看，上述6家券商，业绩并不都十分亮眼。其中，仅首创证券和南京证券实现了营收和净利润的双增长，且增幅都在两位数以上。山西证券营业收入为21.66亿元，同比减少12.46%，不过归母净利润实现正增长；前三季度净赚5.33亿元，同比增长57.83%。

　　西南证券、西部证券、财通证券前三季度的营收和归母净利润均遭遇下滑。仅从归母净利润角度看，西南证券为4.83亿元，同比下降15.29%；西部证券为7.29亿元，同比下滑16.82%；财通证券实现归母净利润14.72亿元，微降1.93%。

　　不过，从股利支付率角度看，虽然上述券商业绩分化明显，不乏“失速”者，但并没有妨碍其大手笔现金分红。6家券商拟派发现金红利占归母净利润的比重在12.27%—33.68%。其中，山西证券为33.68%，南京证券为25.42%，首创证券为20.05%，财通证券为15.77%；西南证券和西部证券接近，分别为13.76%和12.27%。

　　“提高股东回报”是上述券商多次分红的原因之一。比如西南证券称，为积极响应监管号召，提高股东回报，推动一年多次分红，拟在2024年度中期利润分配基础上，拟进行前三季度利润分配。再如南京证券和山西证券均表示，是从公司发展和股东利益等因素综合考虑。

　　尚有10家券商中期分红未落地

　　其实，从上半年的分红情况看，已经能明显感受到上市券商更加大方了。

　　今年上半年，43家上市券商中，过半竞相推出现金分红方案，和往年选择中期分红券商数量屈指可数，形成明显反差。Wind显示，截至11月2日，2024年中期分红预案已经实施完毕的共有17家上市券商，合计分红53.74亿元（税前）。目前中期分红预案尚未实施的上市券商还有10家，合计约有46.84亿元现金“福利”将派发给各家券商股东。

　　在业内看来，上市券商积极分红，除响应政策号召、回报股东外，也有利于提升上市公司吸引力。尤其是随着高股息红利资产持续受到追捧，加大分红、多次分红有利于提高上市公司的估值。而对于市场而言，上市券商回报回报投资者意识和能力的提升，向市场传递积极信号，有利于提振投资者信心。

　　天风证券(5.820, -0.58, -9.06%)非银分析师杜鹏辉在研报中曾分析称，新“国九条”确立以分红为核心的上市企业质量评价体系，半强制性要求上市公司分红，对未来市场风格和投资范式影响深远。

　　杜鹏辉认为，过去，市场存在“高成长赛道过于拥挤，价值赛道无人问津”的问题。新“国九条”后，以分红为核心的政策变化或将有效重构市场估值体系。防止估值模型的过度简化，投资者需要审慎考量高增速的净利润能否实现到高增速的股息。

　　从近期券商策略分析师的研判来看，在一段时间内，高股息策略仍然有一定空间。不过，对于面临业绩考验和高资本投入的券商而言，分红并非越多越好。

　　田利辉认为，对于券商这类资本密集型公司，分红计划需考虑盈利能力与现金流，确保分红不影响公司正常运营和未来发展。同时也需考虑资产负债健康，避免过度分红增加债务负担，以及考虑股东需求与结构，注重股东回报期望与股权稳定性。此外，券商也需考虑发展战略与资金需求，确保分红不与重大投资计划冲突。
"""

# Create a custom httpx client without a proxy
print("Initializing HTTP client...")
custom_http_client = httpx.Client(trust_env=False)
print("HTTP client initialized.")

client = ZhipuAI(
    api_key=os.environ.get('ZHIPUAI_API_KEY'),
    http_client=custom_http_client
)
print("ZhipuAI client created.")

def get_response():
    print("Sending request to ZhipuAI for summary...")
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "system",
                "content": """
你是一位优秀的新闻分析师和摘要专家。当用户提供一段新闻信息时，你需要分析并提供以下格式的摘要：

文章标题：[根据内容生成一个简洁而吸引人的标题]
关键词：[列出4-5个与新闻容相关的关键词，用逗号分隔]
重要的三句话：
1. [第一个重要句子或要点]
2. [第二个重要句子或要点]
3. [第三个重要句子或要点]

请确保你的分析准确、简洁，并且能够抓住新闻的核心内容。
"""
            },
            {
                "role": "user",
                "content": input
            }
        ],
        top_p=0.7,
        temperature=0.95,
        max_tokens=1024,
        tools=[{"type": "web_search", "web_search": {"search_result": True}}],
        stream=True
    )
    full_response = ""
    for chunk in response:
        content = chunk.delta.content if chunk.delta else ''
        full_response += content
    print("Received summary response.")
    return full_response

def stream_output(instance_id, output_queue):
    print(f"Thread {instance_id + 1} started.")
    response = get_response()
    output_queue.put((instance_id, response))
    print(f"Thread {instance_id + 1} completed.")

def rate_output(outputs):
    print("Starting rating of summaries...")
    rating_responses = []
    score_pattern = re.compile(r'<total_score>(\d+)</total_score>')
    
    for instance_id, output in outputs:
        print(f"Rating summary from instance {instance_id + 1}...")
        rating_response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "system",
                    "content": """
你是一位专业的新闻编辑和内容评估专家。请根据以下标准对给定的新闻摘要进行评分：

1. 准确性（1-10分）：摘要是否准确反映了原文的主要内容，没有误解或遗漏重要信息。
2. 简洁性（1-10分）：摘要是否简明扼要，避免了冗余信息，同时保留了关键点。
3. 结构性（1-10分）：摘要的结构是否清晰，各部分之间是否有逻辑连贯性。
4. 标题吸引力（1-10分）：生成的标题是否吸引人，能否准确反映文章主旨。

请为每个标准给出评分，并简要解释你的评分理由。最后给出总分，总分是四个分项的总和，请将总分用xml标签<total_score>和</total_score>包裹。

输出格式：

1. 准确性：[分数]
   理由：[简短解释]
2. 简洁性：[分数]
   理由：[简短解释]
3. 结构性：[分数]
   理由：[简短解释]
4. 标题吸引力：[分数]
   理由：[简短解释]

总分：<total_score>[总分]</total_score>
"""
                },
                {
                    "role": "user",
                    "content": f"新闻摘要: {output}"
                }
            ],
            top_p=0.7,
            temperature=0.95,
            max_tokens=1024,
            tools=[{"type": "web_search", "web_search": {"search_result": True}}],
            stream=False
        )
        if hasattr(rating_response, 'choices') and rating_response.choices:
            rating_content = rating_response.choices[0].message.content
            print(f"Rating content for instance {instance_id + 1}: {rating_content}")  # Debug print
            
            match = score_pattern.search(rating_content)
            if match:
                total_score = int(match.group(1))
                rating_responses.append((instance_id, total_score, output, rating_content))
                print(f"Instance {instance_id + 1} scored {total_score}.")
            else:
                print(f"Error: Could not parse scores for instance {instance_id + 1}")

    if not rating_responses:
        raise ValueError("No valid ratings were parsed.")
        
    best_instance = max(rating_responses, key=lambda x: x[1])
    print(f"Best summary is from instance {best_instance[0] + 1} with a score of {best_instance[1]}.")
    return best_instance

def create_image(title, pinyin, translation_en, translation_jp, description, output_path="output.svg"):
    print(f"Creating image at {output_path}...")
    try:
        # Create an SVG drawing
        dwg = svgwrite.Drawing(output_path, profile='tiny', size=(800, 1200))
        
        # Background color
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#f5f0e1'))
        
        # Add red circle
        dwg.add(dwg.circle(center=(50, 50), r=30, fill='#d9534f'))
        
        # Add blue square
        dwg.add(dwg.rect(insert=(700, 1100), size=(50, 50), fill='#5bc0de'))
        
        # Add title
        dwg.add(dwg.text("汉语新解", insert=(400, 100), text_anchor="middle", font_size="40px", font_family="Microsoft YaHei, sans-serif", fill="black"))
        
        # Add word
        dwg.add(dwg.text(title, insert=(400, 200), text_anchor="middle", font_size="60px", font_family="Microsoft YaHei, sans-serif", fill="black"))
        
        # Add pinyin
        dwg.add(dwg.text(pinyin, insert=(400, 300), text_anchor="middle", font_size="30px", font_family="Microsoft YaHei, sans-serif", fill="gray"))
        
        # Add English translation
        dwg.add(dwg.text(translation_en, insert=(400, 400), text_anchor="middle", font_size="30px", font_family="Microsoft YaHei, sans-serif", fill="gray"))
        
        # Add Japanese translation
        dwg.add(dwg.text(translation_jp, insert=(400, 450), text_anchor="middle", font_size="30px", font_family="Microsoft YaHei, sans-serif", fill="gray"))
        
        # Add description with word wrapping
        max_width = 700  # Maximum width for the text
        description_lines = wrap_text(dwg, description, max_width, font_size=25, font_family="Microsoft YaHei, sans-serif")
        y_position = 550
        for line in description_lines:
            dwg.add(dwg.text(line, insert=(50, y_position), font_size="25px", font_family="Microsoft YaHei, sans-serif", fill="black"))
            y_position += 40
        
        # Save the SVG file
        dwg.save()
        print("SVG file saved successfully.")
        
        # Check if file was created successfully
        if os.path.exists(output_path):
            print(f"SVG file successfully created at: {output_path}")
        else:
            print(f"Failed to create SVG file at: {output_path}")
    
    except Exception as e:
        print(f"An error occurred while creating the image: {str(e)}")

def wrap_text(dwg, text, max_width, font_size, font_family):
    lines = []
    current_line = ''
    for char in text:
        test_line = current_line + char
        # Estimate width based on character count (approximate for Chinese)
        if len(test_line) * (font_size * 0.6) > max_width:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    return lines

def main():
    print("Starting main process...")
    output_queue = queue.Queue()
    threads = []
    outputs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(3):
            threads.append(executor.submit(stream_output, i, output_queue))
            print(f"Submitted thread {i + 1} to executor.")

        # Collect and print streamed output
        while len(outputs) < 3:
            while not output_queue.empty():
                instance_id, output = output_queue.get()
                outputs.append((instance_id, output))
                print(f"Instance {instance_id + 1}: {output}")

    # Output the rating after streaming
    best_instance_id, best_score, best_output, rating_content = rate_output(outputs)
    print(f"Instance {best_instance_id + 1} 是最好的:")
    print(f"摘要内容: {best_output}")
    print(f"评分详情:\n{rating_content}")

    # Create an image with the best output
    title = input
    pinyin = ' '.join(lazy_pinyin(input, style=Style.TONE))
    description = best_output
    output_path = os.path.expanduser("~/Desktop/output.svg")
    print(f"Attempting to save SVG file to: {output_path}")
    create_image(title, pinyin, "", "", description, output_path=output_path)
    print("Main process completed.")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")  # Add this line
