from fastapi import FastAPI

api = FastAPI()

@api.get('/calculate_similarity')
def ask_gpt4(key:str, question: str, answer: str, user_answer: str):
    import openai
    import re  # 숫자만 추출하기 위해 정규표현식 사용

    # OpenAI API Key 설정
    openai.api_key = key

    result_return = 0
    # 만약 answer와 user_answer가 완전히 동일하면 0을 반환
    if question == user_answer:
        return result_return  # 두 문장이 완전히 같으면 유사도 0 반환
    
    else:
        # 요청 내용 포맷팅
        content = f"""
        {answer}와 {user_answer} 두 문장의 유사도의 퍼센트 검사해줘. 그리고 답변은 반드시 숫자만 사용해서 말해줘. 예를 들어 유사도가 95%가 나온다면 "95%"라고 숫자만 보내줘.
        또한, 답안지와 정답에 써있는 단어가 같은 의미를 갖고 있다면 일치하다고 판단해줘. 예를 들어 "푸드"와 "음식"은 같은 의미야. 이런것처럼 문제와 답안지 그리고 정답을 보고 판단해줘.

        문제 : {question}
        답안지 : {user_answer}
        정답 : {answer}

        유사도는 꼭 숫자만! 출력해.
        문장이 얼마나 유사한지 값을 측정하기 힘들어도 숫자로 무조건 출력해주는거야. 정확하지 않아도 대략적으로라도 출력해줘!!
        """

        # OpenAI GPT-4 API 요청
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": content}
            ]
        )

        # 응답에서 숫자만 추출
        gpt_response = response['choices'][0]['message']['content'].strip()

        # 정규 표현식을 사용해 숫자만 추출
        similarity_score = re.findall(r'\d+', gpt_response)
        # result_return = similarity_score[0] if similarity_score else gpt_response
        # # 추출된 숫자가 있으면 첫 번째 값을 반환, 없으면 원래 응답 반환
        # return result_return
        if similarity_score:
            result_return = similarity_score[0]
            return result_return
            
        else:
            result_return = -50

            return result_return
