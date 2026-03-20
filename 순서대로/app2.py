#app.py

import streamlit as st
from datetime import date, timedelta, datetime  #import 확인하기

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

###########################함수 추가 start####################################
# -----------------------------
# 2) 유틸/상태
# -----------------------------
def init_state():
    #>역할: Streamlit이 rerun 될 때마다 상태가 날아가지 않도록 st.session_state 기본값 세팅
    
    #>세팅하는 상태
    #  chat: 채팅 메시지 리스트(assistant/user 역할과 content)
    #  reservations: 저장된 예약 목록(메모리 저장)
    #  draft: 왼쪽 폼에 연결된 “예약 초안”(자동 입력 대상)

    #>포인트
    #  Streamlit은 입력/버튼 누를 때마다 스크립트 전체가 다시 실행되므로, 상태는 session_state로 유지해야 합니다.

    if "reservations" not in st.session_state: #저장된 예약이 없는 경우
        st.session_state.reservations = []

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


# -----------------------------
# 3) 예약 계산/검증/저장
# -----------------------------
def compute_price(draft: dict) -> int:
    #>역할: 현재 draft(초안)에 기반해 예상 금액 계산
    #>입력: draft (service_id, people 등을 참고)
    #>출력: 정수 금액(원)
    #>동작
    # 선택한 프로그램이 price_per_person이면 인당가격 * 인원
    # price_per_group이면 그룹당가격(인원은 제한 체크만 사용)

    # 예약 입력 창에서 선택된 해설 서비스와 일치하는 데이터셋 검색
    svc = next((x for x in DATASET["docent_services"] if x["id"] == draft.get("service_id")), None)
    if not svc: #일치 서비스가 없는 경우
        return 0

    people = max(int(draft.get("people", 1)), 1) #입력 인원 구하기(최소 한명)

    if "price_per_person" in svc: #svc에 price_per_person 있는 경우
        return svc["price_per_person"] * people #사람당 금액 만큼 인원 곱하여 반환
    if "price_per_group" in svc:  #svc에 price_per_group 있는 경우 
        return svc["price_per_group"] #그룹 금액 반환
    return 0



def validate_reservation(draft: dict) -> tuple[bool, str]:
    
    #>역할: “예약 저장” 전에 필수값/제약조건 검증
    #>입력: draft
    #>출력
    # True/False
    # 실패 시 사용자에게 보여줄 에러 메시지
    #>검증 항목
    # 이름/연락처/프로그램/회차 필수
    # 가족 해설(DOC-003 같은 그룹형) 인원 최대 4명
    # 인당형은 정원(capacity) 초과 금지
    # 선택한 시간(time)이 해당 프로그램 times 목록에 실제로 존재하는지 확인

    if not draft.get("name", "").strip(): #이름값이 없다면
        return False, "예약자 이름을 입력해 주세요."
    if not draft.get("phone", "").strip(): #연락처값이 없다면
        return False, "연락처를 입력해 주세요."
    if not draft.get("service_id"): #해설서비스값이 없다면
        return False, "해설 프로그램을 선택해 주세요."
    if not draft.get("time"): #선택회차값이 없다면
        return False, "해설 회차(시간)를 선택해 주세요."

    #선택된 서비스 데이터셋 가져오기
    svc = next((x for x in DATASET["docent_services"] if x["id"] == draft["service_id"]), None)
    if svc:
        if "price_per_group" in svc and int(draft["people"]) > 4: #그룹예약을 골랐고 4명 초과 선택한 경우
            return False, "가족 해설은 최대 4인까지 예약 가능합니다(예시)."
        if "price_per_person" in svc and int(draft["people"]) > int(svc["capacity"]): #선택 인원이 정원보다 큰 경우
            return False, f"정원을 초과했습니다. (정원: {svc['capacity']}명)"

        # 회차 유효성(서비스 times에 포함되는지)
        if draft["time"] not in svc["times"]: #선택 시간이 선택서비스에 유효하지 않는 경우
            return False, f"선택한 회차가 유효하지 않습니다. (가능 회차: {', '.join(svc['times'])})"

    return True, "" #전부 문제 없으면 true,"" 반환

