"""공유 상수 · 채점 함수 · 학생 자가진단 UI"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from pathlib import Path

# ── Google Sheets 설정 ───────────────────────────────────
SPREADSHEET_ID = "1IFJOIqf2tEQCGRZzNMK37FboLOOFcYknBC5I9L75P-U"
_GSHEET_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def _get_spreadsheet():
    """인증된 Spreadsheet 객체 반환 (실패 시 None).
    st.secrets["gcp_service_account"] 우선, 없으면 service_account.json 사용.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        # Streamlit Cloud: secrets에서 인증
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=_GSHEET_SCOPES
            )
        elif SERVICE_ACCOUNT_FILE.exists():
            creds = Credentials.from_service_account_file(
                str(SERVICE_ACCOUNT_FILE), scopes=_GSHEET_SCOPES
            )
        else:
            return None
        gc = gspread.authorize(creds)
        return gc.open_by_key(SPREADSHEET_ID)
    except Exception:
        return None


def _get_or_create_ws(sh, title: str):
    """이름으로 워크시트를 찾거나 없으면 새로 만들어 반환"""
    try:
        return sh.worksheet(title)
    except Exception:
        ws = sh.add_worksheet(title=title, rows=500, cols=20)
        ws.append_row(COLUMNS)
        return ws


def _append_to_sheets(sh, row: list, grade: int, cls: int):
    """'전체' 시트와 'N학년 M반' 시트에 동시 저장"""
    # 전체 시트
    ws_all = _get_or_create_ws(sh, "전체")
    if not ws_all.get_all_values():
        ws_all.append_row(COLUMNS)
    ws_all.append_row(row)

    # 반별 시트
    ws_cls = _get_or_create_ws(sh, f"{grade}학년 {cls}반")
    ws_cls.append_row(row)

_BASE_DIR            = Path(__file__).parent
IMAGE_DIR            = _BASE_DIR / "01_Ref"
SERVICE_ACCOUNT_FILE = _BASE_DIR / "service_account.json"

CATEGORIES = [
    "학교폭력 개념 인식",
    "공감 및 감수성",
    "행동책임 및 실천",
    "학교문화 인식",
    "사이버폭력 인식 및 예방",
]

Q_CAT   = {1:0,2:0,3:0, 4:1,5:1,6:1, 7:2,8:2,9:2, 10:3,11:3,12:3, 13:4,14:4,15:4}
REVERSE = {1, 5, 6, 8, 10, 12, 13, 14}

QUESTIONS_56 = {
    1:  "친한 사이에서의 가벼운 밀치기나 장난스러운 신체 접촉은 크게 문제되지 않는다.",
    2:  "친구가 겉으로 웃고 있어도, 장난으로 때리거나 밀어서 기분이 나빴다면 학교폭력이다.",
    3:  "친구 한 명을 따돌리고 우리끼리만 노는 것은 친구에게 큰 상처를 줄 수 있다.",
    4:  "따돌림을 당하거나 혼자 있는 친구를 보면 마음이 불편하다.",
    5:  "괴롭힘을 당하는 친구를 보면 '저 친구가 잘못한 게 있어서 그럴 거야'라는 생각이 든다.",
    6:  "친한 친구 사이끼리 다소 거친 말투나 욕설, 놀림은 친근함의 표현이다.",
    7:  "친구가 괴롭힘을 당할 때 선생님이나 부모님께 도움을 요청하는 것이 도움이 된다.",
    8:  "내가 직접 때리지 않고 옆에서 구경하거나 웃기만 했다면 나에게는 잘못이 없다.",
    9:  "장난으로 한 일이라도 친구가 상처를 받았다면 진심으로 사과해야 한다.",
    10: "우리 반 전체가 즐겁다면, 한두 명의 친구가 외롭게 지내는 것은 어쩔 수 없는 일이다.",
    11: "우리 학교에는 힘든 일이 있을 때 도움을 요청할 수 있는 선생님이나 어른이 계신다.",
    12: "친구들끼리의 싸움이나 문제는 어른들의 관여없이 우리끼리 해결하는 것이 가장 좋다.",
    13: "친구의 웃긴 사진을 동의 없이 단톡방에 올리는 행동은 학교폭력이 아니다.",
    14: "온라인에서 하는 욕이 직접 만나서 하는 욕보다 상대방의 마음을 덜 아프게 한다.",
    15: "단톡방에서 다른 친구를 놀릴 때 가만히 보고만 있는 것도 친구에게 상처가 될 수 있다.",
}

