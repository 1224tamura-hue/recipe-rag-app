from typing import Any, Dict, List
import re

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from src.config import Settings

STOPWORDS = {
    "おすすめ", "料理", "レシピ", "あります", "ください",
    "教えて", "作り方", "どう", "どんな", "今日", "ダイエット",
    "食べ", "食事", "健康", "カロリー",
}


def build_prompt() -> ChatPromptTemplate:
    system = (
        "あなたは管理栄養士の知識を持つダイエットレシピアドバイザーです。"
        "必ず与えられたコンテキスト（参照レシピ）だけに基づいて回答してください。\n\n"
        "【最重要ルール】\n"
        "1) コンテキストに書かれていない食材・調味料・調理法・料理名を新規に作ってはいけません。\n"
        "2) 質問の条件がコンテキストに見当たらない場合は「該当するレシピは参照データに存在しません」と明確に答えてください。\n"
        "3) 断定せず、根拠がある範囲のみ述べてください。\n"
        "4) 個人の重篤な疾患に関する医療的判断は行わないこと。\n\n"
        "【管理栄養士視点での回答方針】\n"
        "- このレシピがなぜダイエットに有効か（科学的根拠を簡潔に）\n"
        "- PFCバランスのコメント（たんぱく質・脂質・炭水化物の観点）\n"
        "- 安全な摂取量・推奨頻度のアドバイス\n"
        "- 組み合わせると効果的な他のレシピや食材（コンテキスト内から）\n"
        "- 栄養素を守る調理のコツ（加熱しすぎない、など）\n\n"
        "【出力フォーマット】\n"
        "- 判定: （該当あり / 該当なし）\n"
        "- 推奨レシピ: レシピ名（PFC: P__g / F__g / C__g、__kcal）\n"
        "- 栄養アドバイス: ...\n"
        "- PFCバランス解説: ...\n"
        "- 推奨頻度: ...\n"
        "- 根拠: 参照レシピ番号（例: [1], [2]）\n"
    )
    user = (
        "【ユーザープロフィール】\n{profile_context}\n\n"
        "【質問】\n{question}\n\n"
        "【参照レシピ（コンテキスト）】\n{context}\n"
    )
    return ChatPromptTemplate.from_messages([("system", system), ("user", user)])


def format_context(docs: List[Document]) -> str:
    parts = []
    for i, d in enumerate(docs, start=1):
        title = d.metadata.get("title", f"doc{i}")
        kcal = d.metadata.get("calories_kcal", "")
        p = d.metadata.get("protein_g", "")
        f_val = d.metadata.get("fat_g", "")
        c = d.metadata.get("carbs_g", "")
        nutrition = f"（{kcal}kcal / P:{p}g F:{f_val}g C:{c}g）" if kcal else ""
        text = d.page_content
        snippet = text[:700] + ("..." if len(text) > 700 else "")
        parts.append(f"---\n[{i}] {title}{nutrition}\n{snippet}")
    return "\n".join(parts)


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _extract_keywords(question: str) -> list[str]:
    q = _normalize(question)
    words = re.findall(r"[ぁ-んァ-ン一-龥a-zA-Z0-9]{2,}", q)
    words = [w for w in words if w not in STOPWORDS]
    return list(dict.fromkeys(words))


def _doc_text_for_match(d: Document) -> str:
    title = str(d.metadata.get("title", ""))
    tags = str(d.metadata.get("tags", ""))
    body = d.page_content
    return _normalize("\n".join([title, tags, body]))


def _build_joined_text(docs: list[Document]) -> str:
    return _normalize("\n".join([_doc_text_for_match(d) for d in docs]))


def answer_question(
    question: str,
    retrieved_docs: List[Document],
    settings: Settings,
    temperature: float = 0.2,
    profile_context: str = "プロフィール未設定",
) -> Dict[str, Any]:
    if len(retrieved_docs) == 0:
        return {
            "answer": "判定: 該当なし\n回答: 該当するレシピは参照データに存在しません。\n根拠: 参照レシピが取得できませんでした。",
            "sources": [],
        }

    keywords = _extract_keywords(question)
    joined = _build_joined_text(retrieved_docs)
    hits = [k for k in keywords if _normalize(k) in joined]

    if len(keywords) >= 2 and len(hits) == 0:
        return {
            "answer": (
                "判定: 該当なし\n"
                "回答: 該当するレシピは参照データに存在しません。\n"
                "根拠: 参照レシピ内に質問条件に一致する記述がありません。"
            ),
            "sources": [
                {
                    "title": d.metadata.get("title", "unknown"),
                    "snippet": d.page_content[:200] + ("..." if len(d.page_content) > 200 else ""),
                    "calories_kcal": d.metadata.get("calories_kcal", 0),
                    "protein_g": d.metadata.get("protein_g", 0),
                    "fat_g": d.metadata.get("fat_g", 0),
                    "carbs_g": d.metadata.get("carbs_g", 0),
                    "recipe_id": d.metadata.get("id", ""),
                }
                for d in retrieved_docs
            ],
        }

    llm = ChatOpenAI(model=settings.chat_model, temperature=temperature)
    prompt = build_prompt()
    context = format_context(retrieved_docs)

    messages = prompt.format_messages(
        question=question,
        context=context,
        profile_context=profile_context,
    )
    resp = llm.invoke(messages)

    sources = []
    for d in retrieved_docs:
        sources.append({
            "title": d.metadata.get("title", "unknown"),
            "snippet": d.page_content[:400] + ("..." if len(d.page_content) > 400 else ""),
            "calories_kcal": d.metadata.get("calories_kcal", 0),
            "protein_g": d.metadata.get("protein_g", 0),
            "fat_g": d.metadata.get("fat_g", 0),
            "carbs_g": d.metadata.get("carbs_g", 0),
            "recipe_id": d.metadata.get("id", ""),
        })

    return {"answer": resp.content, "sources": sources}
