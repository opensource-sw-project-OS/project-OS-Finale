#from konlpy.tag import Okt
from eunjeon import Mecab
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
#import torch

model_name = "nlp04/korean_sentiment_analysis_dataset3_best"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

from transformers.utils import logging
logging.set_verbosity_error()  # GPU 사용 로그 출력 제어

classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)
model.eval()


def extract_cause(tokens):
    print("here")
    for word, pos in tokens:
        if 'EC' in pos:
            print(f"EC 포함 어절: {word}, 품사: {pos}")
    return "원인 없음"


def extract_cause_by_pos(tokens):
    """
    형태소 분석 결과가 주어졌을 때, 원인 구간(문자열)을 추출한다.
    - tokens: List of (word, pos) tuples
    - return: 추출된 원인 문자열 or "원인 없음"
    """
    # # 1. 결과 → 원인 구조 탐지 (기준: VV+EP + ETN + NNB)
    # 이부분은 제대로 구현하기 힘들 것 같아서 일단 보류
    # for i in range(len(tokens) - 2):
    #     pos1 = tokens[i][1]
    #     pos2 = tokens[i + 1][1]
    #     pos3 = tokens[i + 2][1]

    #     if pos1.startswith('VV') and 'EP' in pos1 \
    #        and pos2 == 'ETN' and tokens[i + 2][0] == '때문':
    #         return tokens[:i+1]
    
    # 2-1: VV+EC → 원인절
    for i, (word, pos) in enumerate(tokens):
        if 'VV+EC' in pos:
            return tokens[:i+1]  # VV+EC까지 포함해서 잘라냄
    
    # 3: '때문' 등장 → 그 앞까지가 원인절
    for i, (word, pos) in enumerate(tokens):
        if word == '때문':
            return tokens[:i+1]  # '때문' 포함해서 리턴
    
    # 2-2. 원인 → 결과 구조 (기준: VV+EC)
    for i, (word, pos) in enumerate(tokens):
        if 'EC' in pos:
            return tokens[:i+1]

    # 4. 원인 없을 경우 (EC도 보이지 않음)

    return None

def restore_korean_spacing(pos_tags):
    """
    형태소 분석 결과를 기반으로, 조사·어미 품사를 고려해 자연스러운 문장 복원을 수행합니다.
    
    :param pos_tags: list of (word, pos) 튜플
    :return: 사람이 읽기 좋은 형태의 자연스러운 문장 문자열
    """
    result = ""
    for i, (word, pos) in enumerate(pos_tags):
        # 1. 문장 첫 단어는 무조건 붙이기
        if i == 0:
            result += word
            continue

        # 2. 아래 품사들은 앞 단어에 붙이기 (조사, 어미, 접속사 등)
        if pos.startswith(("J", "E", "X")):  # J: 조사, E: 어미, X: 접사/보조사
            result += word
        # 3. 기호(마침표, 쉼표)는 앞 단어에 붙이되 뒤에 띄어쓰기 안함
        elif pos.startswith("S"):  # S: 기호 (SF, SP 등)
            result += word
        # 4. 나머지는 앞에 띄어쓰기
        else:
            result += " " + word

    return result.strip()

def extract_and_restore_cause(pos_tags):
    """
    원인 절을 추출한 뒤, 사람이 읽을 수 있는 자연어 문장으로 복원
    :param pos_tags: 형태소 분석 결과
    :return: 원인 절 문자열 or "원인 없음"
    """
    cause_pos = extract_cause_by_pos(pos_tags)
    if cause_pos:
        return restore_korean_spacing(cause_pos)
    else:
        return None





def evaluate_spending(avr_spend, today_spend):

    # 지출 차이 계산
    diff = today_spend - avr_spend
    if avr_spend != 0 :
        diff_percent = round(abs(diff) / avr_spend * 100)
    else :
        diff_percent = '*'
    diff_abs = abs(diff)

    # 혼합 기준에 의한 지출 상태 판단
    if today_spend > avr_spend * 1.10 and diff_abs > 5000:
        spending_status = "많다"
    elif today_spend < avr_spend * 0.90 and diff_abs > 5000:
        spending_status = "적다"
    else:
        spending_status = "비슷하다"

    
    return diff_abs, diff_percent, spending_status

# percent, spend_review = evaluate_spending(avr_spend, today_spend)
# print(f"{percent} {spend_review}")