QUESTIONS_34 = {
    1:  "친한 친구끼리 장난으로 살짝 밀거나 몸을 건드리는 건 괜찮아.",
    2:  "친구가 웃어도, 장난으로 밀거나 때려서 기분이 나빴다면 이건 폭력이야.",
    3:  "친구 한 명을 빼고 우리끼리만 노는 건 그 친구에게 큰 상처가 돼.",
    4:  "혼자 있거나 따돌림 받는 친구를 보면 마음이 불편해.",
    5:  "괴롭힘 당하는 친구를 보면 '그 친구도 뭔가 잘못한 게 있겠지'라고 생각해.",
    6:  "친한 친구끼리 거친 말이나 욕설, 놀림은 사이 좋다는 표현이야.",
    7:  "친구가 괴롭힘을 당할 때 선생님이나 부모님께 말하면 도움이 돼.",
    8:  "내가 때리지 않고 옆에서 구경하거나 웃기만 했다면 나는 잘못이 없어.",
    9:  "장난으로 한 일이라도 친구가 상처받았다면 진심으로 사과해야 해.",
    10: "우리 반 모두가 즐거우면, 한두 명이 외롭게 지내는 건 어쩔 수 없어.",
    11: "우리 학교에는 힘들 때 도움을 요청할 수 있는 선생님이나 어른이 계셔.",
    12: "친구들끼리 문제가 생기면 어른 없이 우리끼리 해결하는 게 제일 좋아.",
    13: "친구의 웃긴 사진을 허락 없이 단톡방에 올리는 건 학교폭력이 아니야.",
    14: "온라인에서 하는 욕은 직접 만나서 하는 욕보다 덜 아프게 해.",
    15: "단톡방에서 친구를 놀릴 때 가만히 보기만 해도 그 친구에게 상처가 될 수 있어.",
}

SITUATIONS_34 = {
    1:  "🎬 철수와 영희는 매우 친한 친구예요. 철수가 장난으로 영희를 살짝 밀었어요.",
    2:  "🎬 민준이가 웃으면서 수아를 밀었는데, 사실 수아는 기분이 많이 나빴어요.",
    3:  "🎬 친구들이 지우를 빼고 자기들끼리만 어울려서 놀고 있어요.",
    4:  "🎬 점심시간에 항상 혼자 밥 먹는 친구가 있어요.",
    5:  "🎬 재민이가 매일 친구들에게 놀림을 받고 있어요.",
    6:  "🎬 단짝 친구들이 서로 거친 말을 주고받으며 웃고 있어요.",
    7:  "🎬 매일 같은 친구에게 괴롭힘을 당하는 아이가 있어요.",
    8:  "🎬 몇 명이 한 친구를 밀치고 있어요. 나는 옆에서 웃으며 구경해요.",
    9:  "🎬 장난으로 친구를 밀었는데 친구가 넘어져서 울어요.",
    10: "🎬 우리 반 대부분은 재밌게 노는데, 한 명은 항상 혼자 구석에 있어요.",
    11: "🎬 학교에서 힘든 일이 생겼는데 누구에게 말해야 할지 몰라요.",
    12: "🎬 친구들끼리 싸움이 생겼어요. 어른한테 말해야 할까요?",
    13: "🎬 친구의 웃긴 표정 사진을 몰래 찍어서 단톡방에 올렸어요.",
    14: "🎬 온라인 게임에서 화가 나서 채팅으로 욕을 했어요.",
    15: "🎬 단톡방에서 친구들이 한 아이를 놀리고 있어요. 나는 가만히 보고만 있어요.",
}

SITUATIONS_56 = {
    1:  "💡 친한 사이라도 상대가 원하지 않는 신체 접촉은 불쾌감을 줄 수 있어요. 판단 기준은 '내 의도'가 아닌 '상대방이 느끼는 감정'이에요.",
    2:  "💡 겉으로 웃는다고 속으로도 괜찮은 게 아닐 수 있어요. 상대방이 실제로 어떻게 느꼈는지가 중요해요.",
    3:  "💡 일부러 한 명을 빼고 노는 것은 '관계적 폭력'이에요. 혼자 남은 친구가 얼마나 상처받을지 생각해 보세요.",
    4:  "💡 공감 능력은 타인의 감정을 내 것처럼 느끼는 거예요. 혼자 있는 친구를 보고 어떤 감정이 드나요?",
    5:  "💡 괴롭힘의 원인이 피해자에게 있다는 생각은 잘못이에요. 어떤 이유로도 괴롭힘은 정당화될 수 없어요.",
    6:  "💡 거친 말이 친근감의 표현처럼 느껴질 수 있지만, 듣는 사람은 상처를 받을 수 있어요.",
    7:  "💡 어른에게 도움을 요청하는 것은 용기 있는 행동이에요. '고자질'이 아니라 꼭 필요한 도움 요청이에요.",
    8:  "💡 방관하거나 웃는 것도 피해자에게 상처를 주고 가해를 돕는 행동이 될 수 있어요.",
    9:  "💡 '장난이었어'는 사과가 아니에요. 상대가 상처받았다면 진심 어린 사과가 필요해요.",
    10: "💡 다수의 즐거움이 소수의 고통을 정당화할 수 없어요. 모두가 함께할 때 진짜 즐거운 교실이 돼요.",
    11: "💡 학교에는 여러분을 도와줄 선생님과 어른이 있어요. 힘들 때 혼자 해결하려 하지 마세요.",
    12: "💡 어른의 도움이 자율성을 해치는 게 아니에요. 심각한 문제일수록 전문가의 도움이 필요해요.",
    13: "💡 동의 없이 사진을 공유하는 것은 명백한 사이버폭력이에요. '재미'는 이유가 될 수 없어요.",
    14: "💡 온라인 말도 기록으로 남고, 받는 사람에게 깊은 상처를 줘요. 오히려 더 오래 남을 수 있어요.",
    15: "💡 방관하는 것도 괴롭힘에 가담하는 것과 같아요. '그냥 보고만 있었어'는 변명이 될 수 없어요.",
}

