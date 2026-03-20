#app.py

import streamlit as st
from datetime import date, timedelta

# -----------------------------
# 1) 샘플 데이터셋(예시)
# -----------------------------
DATASET = {
    "museum": {
        "name": "한빛 시립박물관",
        "tagline": "시간을 걷는 전시, 이야기를 듣는 해설",
        "image_url": "https://images.unsplash.com/photo-1528909514045-2fa4ac7a08ba?auto=format&fit=crop&w=1600&q=80",
        "hours": "10:00 ~ 18:00 (월요일 휴관)",
        "location": "전주시",
        "phone": "063-000-0000",
    },
    "docent_services": [
        {
            "id": "DOC-001",
            "name": "상설전 해설 (60분)",
            "duration_min": 60,
            "capacity": 20,
            "price_per_person": 8000,
            "times": ["10:30", "13:30", "15:30"],
            "notes": "초등 고학년 이상 권장. 단체 예약 가능.",
        },
        {
            "id": "DOC-002",
            "name": "특별전 집중 해설 (90분)",
            "duration_min": 90,
            "capacity": 15,
            "price_per_person": 12000,
            "times": ["11:00", "14:00"],
            "notes": "전시 이해를 돕는 Q&A 시간이 포함됩니다.",
        },
        {
            "id": "DOC-003",
            "name": "어린이 가족 해설 (45분)",
            "duration_min": 45,
            "capacity": 12,
            "price_per_group": 30000,  # 그룹당 가격 예시(최대 4인)
            "times": ["10:00", "16:00"],
            "notes": "가족 단위(최대 4인) 권장. 어린이 눈높이 설명.",
        },
    ],
}

# -----------------------------
# 6) UI
# -----------------------------
def main():
    #>역할: 페이지 전체 레이아웃을 구성하고, 폼/챗봇 입력을 연결
    #>구성
    # st.set_page_config(...)
    # init_state()
    # left, right = st.columns(...)
    # left: 이미지 카드 + 예약 폼 + 저장/초기화 + 예약 목록
    # right: 채팅 출력(render_chat_bubbles) + 입력(st.chat_input)
    #>가장 중요한 포인트
    # st.chat_input으로 메시지 입력 → chat_and_maybe_fill_draft 호출
    # draft가 바뀌면 왼쪽 폼에 즉시 반영되도록 st.rerun() 사용

    st.set_page_config(page_title="박물관 해설 예약", layout="wide")

    if "draft" not in st.session_state: #예약입력 폼 데이터가 없는 경우
        st.session_state.draft = {
            "name": "",
            "phone": "",
            "email": "",
            "visit_date": date.today(),
            "service_id": None,
            "time": None,
            "people": 1,
            "memo": "",
        }
        
    draft = st.session_state.draft

    m = DATASET["museum"]
     
    st.title("박물관 해설 서비스 예약 시스템")
    st.caption("")

    left, right = st.columns([1, 1.2], gap="large")

    # ---- 왼쪽: 이미지 + 예약 폼
    with left:
        st.markdown(
            f"""
            <div style="padding:16px;border-radius:16px;border:1px solid #eee;">
              <div style="font-size:22px;font-weight:700;margin-bottom:6px;">{m['name']}</div>
              <div style="color:#555;margin-bottom:10px;">{m['tagline']}</div>
              <img src="{m['image_url']}" style="width:100%;border-radius:14px;object-fit:cover;max-height:260px;" />
              <div style="margin-top:10px;color:#444;font-size:14px;line-height:1.6;">
                <b>운영시간</b>: {m['hours']}<br/>
                <b>위치</b>: {m['location']}<br/>
                <b>문의</b>: {m['phone']}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.subheader("해설 예약 폼")

        c1, c2 = st.columns(2)
        with c1:
            draft["name"] = st.text_input("예약자 이름", value=draft["name"], placeholder="홍길동")
        with c2:
            draft["phone"] = st.text_input("연락처", value=draft["phone"], placeholder="010-0000-0000")

        draft["email"] = st.text_input("이메일(선택)", value=draft["email"], placeholder="example@email.com")

        # 날짜 선택(다음 14일)
        today = date.today()
        days = [today + timedelta(days=i) for i in range(14)]
        
        default_idx = 0 #14일치 중 선택된 날짜가 있다면 인덱스 반환 없다면 0
        draft["visit_date"] = st.selectbox(
            "방문 날짜",  #초기 옵션
            options=days, #옵션 목록
            index=default_idx,  #초기 선택이 있는 경우 
            format_func=lambda d: d.strftime("%Y-%m-%d (%a)"),  #date 리스트 날짜 포맷으로 변경
        )

        # 서비스 선택
        svc_labels = ["선택하세요"] + [f"{s['name']} ({s['id']})" for s in DATASET["docent_services"]] #해설 서비스 옵션 목록 리스트 작성

        picked_svc = st.selectbox("해설 프로그램", svc_labels, index=svc_labels.index("선택하세요")) #해설 프로그램 콤보 박스 출력 옵션은 svc_labels, 선택 인덱스는 current_label과 일치하는 인덱스 / 이후 항목 선택시 picked_svc에 대입

        # 서비스별 회차/정원/가격 힌트
        times = []
        capacity = None
        notes = ""
        price_hint = ""
        is_group = False

        t1, t2 = st.columns(2)
        with t1:
            draft["time"] = st.selectbox(
                "회차(시간)",
                options=["선택하세요"] + times,
                index=0 , #시간 정보가 없으면 선택하세요 지정 있으면 인덱스+1 해서 선택
            )

        with t2:
            draft["people"] = st.number_input(
                "인원",
                min_value=1,
                max_value=20,
                value=min(int(draft["people"]), 20),
                step=1,
            )

        draft["memo"] = st.text_area("요청사항(선택)", value=draft["memo"])

        st.markdown(f"### 예상 결제금액: **000**")

        b1, b2 = st.columns(2)
        with b1:
            st.button("예약 저장", use_container_width=True) #  use_container_width=True ->버튼을 부모 컨테이너 너비 맞춤 / 버튼 출력 클릭 시 if 실행

        with b2:
            st.button("초안 초기화", use_container_width=True)

        with st.expander("저장된 예약 보기"): #아코디언 출력 
            st.caption("아직 저장된 예약이 없습니다.")

    # ---- 오른쪽: 챗봇(최근 5개 + 입력 하단 + 예약해줘 → 폼 채움)
    with right:
        st.subheader("해설 예약 도우미 챗봇")

        user_text = st.chat_input("예) 내일 14:00 특별전 2명 예약해줘 / 상설전 예약 가능해?")



if __name__ == "__main__":  #직접 실행 시 main 호출
    main()