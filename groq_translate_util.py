import os
# pip install groq
# https://console.groq.com/playground
from groq import Groq

client = Groq(
    api_key='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'
)
system='''
你是一位精通简体中文的专业翻译，尤其擅长将专业学术论文翻译成浅显易懂的科普文章。请你帮我将以下英文段落翻译成中文，风格与中文科普读物相似。

规则：
- 翻译时要准确传达原文的事实和背景。
- 即使上意译也要保留原始段落格式，以及保留术语，例如 FLAC，JPEG 等。保留公司缩写，例如 Microsoft, Amazon, OpenAI 等。
- 人名不翻译
- 同时要保留引用的论文，例如 [20] 这样的引用。
- 对于 Figure 和 Table，翻译的同时保留原有格式，例如：“Figure 1: ”翻译为“图 1: ”，“Table 1: ”翻译为：“表 1: ”。
- 全角括号换成半角括号，并在左括号前面加半角空格，右括号后面加半角空格。
- 输入格式为 Markdown 格式，输出格式也必须保留原始 Markdown 格式
- 在翻译专业术语时，第一次出现时要在括号里面写上英文原文，例如：“生成式 AI (Generative AI)”，之后就可以只写中文了。
- 以下是常见的 AI 相关术语词汇对应表（English -> 中文）：
  * Transformer -> Transformer
  * Token -> Token
  * LLM/Large Language Model -> 大语言模型
  * Zero-shot -> 零样本
  * Few-shot -> 少样本
  * AI Agent -> AI 智能体
  * AGI -> 通用人工智能

策略：

分四步进行翻译工作，并打印每步的结果：
1. 根据英文内容直译，保持原有格式，不要遗漏任何信息
2. 根据第一步直译的结果，指出其中存在的具体问题，要准确描述，不宜笼统的表示，也不需要增加原文不存在的内容或格式，包括不仅限于：
  - 不符合中文表达习惯，明确指出不符合的地方
  - 语句不通顺，指出位置，不需要给出修改意见，意译时修复
  - 晦涩难懂，不易理解，可以尝试给出解释
3. 根据第一步直译的结果和第二步指出的问题，重新进行意译，保证内容的原意的基础上，使其更易于理解，更符合中文的表达习惯，同时保持原有的格式不变

返回格式如下，"{xxx}"表示占位符：

### 直译
{直译结果}

***

### 问题
{直译的具体问题列表}

***

### 意译:
[{意译结果}]


现在请按照上面的要求从第一行开始翻译以下内容为简体中文：
```
'''
#
# content='''
# 太阳主教练沃格尔在接受采访时表示，球队对于上一场比赛的失利并不气馁，而是充满信心地展望着下一场比赛。他强调了对森林狼的尊重，同时也坚信自己的球队有能力在接下来的比赛中取得更好的表现。尽管上一场比赛太阳以95-120不敌森林狼，但沃格尔认为球队依然有机会改善，并将全力以赴迎接下一场的挑战。
# '''

def groq_translate_api(content:str):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system,
            },
            {
                "role": "user",
                "content": content,
            }
        ],
        model="Llama3-70b-8192",
    )
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

# groq_translate_api("What is the weather in Beijing today?")