OPTIONS_34 = ["완전 그래! 😄", "그래 😊", "잘 모르겠어 😐", "아닌 것 같아 🤔", "절대 아니야! 😤"]
OPTIONS_56 = ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다", "전혀 그렇지 않다"]
CAT_COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#DDA0DD"]

# 범주별 문항 번호 매핑
CAT_QUESTIONS = {
    "학교폭력 개념 인식":     [1, 2, 3],
    "공감 및 감수성":         [4, 5, 6],
    "행동책임 및 실천":       [7, 8, 9],
    "학교문화 인식":          [10, 11, 12],
    "사이버폭력 인식 및 예방": [13, 14, 15],
}

# 문항별 상세설명 (5-6학년 / PDF 붙임2 원문)
EXPLANATIONS_56 = {
    1:  "아무리 친한 사이라도 상대방의 허락 없는 신체 접촉은 단순한 장난이 아닌 학교폭력이 될 수 있습니다. 내가 즐겁더라도 상대방이 아픔이나 불쾌함을 느낀다면 그것은 상대의 인격을 존중하지 않는 행동입니다. 진정한 우정은 장난을 핑계로 고통을 주는 것이 아니라 서로의 몸과 마음을 소중히 여기는 건강한 관계에서 시작됩니다.",
    2:  "친구가 겉으로 웃고 있다고 해서 반드시 기분이 좋은 것은 아닙니다. 너무 당황스럽거나 무안해서, 혹은 더 큰 괴롭힘이 두려워 억지로 웃음을 짓는 경우도 있습니다. 어떤 행동이 학교폭력인지 아닌지를 결정하는 가장 중요한 기준은 행동을 당한 사람이 느낀 마음의 상처와 불쾌함입니다.",
    3:  "우리끼리만 즐겁다고 해서 다른 친구 한 명을 소외시키는 것은 그 친구의 마음에 아주 깊은 생채기를 남기는 행동입니다. 눈에 보이는 상처는 없지만, 혼자 남겨진 친구는 세상에서 가장 외로운 기분을 느끼며 큰 슬픔에 빠지게 됩니다. 모두가 함께 어울릴 때 우리 반은 누구도 다치지 않는 안전하고 행복한 보금자리가 될 수 있습니다.",
    4:  "괴로워하는 친구를 보며 느끼는 마음의 불편함은 내 안의 '공감 센서'가 아주 건강하게 작동하고 있다는 멋진 신호입니다. 학교폭력 감수성은 친구의 아픔을 나의 일처럼 느끼는 섬세한 마음에서 시작됩니다. 친구가 힘들어 하는 모습을 그냥 지나치지 않고 도와주고 싶은 마음은 우리 반을 모두가 안전한 교실에서 함께 지낼 수 있게 하는 소중한 씨앗이 됩니다.",
    5:  "학교폭력의 원인을 피해자에게서 찾는 태도는 문제의 본질을 흐리게 할 수 있습니다. 어떤 이유가 있더라도 친구를 괴롭히는 행동은 결코 정당화될 수 없으며, 피해자에게 책임을 돌리는 생각은 가해자의 잘못을 정당화할 위험이 큽니다. 만약 친구에게 고칠 점이나 갈등이 있다면 괴롭힘이 아닌 학교의 규칙과 올바른 대화를 통해 해결하는 것이 마땅합니다.",
    6:  "욕설과 놀림은 친밀함의 증거가 아니라 상대를 존중하지 않는 잘못된 습관입니다. 타인이 어떻게 받아들일지를 고려하지 않고 한 말은 의도와 상관없이 상대에게 불쾌감을 주어 언어폭력이 될 수 있습니다. 진정한 우정은 거친 표현이 아니라 서로 예의를 지키며 따뜻한 말로 마음을 나눌 때 깊어집니다.",
    7:  "학교폭력을 목격했을 때 어른에게 알리는 것은 '고자질'이 아니라 친구를 지키는 '정의로운 신고'입니다. 주변에 도움을 요청하는 행동은 더 큰 피해를 막는 가장 빠르고 안전한 방법입니다. 학교가 모두에게 안전한 곳이 되려면, 누구에게 차별이나 학교폭력이 생겼을 때 이를 바로잡으려 노력해야 합니다.",
    8:  "학교폭력을 구경하거나 함께 웃는 행동은 가해자에게 용기를 주고 피해자를 더 외롭게 만드는 일입니다. 직접 폭력을 가하지 않았더라도 그 상황을 즐기거나 내버려 두었다면 학교폭력에 함께 참여한 것과 다름없습니다. 모두가 안전한 학교를 만들기 위해서는 모르는 척하는 방관자가 아니라, 잘못된 상황을 바로잡으려고 노력하는 '방어자'의 태도가 필요합니다.",
    9:  "나의 의도가 어떠했는가보다 나의 행동으로 인해 친구가 어떤 기분을 느꼈는가가 훨씬 더 중요합니다. '장난'은 가해자가 자신의 행동을 가볍게 여기기 위해 사용하는 변명에 불과하며, 상대방이 고통을 느꼈다면 그 행동은 이미 학교폭력입니다. 진심 어린 사과는 자신의 행동이 타인에게 미친 영향을 책임지는 성숙하고 용기 있는 태도입니다.",
    10: "진정으로 건강한 학급 공동체는 단 한 명의 친구도 소외되지 않고 모두가 서로 연결되어 있을 때 비로소 완성됩니다. 다수의 즐거움을 위해 소수의 불편함을 당연하게 여기는 태도는 친구를 배움과 성장의 기회로부터 소외시킵니다. 모든 학생은 존재 그 자체로 존중받으며 누구도 차별받지 않고 존재할 권리가 있습니다.",
    11: "안전한 학교 공동체는 문제가 발생했을 때 언제든 도움을 받을 수 있다는 강력한 신뢰가 있을 때 비로소 만들어집니다. 선생님과 학교의 어른들은 학생들의 고민을 진심으로 경청하고 해결을 위해 함께 발맞추어 나가는 든든한 조력자입니다. 힘든 일이 생기면 혼자 고민하지 말고 선생님께 도움을 요청하세요.",
    12: "학생들 사이의 갈등을 우리끼리만 해결하려고 고집하는 것은 힘의 균형이 깨진 상황에서 더 큰 상처를 남기거나 상황을 더 복잡하게 만들 위험이 있습니다. 어른들의 개입은 학생들의 자율성을 해치는 일이 아니라, 모든 학생이 공정하고 안전하게 자신의 이야기를 할 수 있도록 돕는 든든한 보호막입니다.",
    13: "친구의 허락 없이 사진이나 영상을 인터넷에 올리는 것은 명백한 사생활 침해이자 괴롭힘입니다. 온라인의 특성상 한 번 퍼진 정보는 완전히 삭제하기가 매우 어렵고 누가 보았는지 알 수 없어 피해자의 일상에 깊은 고통을 남깁니다. 디지털 공간에서도 서로의 사생활을 소중히 지켜주는 성숙한 태도가 필요합니다.",
    14: "얼굴이 보이지 않는 온라인 공간에서 오가는 거친 말은 피해자의 마음에 더 깊은 생채기를 남기는 위험한 행동입니다. 인터넷의 특성상 한 번 내뱉은 욕설은 기록으로 남아 쉽게 삭제하기 어렵고, 불특정 다수에게 순식간에 퍼지며 피해자를 끊임없이 괴롭힙니다. 보이지 않는 곳에서도 상대의 인격을 존중하고 따뜻한 말을 건네는 태도가 필요합니다.",
    15: "단톡방에서의 침묵은 단순한 방관을 넘어 가해자의 행동에 동조하는 무언의 메시지가 됩니다. 피해자는 아무도 도와주지 않는 화면 너머에서 세상 전체로부터 외면받는 듯한 깊은 외로움과 상처를 입습니다. 사이버 공간에서도 친구의 아픔에 공감하고 용기 있게 목소리를 내는 태도가 필요합니다.",
}