def save_reservation(draft: dict) -> dict:
    #>역할: 예약 확정 저장(현재는 메모리 저장)
    #>입력: draft
    #>출력: 저장된 예약 record(dict)
    #>동작
    # saved_at를 기록
    # total_price 계산해서 함께 저장
    # st.session_state.reservations.append(record)
    #>포인트(확장 과제)
    # 여기만 바꾸면 CSV/DB/구글시트 저장으로 쉽게 확장 가능합니다.

    total = compute_price(draft)  #입력값 전달해서 총 금액 가져오기
    record = {
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": draft["name"],
        "phone": draft["phone"],
        "email": draft["email"],
        "visit_date": str(draft["visit_date"]),
        "service_id": draft["service_id"],
        "time": draft["time"],
        "people": int(draft["people"]),
        "memo": draft["memo"],
        "total_price": total,
    }
    st.session_state.reservations.append(record) #session에 예약 정보 record 딕셔너리 저장
    return record #예약 정보 딕셔너리 반환


###########################함수 추가 end ####################################

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

    ##############################여기부터#############################
    # if "draft" not in st.session_state: #예약입력 폼 데이터가 없는 경우
    #     st.session_state.draft = {
    #         "name": "",
    #         "phone": "",
    #         "email": "",
    #         "visit_date": date.today(),
    #         "service_id": None,
    #         "time": None,
    #         "people": 1,    
    #         "memo": "",
    #     }
    
    init_state()    
    ##############################여기까지#############################
   
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
        
        #default_idx = 0 #14일치 중 선택된 날짜가 있다면 인덱스 반환 없다면 0
        ##############################여기부터#############################
        default_idx = days.index(draft["visit_date"]) if draft["visit_date"] in days else 0 #14일치 중 선택된 날짜가 있다면 인덱스 반환 없다면 0
        ##############################여기까지#############################
        
        draft["visit_date"] = st.selectbox(
            "방문 날짜",  #초기 옵션
            options=days, #옵션 목록
            index=default_idx,  #초기 선택이 있는 경우 
            format_func=lambda d: d.strftime("%Y-%m-%d (%a)"),  #date 리스트 날짜 포맷으로 변경
        )

        # 서비스 선택
        svc_labels = ["선택하세요"] + [f"{s['name']} ({s['id']})" for s in DATASET["docent_services"]] #해설 서비스 옵션 목록 리스트 작성
        
        ##############################여기부터#############################
        current_label = "선택하세요" #현재 라벨
        if draft["service_id"]: #선택 서비스가 있는 경우
            found = next((x for x in DATASET["docent_services"] if x["id"] == draft["service_id"]), None) #일치하는 서비스 찾기
            if found: #찾았으면
                current_label = f"{found['name']} ({found['id']})"  #현재 라밸 변경


        #picked_svc = st.selectbox("해설 프로그램", svc_labels, index=svc_labels.index("선택하세요")) #해설 프로그램 콤보 박스 출력 옵션은 svc_labels, 선택 인덱스는 current_label과 일치하는 인덱스 / 이후 항목 선택시 picked_svc에 대입
        picked_svc = st.selectbox("해설 프로그램", svc_labels, index=svc_labels.index(current_label)) #해설 프로그램 콤보 박스 출력 옵션은 svc_labels, 선택 인덱스는 current_label과 일치하는 인덱스 / 이후 항목 선택시 picked_svc에 대입
        
        if picked_svc != "선택하세요": # 선택항목이 "선택하세요"가 아니면
            draft["service_id"] = picked_svc.split("(")[-1].replace(")", "").strip() #선택 항목에서 service_id 분리하여 저장
        else:
            draft["service_id"] = None  # 선택하세요 인 경우 None 저장
        ##############################여기까지#############################
        
        # 서비스별 회차/정원/가격 힌트
        times = []
        capacity = None
        notes = ""
        price_hint = ""
        is_group = False

        ##############################여기부터#############################
        if draft["service_id"]: #선택항목이 있는 경우 선택 예시 정보 와 선택 회차, 인원 정보 항목 데이터 셋팅
            svc = next((x for x in DATASET["docent_services"] if x["id"] == draft["service_id"]), None)
            if svc:
                times = svc["times"]
                capacity = svc["capacity"]
                notes = svc["notes"]
                if "price_per_person" in svc:
                    price_hint = f"1인 {svc['price_per_person']:,}" # currency : 금액 포맷팅
                elif "price_per_group" in svc:
                    price_hint = f"1그룹 {svc['price_per_group']:,}(최대 4인 예시)"
                    is_group = True
        ##############################여기까지#############################
        
        t1, t2 = st.columns(2)
        with t1:
            draft["time"] = st.selectbox(
                "회차(시간)",
                options=["선택하세요"] + times,
                ##############################여기부터#############################
                #index=0 , #시간 정보가 없으면 선택하세요 지정 있으면 인덱스+1 해서 선택
                index=0 if draft["time"] not in times else (times.index(draft["time"]) + 1), #시간 정보가 없으면 선택하세요 지정 있으면 인덱스+1 해서 선택 (0번은 '선택하세요')
                ##############################여기까지#############################
            )
            
            ##############################여기부터#############################
            if draft["time"] == "선택하세요":
                draft["time"] = None  # 선택 시간이 선택하세요 이면 time -> None
            ##############################여기까지#############################
                
        with t2:
            ##############################여기부터#############################
            if is_group:    #그룹 신청 인 경우 
                draft["people"] = st.number_input(
                    "인원(최대 4인)",
                    min_value=1,
                    max_value=4,
                    value=min(int(draft["people"]), 4), #입력 인원이 4보다 커도 4명으로 컷팅
                    step=1,
                )
            else:    #그룹 신청 아닌 경우 
                max_people = int(capacity) if capacity is not None else 20 #정원이 None이면 20 아니면 정원 값
                draft["people"] = st.number_input(
                    "인원",
                    min_value=1,
                    max_value=max_people,
                    value=min(int(draft["people"]), max_people),
                    step=1,
                )
        if draft["service_id"]: # 선택 서비스 있으면 안내 창 출력
            st.info(f"정원: {capacity}명 / 가격: {price_hint}\n\n비고: {notes}")
            ##############################여기까지#############################
        
        draft["memo"] = st.text_area("요청사항(선택)", value=draft["memo"])

        ##############################여기부터#############################
        #st.markdown(f"### 예상 결제금액: **000**")
        total = compute_price(draft)  #총 금액 가져오기    compute_price() 함수 추가하기!!!!!
        st.markdown(f"### 예상 결제금액: **{total:,}**")
        ##############################여기까지#############################
        b1, b2 = st.columns(2)
        with b1:
            ##############################여기부터#############################
            #st.button("예약 저장", use_container_width=True) #  use_container_width=True ->버튼을 부모 컨테이너 너비 맞춤 / 버튼 출력 클릭 시 if 실행
            if st.button("예약 저장", use_container_width=True): #  use_container_width=True ->버튼을 부모 컨테이너 너비 맞춤 / 버튼 출력 클릭 시 if 실행
                ok, msg = validate_reservation(draft) # 유효성 검사
                if not ok: #유효성 검사 false 경우
                    st.error(msg) #에러 msg 처리
                else: #유효성 검사 true 경우
                    saved = save_reservation(draft) #예약 저장 후 딕셔너리 반환
                    st.success("예약이 저장되었습니다.")
                    summary = (
                        f"예약 저장 완료\n"
                        f"- 날짜: {saved['visit_date']}\n"
                        f"- 프로그램: {saved['service_id']}\n"
                        f"- 시간: {saved['time']}\n"
                        f"- 인원: {saved['people']}\n"
                        f"- 금액: {saved['total_price']:,}"
                    )
            ##############################여기까지#############################
            
        with b2:
            ##############################여기부터#############################
            #st.button("초안 초기화", use_container_width=True)
            if st.button("초안 초기화", use_container_width=True):
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
                st.rerun()
            ##############################여기까지#############################

        with st.expander("저장된 예약 보기"): #아코디언 출력 
            ##############################여기부터#############################
            # st.caption("아직 저장된 예약이 없습니다.")
            if not st.session_state.reservations: #예약 정보 없을 시
                st.caption("아직 저장된 예약이 없습니다.")
            else: #예약 정보 출력
                st.dataframe(st.session_state.reservations, use_container_width=True)
            ##############################여기까지#############################

    # ---- 오른쪽: 챗봇(최근 5개 + 입력 하단 + 예약해줘 → 폼 채움)
    with right:
        st.subheader("해설 예약 도우미 챗봇")

        user_text = st.chat_input("예) 내일 14:00 특별전 2명 예약해줘 / 상설전 예약 가능해?")



if __name__ == "__main__":  #직접 실행 시 main 호출
    main()