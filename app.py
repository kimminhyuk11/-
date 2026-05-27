import streamlit as st
from google import genai
from google.genai import types

# 페이지 설정
st.set_page_config(
    page_title="인생상담 챗봇",
    page_icon="💬",
    layout="centered"
)

st.title("💬 인생상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반 상담 챗봇")

# API 키 불러오기
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("GOOGLE_API_KEY가 설정되지 않았습니다.")
    st.stop()

# Gemini 클라이언트 생성
client = genai.Client(api_key=api_key)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요. "
                "삶, 진로, 인간관계, 감정 고민 등을 편하게 이야기해 주세요."
            )
        }
    ]

# 기존 채팅 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
prompt = st.chat_input("고민이나 질문을 입력하세요")

if prompt:
    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            # Gemini용 대화 기록 변환
            history = []

            for msg in st.session_state.messages[:-1]:
                role = "model" if msg["role"] == "assistant" else "user"

                history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg["content"])]
                    )
                )

            # 현재 사용자 입력 포함
            history.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=history,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    top_p=0.95,
                    max_output_tokens=1024,
                    system_instruction=(
                        "너는 따뜻하고 공감 능력이 뛰어난 인생상담 챗봇이다. "
                        "사용자의 감정을 존중하고 현실적이고 균형 잡힌 조언을 제공해라. "
                        "위험하거나 극단적인 선택은 권장하지 말고, "
                        "필요 시 전문가 상담도 권유해라."
                    )
                )
            )

            answer = response.text

        except Exception as e:
            answer = (
                "죄송해요. 응답 생성 중 오류가 발생했습니다.\n\n"
                f"오류 내용: {str(e)}"
            )

        # 응답 출력
        message_placeholder.markdown(answer)

    # 응답 저장
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# 사이드바
with st.sidebar:
    st.header("설정")

    if st.button("대화 초기화"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "안녕하세요. "
                    "삶, 진로, 인간관계, 감정 고민 등을 편하게 이야기해 주세요."
                )
            }
        ]
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        ### 사용 모델
        - Gemini 2.5 Flash Lite

        ### 기능
        - 채팅 기록 유지
        - 오류 처리
        - 상담 스타일 응답
        """
    )