# 문항별 상세설명 (3-4학년 / 쉬운 말 버전)
EXPLANATIONS_34 = {
    1:  "친한 친구라도 허락 없이 몸을 건드리면 안 돼요. 내가 재밌어도 친구가 싫다고 느끼면 그건 폭력이에요. 진짜 친구는 서로의 몸을 소중히 여겨요. 💛",
    2:  "친구가 웃고 있다고 기분이 좋은 게 아닐 수도 있어요. 부끄럽거나 무서워서 억지로 웃을 수도 있거든요. 중요한 건 친구가 어떻게 느끼는지예요. 💛",
    3:  "친구 한 명을 빼고 노는 건 그 친구에게 정말 큰 상처를 줘요. 혼자 남겨진 친구는 너무 외롭고 슬퍼요. 모두 함께 놀 때 우리 반이 더 행복해져요! 💛",
    4:  "혼자 있거나 따돌림 받는 친구를 보면 마음이 불편한 게 맞아요. 그건 내 안에 착한 마음이 있다는 거예요! 친구의 아픔을 내 일처럼 느끼는 게 진짜 공감이에요. 💛",
    5:  "괴롭힘을 당하는 게 그 친구 잘못이 아니에요. 어떤 이유가 있어도 친구를 괴롭히는 건 절대 안 돼요. 문제가 있으면 선생님께 말하거나 대화로 해결해요. 💛",
    6:  "친한 친구한테라도 거친 말이나 욕설은 상처를 줄 수 있어요. 친하다고 나쁜 말을 해도 된다는 건 아니에요. 진짜 친구는 서로에게 따뜻하고 예쁜 말을 써요. 💛",
    7:  "친구가 괴롭힘을 당할 때 선생님이나 부모님께 말하는 건 고자질이 아니에요! 그건 친구를 도와주는 용기 있는 행동이에요. 어른에게 말하면 더 빠르게 도움받을 수 있어요. 💛",
    8:  "직접 때리지 않았어도 구경하거나 웃으면 친구에게 더 큰 상처를 줘요. 가만히 보고만 있으면 괴롭히는 것을 도와주는 것과 같아요. 나쁜 일을 막으려고 노력하는 게 진짜 용감한 거예요. 💛",
    9:  "장난이었어도 친구가 상처받았다면 진심으로 사과해야 해요. \"장난이었어\"는 진짜 사과가 아니에요. 미안하다고 말하고 친구의 마음을 위로해 주세요. 💛",
    10: "몇 명이 외롭게 지내도 괜찮다는 생각은 틀렸어요. 우리 반 모두가 함께 행복해야 진짜 좋은 반이에요. 혼자 있는 친구한테 먼저 다가가 말을 걸어 보세요. 💛",
    11: "학교에서 힘든 일이 생기면 선생님이나 어른께 말해도 돼요. 선생님들은 여러분을 도와주고 싶어 하세요. 혼자 고민하지 말고 어른에게 도움을 요청하세요. 💛",
    12: "친구들끼리 싸우거나 문제가 생기면 선생님께 도움을 받는 게 좋아요. 어른이 도와주면 더 공평하고 안전하게 해결할 수 있어요. 도움을 요청하는 건 약한 게 아니에요! 💛",
    13: "친구 허락 없이 사진을 단톡방에 올리면 안 돼요. 그건 사이버 폭력이에요! 재밌다고 해도 친구가 싫다면 절대 하면 안 돼요. 💛",
    14: "온라인에서 하는 욕도 직접 하는 욕만큼 상처를 줘요. 기록으로 남아서 더 오랫동안 친구를 괴롭힐 수 있어요. 온라인에서도 항상 따뜻한 말을 써요. 💛",
    15: "단톡방에서 친구가 놀림 받을 때 가만히 보고만 있으면 친구가 더 외로워요. 침묵도 상처가 돼요. 용기 내서 \"그만해\"라고 말해주거나 선생님께 알려주세요. 💛",
}


