from pathlib import Path
import sys

import pandas as pd
import pydeck as pdk
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.services.api_client import (
    get_currency_history,
    get_latest_rates,
    login_user,
    logout_user,
    signup_user,
    sync_latest_rates,
)


st.set_page_config(
    page_title="환율 대시보드",
    page_icon="💱",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    div[data-testid="stDecoration"] {
        display: none;
    }
    .auth-shell {
        max-width: 460px;
        margin: 3rem auto 0 auto;
    }
    .auth-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .auth-copy {
        color: inherit;
        opacity: 0.72;
        margin-bottom: 1.3rem;
        line-height: 1.6;
    }
    .screen-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .screen-copy {
        opacity: 0.72;
        margin-bottom: 1rem;
    }
    .tight-bottom {
        margin-bottom: 0.2rem;
    }
    .map-wrap {
        margin-top: 0.5rem;
    }
    .dashboard-top {
        margin-top: 2.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if "sync_message" not in st.session_state:
    st.session_state.sync_message = None


CURRENCY_LOCATIONS = {
    "AED": {"나라": "아랍에미리트", "도시": "두바이", "위도": 25.2048, "경도": 55.2708},
    "AUD": {"나라": "호주", "도시": "캔버라", "위도": -35.2809, "경도": 149.13},
    "BHD": {"나라": "바레인", "도시": "마나마", "위도": 26.2235, "경도": 50.5876},
    "BND": {"나라": "브루나이", "도시": "반다르스리브가완", "위도": 4.9031, "경도": 114.9398},
    "CAD": {"나라": "캐나다", "도시": "오타와", "위도": 45.4215, "경도": -75.6972},
    "CHF": {"나라": "스위스", "도시": "베른", "위도": 46.948, "경도": 7.4474},
    "CNH": {"나라": "중국", "도시": "베이징", "위도": 39.9042, "경도": 116.4074},
    "DKK": {"나라": "덴마크", "도시": "코펜하겐", "위도": 55.6761, "경도": 12.5683},
    "EUR": {"나라": "유로권", "도시": "브뤼셀", "위도": 50.8503, "경도": 4.3517},
    "GBP": {"나라": "영국", "도시": "런던", "위도": 51.5072, "경도": -0.1276},
    "HKD": {"나라": "홍콩", "도시": "홍콩", "위도": 22.3193, "경도": 114.1694},
    "IDR(100)": {"나라": "인도네시아", "도시": "자카르타", "위도": -6.2088, "경도": 106.8456},
    "JPY(100)": {"나라": "일본", "도시": "도쿄", "위도": 35.6762, "경도": 139.6503},
    "KRW": {"나라": "대한민국", "도시": "서울", "위도": 37.5665, "경도": 126.978},
    "KWD": {"나라": "쿠웨이트", "도시": "쿠웨이트시티", "위도": 29.3759, "경도": 47.9774},
    "MYR": {"나라": "말레이시아", "도시": "쿠알라룸푸르", "위도": 3.139, "경도": 101.6869},
    "NOK": {"나라": "노르웨이", "도시": "오슬로", "위도": 59.9139, "경도": 10.7522},
    "NZD": {"나라": "뉴질랜드", "도시": "웰링턴", "위도": -41.2865, "경도": 174.7762},
    "SAR": {"나라": "사우디아라비아", "도시": "리야드", "위도": 24.7136, "경도": 46.6753},
    "SEK": {"나라": "스웨덴", "도시": "스톡홀름", "위도": 59.3293, "경도": 18.0686},
    "SGD": {"나라": "싱가포르", "도시": "싱가포르", "위도": 1.3521, "경도": 103.8198},
    "THB": {"나라": "태국", "도시": "방콕", "위도": 13.7563, "경도": 100.5018},
    "USD": {"나라": "미국", "도시": "워싱턴 D.C.", "위도": 38.9072, "경도": -77.0369},
}


def build_map_dataframe(rates: list[dict]) -> pd.DataFrame:
    rows = []
    for item in rates:
        location = CURRENCY_LOCATIONS.get(item.get("cur_unit", ""))
        if not location:
            continue

        deal_bas_r = item.get("deal_bas_r")
        rows.append(
            {
                "통화코드": item.get("cur_unit"),
                "통화명": item.get("cur_nm"),
                "나라": location["나라"],
                "도시": location["도시"],
                "매매기준율": deal_bas_r,
                "송금받을때": item.get("ttb"),
                "송금보낼때": item.get("tts"),
                "위도": location["위도"],
                "경도": location["경도"],
                "점크기": 70000 if deal_bas_r is None else max(50000, min(int(deal_bas_r * 45), 160000)),
            }
        )

    return pd.DataFrame(rows)


def show_auth_screen() -> None:
    st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">환율 대시보드</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="auth-copy">회원 계정으로 로그인한 뒤 최신 환율과 통화별 흐름을 확인할 수 있습니다.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.auth_mode == "login":
        with st.container(border=True):
            st.subheader("로그인")
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("이메일", placeholder="you@example.com")
                password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")
                submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")

            if submitted:
                result = login_user(email=email, password=password)
                if result.get("message") == "login_failed":
                    st.error(result.get("detail", "로그인에 실패했습니다."))
                else:
                    st.session_state.auth_user = result
                    st.success(f"{result.get('name')}님, 로그인되었습니다.")
                    st.rerun()

            st.caption("처음 방문하셨다면 아래에서 회원가입을 진행해 주세요.")
            if st.button("회원가입으로 이동", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()
    else:
        with st.container(border=True):
            st.subheader("회원가입")
            with st.form("signup_form", clear_on_submit=False):
                name = st.text_input("이름", placeholder="홍길동")
                email = st.text_input("이메일", placeholder="you@example.com")
                password = st.text_input("비밀번호", type="password", placeholder="6자 이상 입력")
                submitted = st.form_submit_button("회원가입", use_container_width=True, type="primary")

            if submitted:
                result = signup_user(name=name, email=email, password=password)
                if result.get("message") == "signup_failed":
                    st.error(result.get("detail", "회원가입에 실패했습니다."))
                else:
                    st.success("회원가입이 완료되었습니다. 이제 로그인해 주세요.")
                    st.session_state.auth_mode = "login"
                    st.rerun()

            if st.button("로그인으로 돌아가기", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def show_dashboard() -> None:
    latest_rates = get_latest_rates()
    rates = latest_rates.get("rates", [])

    st.markdown('<div class="dashboard-top"></div>', unsafe_allow_html=True)

    header_left, header_right = st.columns([1.7, 1])
    with header_left:
        st.markdown('<div class="screen-title">환율 대시보드</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="screen-copy">한국수출입은행 환율 정보를 기준으로 최신 데이터와 통화별 흐름을 확인합니다.</div>',
            unsafe_allow_html=True,
        )
    with header_right:
        st.write("")
        st.write(f"로그인 사용자: {st.session_state.auth_user.get('name', '')}")
        if st.button("로그아웃", use_container_width=True):
            result = logout_user()
            if result.get("message") == "logout_failed":
                st.warning(result.get("detail", "로그아웃 요청에 실패했습니다."))
            else:
                st.success("로그아웃되었습니다.")

            st.session_state.auth_user = None
            st.session_state.auth_mode = "login"
            st.rerun()

    top_left, top_right = st.columns([1.55, 1])
    with top_left:
        with st.container(border=True):
            st.markdown('<div class="tight-bottom">최신 환율을 다시 저장하고 화면을 갱신합니다.</div>', unsafe_allow_html=True)
            if st.button("최신 환율 가져오기", use_container_width=True, type="primary"):
                st.session_state.sync_message = sync_latest_rates()
                st.rerun()

    with top_right:
        with st.container(border=True):
            title_col, help_col = st.columns([8, 1])
            with title_col:
                st.markdown("**저장된 기준일**")
                st.write(latest_rates.get("announcement_date") or "아직 없음")
            with help_col:
                with st.popover("?"):
                    st.write("환율은 날짜 단위로 저장됩니다.")
                    st.write("한 번 수집한 날짜 1건과, 그 날짜의 통화별 환율 여러 건이 함께 저장됩니다.")

    if st.session_state.sync_message:
        sync_result = st.session_state.sync_message
        if sync_result.get("message") == "sync_failed":
            st.error(f"환율 수집에 실패했습니다. {sync_result.get('detail', '원인을 확인해 주세요.')}")
        else:
            st.success(
                f"{sync_result.get('announcement_date')} 기준 환율 {sync_result.get('rate_count', 0)}건을 저장했습니다."
            )

    table_col, trend_col = st.columns([1.35, 1])
    with table_col:
        with st.container(border=True):
            st.subheader("최신 환율")
            if rates:
                df = pd.DataFrame(rates).rename(
                    columns={
                        "cur_unit": "통화코드",
                        "cur_nm": "통화명",
                        "deal_bas_r": "매매기준율",
                        "ttb": "송금받을때",
                        "tts": "송금보낼때",
                    }
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("아직 저장된 환율 데이터가 없습니다. 상단 버튼으로 먼저 불러와 주세요.")

    with trend_col:
        with st.container(border=True):
            st.subheader("통화별 흐름")
            if rates:
                currency_options = [item["cur_unit"] for item in rates if item.get("cur_unit")]
                selected_currency = st.selectbox("통화 선택", options=currency_options, index=0)
                history_payload = get_currency_history(selected_currency)
                history_rows = history_payload.get("history", [])
                if history_rows:
                    history_df = pd.DataFrame(history_rows).sort_values("announcement_date")
                    chart_df = history_df.rename(
                        columns={
                            "announcement_date": "기준일",
                            "deal_bas_r": "매매기준율",
                            "cur_unit": "통화코드",
                            "cur_nm": "통화명",
                            "ttb": "송금받을때",
                            "tts": "송금보낼때",
                        }
                    )
                    st.line_chart(chart_df.set_index("기준일")["매매기준율"])
                    st.dataframe(chart_df, use_container_width=True, hide_index=True)
                else:
                    st.info("선택한 통화의 이력이 아직 없습니다.")
            else:
                st.info("데이터를 불러오면 이 영역에 통화별 흐름이 표시됩니다.")

    st.markdown("")
    with st.container(border=True):
        st.subheader("세계 지도에서 보기")
        st.caption("지도 위 점에 마우스를 올리면 해당 국가의 환율 정보를 확인할 수 있습니다.")
        if rates:
            map_df = build_map_dataframe(rates)
            if not map_df.empty:
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position="[경도, 위도]",
                    get_radius="점크기",
                    get_fill_color="[37, 99, 235, 190]",
                    get_line_color="[255, 255, 255, 220]",
                    line_width_min_pixels=1,
                    stroked=True,
                    pickable=True,
                    auto_highlight=True,
                )
                view_state = pdk.ViewState(
                    latitude=22,
                    longitude=20,
                    zoom=1.15,
                    pitch=0,
                )
                tooltip = {
                    "html": """
                    <div style="padding: 6px 8px;">
                        <div style="font-weight: 700; margin-bottom: 4px;">{나라} · {도시}</div>
                        <div>통화: {통화명} ({통화코드})</div>
                        <div>매매기준율: {매매기준율}</div>
                        <div>송금받을때: {송금받을때}</div>
                        <div>송금보낼때: {송금보낼때}</div>
                    </div>
                    """,
                    "style": {
                        "backgroundColor": "rgba(15, 23, 42, 0.92)",
                        "color": "white",
                        "borderRadius": "10px",
                    },
                }
                st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
                st.pydeck_chart(
                    pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        map_provider="carto",
                        map_style="light",
                        tooltip=tooltip,
                    ),
                    use_container_width=True,
                    height=560,
                )
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("현재 지도에 표시할 수 있는 환율 좌표 데이터가 없습니다.")
        else:
            st.info("환율 데이터를 먼저 불러오면 세계 지도에 국가별 점이 표시됩니다.")


if st.session_state.auth_user is None:
    show_auth_screen()
else:
    show_dashboard()
