from openai import OpenAI

DEFAULT_PROMPT = """请你作为项目经理的角色，判断变动、更新的内容是否需要人工进行 review，具体规则如下，结果以 JSON 格式返回，字段包括 review_needed、changed_content 和 review_reason。
1. 若更新内容、变动内容中涉及与安全相关的信息(如 CVE 漏洞、安全漏洞、OpenSSL 等版本升级)，则无条件让人工进行 review。
2. 若更新内容、变动内容中仅文档内容更新、新增、删除文件或文档内容，则无需人工进行 review。
3. 其余情况请自行判断是否需要人工进行 review。
4. 如果需要，请总结出变动内容 changed_content 并给出 review 的原因作为 review_reason，同时 review_needed 为 true。
5. 如果不需要，也请总结出变动内容 changed_content，给出不需要 review 的原因作为 review_reason，同时 review_needed 为 false。
6. 不要过度思考，直接给出判断结果。
"""
# DEFAULT_API_URL = "https://ark.cn-beijing.volces.com/api/v3"

class AiClient:
    def __init__(self, model: str, diff: str, api_token: str, base_url: str | None = None):
        self.client = OpenAI( 
            base_url=base_url,
            api_key=api_token
        )
        self.model = model
        self.diff = diff

    def get_response(self):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": [{"type": "text", "text": DEFAULT_PROMPT}, {"type": "text", "text": self.diff}]},
            ],
        )
        return response.choices[0].message.content