# ── 채점 ─────────────────────────────────────────────────
def calc_score(q_num: int, ans_idx: int) -> int:
    if q_num in REVERSE:
        return ans_idx + 1
    else:
        return 5 - ans_idx


def get_cat_scores(answers: dict) -> dict:
    scores = {c: 0 for c in CATEGORIES}
    for q, idx in answers.items():
        scores[CATEGORIES[Q_CAT[q]]] += calc_score(q, idx)
    return scores


def normalize(cat_scores: dict):
    """범주 15점 만점 → 20점, 총점 75 → 100 정규화"""
    norm  = {c: round(s / 15 * 20) for c, s in cat_scores.items()}
    total = round(sum(cat_scores.values()) / 75 * 100)
    return norm, total


# ── 회차 관리 (Google Sheets _rounds 탭) ──────────────────
_ROUNDS_HEADER = ["id", "name", "date", "is_current"]


def _get_rounds_ws():
    """_rounds 워크시트 반환 (없으면 생성)"""
    sh = _get_spreadsheet()
    if sh is None:
        return None
    try:
        return sh.worksheet("_rounds")
    except Exception:
        ws = sh.add_worksheet(title="_rounds", rows=100, cols=4)
        ws.append_row(_ROUNDS_HEADER)
        # 기본 1회차 생성
        ws.append_row([1, "1회차", str(date.today()), 1])
        return ws


def load_rounds() -> dict:
    ws = _get_rounds_ws()
    if ws is None:
        return {"rounds": [{"id": 1, "name": "1회차", "date": str(date.today())}], "current": 1}
    rows = ws.get_all_values()
    if len(rows) <= 1:
        ws.append_row([1, "1회차", str(date.today()), 1])
        return {"rounds": [{"id": 1, "name": "1회차", "date": str(date.today())}], "current": 1}
    rounds, current = [], 1
    for r in rows[1:]:
        rid = int(r[0])
        rounds.append({"id": rid, "name": r[1], "date": r[2]})
        if str(r[3]) == "1":
            current = rid
    return {"rounds": rounds, "current": current}


def get_current_round_id() -> int:
    return load_rounds()["current"]


def create_new_round(name: str) -> int:
    ws = _get_rounds_ws()
    if ws is None:
        return 1
    rows = ws.get_all_values()
    ids = [int(r[0]) for r in rows[1:]] if len(rows) > 1 else [0]
    new_id = max(ids) + 1
    # 기존 전부 is_current=0
    for i, r in enumerate(rows[1:], start=2):
        ws.update_cell(i, 4, 0)
    ws.append_row([new_id, name, str(date.today()), 1])
    return new_id


def set_current_round(round_id: int):
    ws = _get_rounds_ws()
    if ws is None:
        return
    rows = ws.get_all_values()
    for i, r in enumerate(rows[1:], start=2):
        ws.update_cell(i, 4, 1 if int(r[0]) == round_id else 0)


# ── 데이터 저장/로드 ─────────────────────────────────────
COLUMNS = ["round", "student_name", "grade", "class", "total_score"] + CATEGORIES

_NUM_COLS = ["round", "grade", "class", "total_score"] + CATEGORIES