def compose_final_message(emo_type, cause, spend_review, percent, diff):
    
    # 감정 그룹 분류
    positive_emotions = ["기쁨", "중립"]
    negative_emotions = ["슬픔", "불안", "분노", "당황", "혐오"] # 확장 가능

    # 1?? 감정 표현
    first = f"너의 문장을 보니 {emo_type}이 느껴졌어."

    # 2?? 원인 공감 or 커버 문장
    if cause and cause != "None":
        if cause.endswith("서"):
            second = f"{cause} 그랬구나."
        else:
            second = f"{cause}서 그랬구나."
    else:
        second = "말하지 못한 이유가 있었겠지. 괜찮아."

    # 3?? 지출 평가 문장
    # 접속어 선택
    if emo_type in positive_emotions:
        connector = {
            "많다": "그런데",
            "비슷하다": "그리고",
            "적다": "거기다"
        }[spend_review]
    else:
        connector = {
            "많다": "그래서",
            "비슷하다": "하지만",
            "적다": "그런데도"
        }[spend_review]

    # 지출 평가 문장 생성
    if spend_review == "많다":
        feedback = f"최근 지출에 비해서 {diff}원({percent}%) 많이 쓴 것 같아."
    elif spend_review == "적다":
        feedback = f"최근 지출보다 {diff}원({percent}%)나 줄였다니 대단해."
    else:
        feedback = "오늘은 평소처럼 무리 없이 잘 소비한 것 같아."

    # 결과 반환
    third = f"{connector} {feedback}"

    # 4?? 감정-지출 기반 위로 문장
    if emo_type == "기쁨":
        if spend_review == "많다":
            fourth = "기쁜 마음에 나를 위해 쓰는 것도 좋아. 하지만 예산도 함께 챙겨보자."
        elif spend_review == "비슷하다":
            fourth = "평소대로 지낸 하루, 그 자체로도 충분히 괜찮아."
        else:
            fourth = "행복한 기분에 절제까지 해냈다니, 스스로를 칭찬해도 돼."
    elif emo_type == "중립":
        if spend_review == "많다":
            fourth = "무의식 중에 지출이 늘었을 수 있어. 다음엔 조금만 더 의식해보자."
        elif spend_review == "비슷하다":
            fourth = "특별한 일 없이 평소처럼 지낸 하루였어."
        else:
            fourth = "자연스러운 하루였고, 무리하지 않아 보여."
    else:
        if spend_review == "많다":
            fourth = "힘들 땐 소비로 위안받기도 해. 너무 자책하지 않아도 돼."
        elif spend_review == "비슷하다":
            fourth = "마음이 어려워도 흐트러지지 않은 하루였어."
        else:
            fourth = "기분이 안 좋은데도 절제했다는 게 참 대단해."

    # 5?? 정서적 마무리
    closing = "오늘 하루도 잘 버텨냈어. 내일은 더 괜찮을 거야."

    return "\n".join([first, second, third, fourth, closing])


def wrapping(text="", today_spend = 0, avr_spend = 0) :
    emo_type = classifier(text)[0]['label']
    #기존의 7가지 라벨을 5가지 라벨 -> 기쁨, 중립, 슬픔, 불안, 분노 로 바꾸는 코드
    if emo_type == "행복":
        emo_type = "기쁨"
    elif emo_type == "당황" :
        emo_type = "불안"
    elif emo_type == "혐오" :
        emo_type = "분노"

    mecab = Mecab()
    morph = mecab.pos(phrase=text)
    cause = extract_and_restore_cause(morph)
    diff, percent, spend_review = evaluate_spending(avr_spend, today_spend)

    result = compose_final_message(emo_type, cause, spend_review, percent, diff)
    return emo_type, result


import sys
import json

for line in sys.stdin:
    try:
        data = json.loads(line) # json 형식의 파일을 json으로 입력 받음(사실 여기선 dictionary처럼 다뤄짐)
        if 'data' not in data:
            raise KeyError('해당하는 property가 없습니다')
        
        text = data['data']
        avr_spend = data['avr']
        today_spend = data['spend']
        
        result = {} # dictionary
        
        result['emotion'], result['data'] = wrapping(text, today_spend, avr_spend)

        #result['점수'] = any_function(text)
   
        # dictionary를 json.dumps()를 통해 json으로 변환함
        # 여기서의 print는 nodejs 서버에 결과를 전달하는 역할
        print(json.dumps(result, ensure_ascii=False))
        #print(data)
        sys.stdout.flush()
        
    except Exception as e:
        print(json.dumps({ "err": str(e) }), file=sys.stderr)
        sys.stdout.flush()