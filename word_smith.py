from zhipuai import ZhipuAI
import httpx
import concurrent.futures
import queue
import threading
import time  # Add this import
import re  # Add this import
from PIL import Image, ImageDraw, ImageFont  # Add this import
import svgwrite  # Add this import
from pypinyin import lazy_pinyin, Style  # Add Style for tone marks

input = "内卷"

# Create a custom httpx client without a proxy
custom_http_client = httpx.Client(trust_env=False)

client = ZhipuAI(
    api_key=os.getenv('ZHIPUAI_API_KEY'),
    http_client=custom_http_client
)

def get_response():
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "system",
                "content": """
你是一位新汉语老师，名叫新汉语老师。你有以下特点：
- 风格：你擅长模仿 Oscar Wilde、鲁迅和林语堂的风格。
- 擅长：你能够一针见血地指出问题的核心。
- 表达：你喜欢用隐喻的方式来表达观点。
- 批判：你擅长用讽刺幽默的方式进行批判。

当用户输入一个汉语词汇时，你会用一个特殊视角来解释这个词汇。你的解释应该是：
- 一句话表达
- 使用隐喻
- 一针见血
- 辛辣讽刺
- 抓住本质

例如，当用户输入"委婉"时，你可以这样解释："刺向他人时, 决定在剑刃上撒上止痛药。"
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

    # Assuming the response contains description only
    translation_response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "system",
                "content": "You are a translator."
            },
            {
                "role": "user",
                "content": f"Translate the following word to English in one word or a short phrase: {input}"  # Updated prompt for brevity
            }
        ],
        top_p=0.7,
        temperature=0.7,
        max_tokens=16,  # Reduced to ensure concise translation
        tools=[{"type": "web_search", "web_search": {"search_result": True}}],
        stream=False
    )
    if translation_response.get('message'):
        translation_en = translation_response['message']['content'].strip()
    else:
        translation_en = "Translation not available."
    
    # Add Japanese translation
    translation_jp_response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "system",
                "content": "You are a translator."
            },
            {
                "role": "user",
                "content": f"Translate the following word to Japanese in one word or a short phrase: {input}"
            }
        ],
        top_p=0.7,
        temperature=0.7,
        max_tokens=16,
        tools=[{"type": "web_search", "web_search": {"search_result": True}}],
        stream=False
    )
    if translation_jp_response.get('message'):
        translation_jp = translation_jp_response['message']['content'].strip()
        # Extract only the Japanese translation after the hyphen or newline
        translation_jp = re.split(r'[-\n]', translation_jp, maxsplit=1)[-1].strip()
    else:
        translation_jp = "Translation not available."
    
    description = full_response  # Description from the first response
    return translation_en, translation_jp, description  # Updated return

def stream_output(instance_id, output_queue):
    response = get_response()
    output_queue.put((instance_id, response))

def rate_output(outputs):
    rating_responses = []
    score_pattern = re.compile(r'<total_score>(\d+)</total_score>')
    
    for instance_id, output in outputs:
        rating_response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "system",
                    "content": """
你是一位新汉语老师，名叫新汉语老师。你有以下特点：
- 风格：你擅长模仿 Oscar Wilde、鲁迅和林语堂的风格。
- 擅长：你能够一针见血地指出问题的核心。
- 表达：你喜欢用隐喻的方式来表达观点。
- 批判：你擅长用讽刺幽默的方式进行批判。

请根据以下标准对给定的输出进行评分：
- 清晰度
- 黑色幽默
- 意料之外

评分范围是1到10，10是最高分。请给出每个标准的评分，并解释你的评分理由。最后给个总分，总分是将三个分项相加，请将总分用xml标签<total_score>和</total_score>包裹。

输出案例：

<example_output>
- 清晰度：8
理由：解释清晰，逻辑清晰，表达清晰
- 黑色幽默：9
理由：使用黑色幽默，让解释更加有趣
- 意料之外：7
理由：意料之外，让解释更加出乎意料
总分：<total_score>24</total_score>
</example_output>
"""
                },
                {
                    "role": "user",
                    "content": f"输出: {output[1]}"  # Only the description
                }
            ],
            top_p=0.7,
            temperature=0.95,
            max_tokens=1024,
            tools=[{"type": "web_search", "web_search": {"search_result": True}}],
            stream=False
        )
        if hasattr(rating_response, 'choices') and rating_response.choices:
            rating_content = rating_response.choices[0].text
            print(f"Rating content for instance {instance_id + 1}: {rating_content}")  # Debug print
            
            match = score_pattern.search(rating_content)
            if match:
                total_score = int(match.group(1))
                rating_responses.append((instance_id, total_score, output))  # output is (translation, description)
            else:
                print(f"Error: Could not parse scores for instance {instance_id + 1}")

    if not rating_responses:
        raise ValueError("No valid ratings were parsed.")
        
    best_instance = max(rating_responses, key=lambda x: x[1])
    return best_instance

def create_image(title, pinyin, translation_en, translation_jp, description, output_path="output.svg"):
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
    output_queue = queue.Queue()
    threads = []
    outputs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(3):
            threads.append(executor.submit(stream_output, i, output_queue))

        # Collect and print streamed output
        while len(outputs) < 3:
            while not output_queue.empty():
                instance_id, output = output_queue.get()
                outputs.append((instance_id, output))
                print(f"Instance {instance_id + 1}: {output}")

    # Output the rating after streaming
    best_instance_id, best_score, best_output = rate_output(outputs)
    print(f"Instance {best_instance_id + 1} 是最好的: <answer>{best_output}</answer>")

    # Create an image with the best output
    title = input
    pinyin = ' '.join(lazy_pinyin(input, style=Style.TONE))  # Add tone marks to pinyin
    translation_en, translation_jp, description = best_output  # Unpack correctly
    create_image(title, pinyin, translation_en, translation_jp, description, output_path="C:/Users/gbyha/Downloads/output.svg")

def translate_text(language, text):
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": f"Translate the following word to {language} in one word or a short phrase: {text}"}
        ],
        # ... existing parameters ...,
        stream=False
    )
    content = response.choices[0].text.strip() if response.choices else "Translation not available."
    return content

# Use the function
translation_en = translate_text("English", input)
translation_jp = translate_text("Japanese", input)

if __name__ == "__main__":
    main()