def _sheet_to_df(rows: list) -> pd.DataFrame:
    """시트 rows(헤더 포함) → DataFrame, 숫자 컬럼 변환"""
    if len(rows) <= 1:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(rows[1:], columns=rows[0])
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[COLUMNS]
    for col in _NUM_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def load_data(round_id: int | None = None) -> pd.DataFrame:
    sh = _get_spreadsheet()
    if sh is None:
        return pd.DataFrame(columns=COLUMNS)
    try:
        ws = _get_or_create_ws(sh, "전체")
        df = _sheet_to_df(ws.get_all_values())
        if round_id is not None:
            df = df[df["round"] == round_id].reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)


def save_result(info: dict, norm_cats: dict, total: int):
    round_id = get_current_round_id()
    new_row  = {
        "round":        round_id,
        "student_name": info["name"],
        "grade":        info["grade"],
        "class":        info["class"],
        "total_score":  total,
        **norm_cats,
    }
    sh = _get_spreadsheet()
    if sh is not None:
        _append_to_sheets(
            sh,
            [new_row[col] for col in COLUMNS],
            info["grade"],
            info["class"],
        )


def _rewrite_ws(ws, header: list, rows: list):
    """시트를 초기화하고 헤더 + 데이터로 재작성"""
    ws.clear()
    ws.append_row(header)
    if rows:
        ws.append_rows(rows)


def reset_data(round_id: int, grade: int | None = None, cls: int | None = None):
    """지정 범위 데이터 삭제 (Google Sheets)"""
    sh = _get_spreadsheet()
    if sh is None:
        return
    try:
        ws_all = _get_or_create_ws(sh, "전체")
        all_rows = ws_all.get_all_values()
        if len(all_rows) <= 1:
            return
        header = all_rows[0]
        ri = header.index("round")
        gi = header.index("grade")
        ci = header.index("class")

        def should_keep(r):
            if str(r[ri]) != str(round_id):
                return True
            if grade is not None and str(r[gi]) != str(grade):
                return True
            if cls is not None and str(r[ci]) != str(cls):
                return True
            return False

        kept = [r for r in all_rows[1:] if should_keep(r)]
        _rewrite_ws(ws_all, header, kept)

        # 반별 시트도 갱신
        for ws in sh.worksheets():
            if ws.title == "전체":
                continue
            try:
                g = int(ws.title.split("학년")[0])
                c = int(ws.title.split("학년 ")[1].replace("반", ""))
            except Exception:
                continue
            cls_rows = [r for r in kept
                        if str(r[gi]) == str(g) and str(r[ci]) == str(c)]
            _rewrite_ws(ws, header, cls_rows)
    except Exception:
        pass


# ── 공통 UI 헬퍼 ─────────────────────────────────────────
def round_selector_sidebar() -> int:
    """사이드바에 회차 선택기를 표시하고 선택된 round_id를 반환"""
    data      = load_rounds()
    rounds    = data["rounds"]
    current   = data["current"]
    round_ids = [r["id"] for r in rounds]
    round_labels = {r["id"]: f"{r['name']}  ({r['date']})" for r in rounds}

    default_idx = round_ids.index(current) if current in round_ids else 0

    with st.sidebar:
        st.markdown("---")
        st.markdown("**📋 검사 회차**")
        sel_id = st.selectbox(
            "조회 회차",
            options=round_ids,
            format_func=lambda x: round_labels[x],
            index=default_idx,
            key="sidebar_round_sel",
        )
        cur_label = round_labels.get(current, "")
        st.caption(f"현재 검사 진행 회차: **{cur_label}**")
    return sel_id


def download_csv_button(df: pd.DataFrame, filename: str, label: str = "📥 결과 다운로드 (CSV)"):
    display = df.drop(columns=["round"], errors="ignore")
    csv = display.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


