import re
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL, USE_LLM

class IntentAgent:
    def run(self, message: str) -> str:
        text = message.lower()
        if any(k in text for k in ["退款", "退货", "refund"]):
            return "refund"
        if any(k in text for k in ["订单", "物流", "快递", "发货", "order", "delivery"]):
            return "order"
        if any(k in text for k in ["投诉", "差评", "生气", "人工", "客服"]):
            return "human"
        if any(k in text for k in ["优惠券", "券", "折扣"]):
            return "coupon"
        return "general"

class QualityAgent:
    def run(self, message: str, answer: str) -> tuple[bool, str]:
        risky_words = ["投诉", "差评", "律师", "报警", "赔偿", "强烈不满"]
        need_human = any(w in message for w in risky_words)
        if len(answer.strip()) < 10:
            need_human = True
            answer += "\n\n这个问题建议转人工客服进一步处理。"
        return need_human, answer

class AnswerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def run(self, message: str, intent: str, docs: list[str], history: list[dict]) -> str:
        if USE_LLM and self.client:
            return self._llm_answer(message, intent, docs, history)
        return self._rule_answer(message, intent, docs)

    def _llm_answer(self, message: str, intent: str, docs: list[str], history: list[dict]) -> str:
        context = "\n\n".join(docs) if docs else "暂无可用知识库内容。"
        system_prompt = f"""
你是企业智能客服。请基于知识库回答用户问题。
要求：
1. 回答准确、友好、简洁。
2. 不要编造知识库不存在的政策。
3. 涉及投诉、金额争议、强烈不满时建议转人工。
4. 当前识别意图：{intent}

知识库：
{context}
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": message})

        resp = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.3
        )
        return resp.choices[0].message.content or "抱歉，我暂时无法回答这个问题。"

    def _rule_answer(self, message: str, intent: str, docs: list[str]) -> str:
        doc_text = "\n".join(docs)
        order_no = re.search(r"OD\d+", message, re.IGNORECASE)
        if intent == "order":
            if order_no:
                return f"我已识别到订单号 {order_no.group(0)}。当前 Demo 未连接真实订单系统，正式版本可自动调用订单接口查询物流、发货和售后状态。"
            return "请提供订单号，我可以帮你查询发货、物流或售后状态。"
        if intent == "refund":
            return "根据售后规则，商品签收后 7 天内，若未使用且不影响二次销售，可以申请无理由退款。若存在质量问题，请提供照片或视频，平台会优先审核。"
        if intent == "coupon":
            return "优惠券无法使用通常是因为未达到门槛、商品不支持、优惠券过期，或账户不符合活动条件。你可以把优惠券截图或活动名称发给我继续判断。"
        if intent == "human":
            return "理解你的情况。这个问题可能涉及投诉或复杂售后，我建议为你转接人工客服，并创建工单继续处理。"
        if docs:
            return f"我查到以下相关信息：\n\n{doc_text}\n\n你可以继续补充订单号或具体问题，我会进一步判断。"
        return "我理解你的问题。当前知识库中没有找到完全匹配的信息，建议补充订单号、商品名称或问题截图，我可以继续帮你判断。"

class CustomerServiceOrchestrator:
    def __init__(self, kb):
        self.intent_agent = IntentAgent()
        self.answer_agent = AnswerAgent()
        self.quality_agent = QualityAgent()
        self.kb = kb

    def run(self, message: str, history: list[dict]) -> dict:
        intent = self.intent_agent.run(message)
        docs = self.kb.search(message, top_k=3)
        answer = self.answer_agent.run(message, intent, docs, history)
        need_human, checked_answer = self.quality_agent.run(message, answer)
        if intent == "human":
            need_human = True
        return {
            "answer": checked_answer,
            "intent": intent,
            "need_human": need_human,
            "retrieved_docs": docs
        }
