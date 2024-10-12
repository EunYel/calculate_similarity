from fastapi import FastAPI

api = FastAPI()

@api.get('/calculate_similarity')
def calculate_similarity(key: str, question: str, answer: str, user_answer: str):
    import re  # 숫자만 추출하기 위해 정규표현식 사용
    import requests

    result_return = 0

    # 만약 answer와 user_answer가 완전히 동일하면 0을 반환
    if question == user_answer:
        return result_return  # 두 문장이 완전히 같으면 유사도 0 반환

    else:
        # similarity API 요청
        url = "http://34.64.252.14:5000/similarity"
        data = {
            "text1": answer,
            "text2": user_answer
        }
        # POST 요청을 보내고 응답 받기
        try:
            response = requests.post(url, json=data, timeout=4)

            # 상태 코드와 응답 확인
            if response.status_code == 200:
                result_return = response.json().get('similarity', None)
                if result_return is not None:
                    result_return = result_return * 100
                else:
                    return -50
            else:
                # Error 처리
                return -50

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return -50

        # 만약 result_return 값이 None이라면, OpenAI GPT-4 API 호출
        if result_return is None:
            # OpenAI GPT-4 API 호출
            import openai
            openai.api_key = key

            # 요청 내용 포맷팅
            content = f"""
            {answer}와 {user_answer} 두 문장의 유사도의 퍼센트 검사해줘. 그리고 답변은 반드시 숫자만 사용해서 말해줘. 예를 들어 유사도가 95%가 나온다면 "95%"라고 숫자만 보내줘.
            또한, 답안지와 정답에 써있는 단어가 같은 의미를 갖고 있다면 일치하다고 판단해줘. 예를 들어 "푸드"와 "음식"은 같은 의미야. 이런 것처럼 문제와 답안지 그리고 정답을 보고 판단해줘.

            문제 : {question}
            답안지 : {user_answer}
            정답 : {answer}

            유사도는 꼭 숫자만! 출력해.
            문장이 얼마나 유사한지 값을 측정하기 힘들어도 숫자로 무조건 출력해주는 거야. 정확하지 않아도 대략적으로라도 출력해줘!!
            """

            # OpenAI GPT-4 API 요청
            gpt_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": content}
                ]
            )

            # 응답에서 숫자만 추출
            gpt_content = gpt_response['choices'][0]['message']['content'].strip()

            # 정규 표현식을 사용해 숫자만 추출
            similarity_score = re.findall(r'\d+', gpt_content)

            # 추출된 유사도 값이 있으면 반환, 없으면 오류 처리
            if similarity_score:
                result_return = int(similarity_score[0])  # 첫 번째 숫자 추출'
                return result_return
            else:
                return -50  # 숫자가 없을 경우 -50 반환

        return result_return