@st.dialog("초기화 확인")
def _reset_dialog(round_id: int, grade: int | None, cls: int | None, label: str):
    st.warning(f"⚠️ **{label}** 데이터를 삭제합니다.\n\n이 작업은 되돌릴 수 없습니다.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("삭제 확인", type="primary", use_container_width=True):
            reset_data(round_id, grade, cls)
            st.rerun()
    with c2:
        if st.button("취소", use_container_width=True):
            st.rerun()


def reset_button(round_id: int, grade: int | None = None, cls: int | None = None, label: str = "전체"):
    if st.button(f"🗑️ {label} 초기화", use_container_width=True, type="secondary"):
        _reset_dialog(round_id, grade, cls, label)


# ── 교직원 페이지 인증 ───────────────────────────────────
def require_auth(auth_key: str = "staff_auth"):
    if not st.session_state.get(auth_key):
        st.markdown("### 🔒 교직원 인증")
        with st.form("auth_form", border=False):
            pwd = st.text_input("비밀번호를 입력하세요", type="password")
            submitted = st.form_submit_button("확인", type="primary", use_container_width=True)
        if submitted:
            if pwd == "0143":
                st.session_state[auth_key] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
        st.stop()


# ── 사이드바 숨김 (학생 페이지용) ───────────────────────
def hide_sidebar():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"]       {display: none !important;}
    button[data-testid="collapsedControl"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)


# ── CSS ──────────────────────────────────────────────────
def apply_css():
    st.markdown("""
    <style>
    .cat-badge-34 { background:#FF8C42; color:white; padding:4px 14px;
        border-radius:20px; font-size:0.85em; font-weight:bold; display:inline-block; }
    .cat-badge-56 { background:#4A90E2; color:white; padding:4px 14px;
        border-radius:20px; font-size:0.85em; font-weight:bold; display:inline-block; }
    .sit-34 { background:#FFF9C4; border-left:5px solid #FFC107;
        padding:12px 16px; border-radius:0 10px 10px 0; margin:12px 0; }
    .sit-56 { background:#E8F4FD; border-left:5px solid #4A90E2;
        padding:12px 16px; border-radius:0 10px 10px 0; margin:12px 0; }
    .q-34 { font-size:1.35em; font-weight:700; line-height:1.7; margin:12px 0; }
    .q-56 { font-size:1.15em; font-weight:600; line-height:1.6; margin:12px 0; }
    </style>
    """, unsafe_allow_html=True)


# ── 세션 상태 관리 ──────────────────────────────────────
def init_quiz(prefix):
    for key, val in [
        (f"{prefix}_page", "info"), (f"{prefix}_q", 0),
        (f"{prefix}_answers", {}),  (f"{prefix}_info", {}),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val


def reset_quiz(prefix):
    for key in [f"{prefix}_page", f"{prefix}_q",
                f"{prefix}_answers", f"{prefix}_info", f"{prefix}_saved"]:
        st.session_state.pop(key, None)


# ── 정보 입력 화면 ───────────────────────────────────────
def show_info_page(prefix, grade_group):
    col_logo, col_title = st.columns([1, 3], vertical_alignment="center")
    with col_logo:
        st.markdown("""
        <div style='text-align:center;'>
            <div style='font-weight:800; font-size:1.6em; margin-bottom:8px;'>인천석암초등학교</div>
            <img src='data:image/jpeg;base64,{logo_b64}' width='160' style='display:block; margin:0 auto;'/>
        </div>
        """.replace("{logo_b64}", __import__("base64").b64encode(open(str(IMAGE_DIR / "ROCKTHESCHOOL.jpeg"), "rb").read()).decode()), unsafe_allow_html=True)
    with col_title:
        if grade_group == "34":
            st.markdown("## 👋 안녕! 학교폭력에 대한 내 마음을 확인해 보자!")
            st.markdown("15개의 그림 문제를 보고 솔직하게 답해줘! 정답은 없어 😊")
        else:
            st.markdown("## 학교폭력 감수성 자가진단")
            st.markdown("15개 문항을 읽고 솔직하게 응답해 주세요. 정답은 없습니다.")
    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        grade = st.selectbox("학년", [3, 4] if grade_group == "34" else [5, 6])
    with c2:
        class_num = st.selectbox("반", list(range(1, 11)))
    with c3:
        student_num = st.selectbox("번호", list(range(1, 41)))

    st.divider()
    btn = "시작하기! 🚀" if grade_group == "34" else "진단 시작"
    if st.button(btn, use_container_width=True, type="primary"):
        st.session_state[f"{prefix}_info"] = {
            "name": str(student_num), "grade": grade, "class": class_num
        }
        st.session_state[f"{prefix}_page"] = "quiz"
        st.rerun()


# ── 문항 카드 화면 ───────────────────────────────────────
def show_quiz_page(prefix, grade_group):
    questions  = QUESTIONS_34  if grade_group == "34" else QUESTIONS_56
    situations = SITUATIONS_34 if grade_group == "34" else SITUATIONS_56
    options    = OPTIONS_34    if grade_group == "34" else OPTIONS_56
    badge_cls  = "cat-badge-34" if grade_group == "34" else "cat-badge-56"
    sit_cls    = "sit-34"       if grade_group == "34" else "sit-56"
    q_cls      = "q-34"         if grade_group == "34" else "q-56"

    q_idx   = st.session_state[f"{prefix}_q"]
    q_num   = q_idx + 1
    answers = st.session_state[f"{prefix}_answers"]
    cat     = CATEGORIES[Q_CAT[q_num]]

    st.progress(q_num / 15)
    st.caption(f"{'⭐' * q_num}{'☆' * (15 - q_num)}   {q_num} / 15 문항")
    st.divider()

    col_img, col_q = st.columns([1, 1.2], gap="large")

    with col_img:
        img_path = IMAGE_DIR / f"{q_num}.png"
        if img_path.exists():
            st.image(str(img_path), use_container_width=True)
        else:
            st.markdown(
                "<div style='background:#f0f0f0;height:280px;border-radius:15px;"
                "display:flex;align-items:center;justify-content:center;"
                "font-size:5em;'>🏫</div>",
                unsafe_allow_html=True,
            )

    with col_q:
        st.markdown(f'<span class="{badge_cls}">{cat}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="{q_cls}">{questions[q_num]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{sit_cls}">{situations[q_num]}</div>', unsafe_allow_html=True)

    st.divider()

    prev_ans = answers.get(q_num, None)
    label = "어떻게 생각해? 👇" if grade_group == "34" else "나의 생각 👇"
    st.markdown(f"**{label}**")

    btn_cols = st.columns(5)
    for i, (col, opt) in enumerate(zip(btn_cols, options)):
        with col:
            is_sel    = (prev_ans == i)
            btn_label = f"✅ {opt}" if is_sel else opt
            if st.button(btn_label, key=f"opt_{prefix}_{q_num}_{i}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                answers[q_num] = i
                if q_num < 15:
                    st.session_state[f"{prefix}_q"] += 1
                else:
                    st.session_state[f"{prefix}_page"] = "result"
                st.rerun()

    if q_idx > 0:
        st.divider()
        if st.button("◀ 이전 문항"):
            st.session_state[f"{prefix}_q"] -= 1
            st.rerun()


# ── 결과 화면 ────────────────────────────────────────────
def show_result_page(prefix, grade_group):
    info    = st.session_state.get(f"{prefix}_info", {})
    answers = st.session_state.get(f"{prefix}_answers", {})
    name    = info.get("name", "학생")

    cat_scores        = get_cat_scores(answers)
    norm_cats, total  = normalize(cat_scores)

    # 결과 페이지 최초 진입 시 자동 저장
    saved_key = f"{prefix}_saved"
    if not st.session_state.get(saved_key):
        save_result(info, norm_cats, total)
        st.session_state[saved_key] = True

    if grade_group == "34":
        st.markdown(f"## 🎉 {name}번 학생의 진단 결과!")
        if total >= 80:
            st.success("🌟 대단해요! 친구들의 마음을 정말 잘 이해하고 있어요!")
        elif total >= 60:
            st.info("😊 잘 하고 있어요! 조금 더 친구의 마음을 생각해봐요.")
        else:
            st.warning("💪 앞으로 조금씩 배워나가면 돼요. 괜찮아요!")
    else:
        st.markdown(f"## 📊 {name}번 학생의 자가진단 결과")
        if total >= 80:
            st.success("✅ 학교폭력 감수성이 매우 높습니다. 주변 친구들에게 좋은 영향을 줄 수 있어요!")
        elif total >= 60:
            st.warning("🔶 일부 영역에서 감수성을 더 키울 필요가 있습니다.")
        else:
            st.error("⚠️ 학교폭력 예방 교육에 적극적으로 참여해 보세요.")

    m1, m2 = st.columns(2)
    with m1:
        st.metric("총점", f"{total} / 100")
    with m2:
        best = max(norm_cats, key=norm_cats.get)
        st.metric("가장 높은 영역", f"{best} ({norm_cats[best]}/20)")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        vals = list(norm_cats.values())
        lbls = list(norm_cats.keys())
        fig = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=lbls + [lbls[0]],
            fill="toself", fillcolor="rgba(74,144,226,0.2)",
            line=dict(color="royalblue", width=2),
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 20])),
            title="범주별 레이더 차트", showlegend=False, height=340,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.bar(
            x=list(norm_cats.keys()), y=list(norm_cats.values()),
            color=list(norm_cats.keys()),
            color_discrete_sequence=CAT_COLORS,
            title="범주별 점수 (20점 만점)",
            range_y=[0, 20], labels={"x": "", "y": "점수"},
        )
        fig2.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("영역별 상세")
    for cat, score in norm_cats.items():
        st.progress(score / 20, text=f"{cat}: {score}/20점")

    # ── 점수 10 이하 범주: 문항별 상세 설명 ─────────────────
    low_cats = {cat: score for cat, score in norm_cats.items() if score <= 10}
    if low_cats:
        st.divider()
        if grade_group == "34":
            st.subheader("📖 더 알아보기")
            st.caption("점수가 낮은 영역이에요. 함께 생각해 봐요!")
        else:
            st.subheader("📖 문항별 상세 설명")
            st.caption("10점 이하 영역에 대한 상세 해설입니다.")

        explanations = EXPLANATIONS_34 if grade_group == "34" else EXPLANATIONS_56
        questions    = QUESTIONS_34    if grade_group == "34" else QUESTIONS_56

        for cat in low_cats:
            score = norm_cats[cat]
            with st.expander(f"**{cat}** — {score}/20점", expanded=True):
                for q_num in CAT_QUESTIONS[cat]:
                    col_img, col_txt = st.columns([1, 2], gap="medium")
                    with col_img:
                        img_path = IMAGE_DIR / f"{q_num}.png"
                        if img_path.exists():
                            st.image(str(img_path), use_container_width=True)
                    with col_txt:
                        st.markdown(f"**문항 {q_num}.** {questions[q_num]}")
                        st.info(explanations[q_num])
                    st.markdown("---")

    st.divider()
    s1, s2 = st.columns(2)
    with s1:
        st.success("✅ 결과가 자동으로 저장되었습니다!")
    with s2:
        lbl = "다시 하기 🔄" if grade_group == "34" else "다시 시작"
        if st.button(lbl, use_container_width=True):
            st.session_state.pop(f"{prefix}_saved", None)
            reset_quiz(prefix)
            st.rerun()


# ── 라우터 ───────────────────────────────────────────────
def show_student_quiz(grade_group: str):
    apply_css()
    prefix = f"quiz_{grade_group}"
    init_quiz(prefix)
    page = st.session_state[f"{prefix}_page"]
    if page == "info":
        show_info_page(prefix, grade_group)
    elif page == "quiz":
        show_quiz_page(prefix, grade_group)
    elif page == "result":
        show_result_page(prefix, grade_group)
