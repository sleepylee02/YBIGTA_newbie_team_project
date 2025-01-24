# YBIGTA Newbie Team Project

## 팀 소개

TEAM 1

- **이재영**: 안녕하세요~ 저는 응용통계학과 21학번 이재영입니다! 데이터 관련 프로젝트를 좋아해서 da 팀으로 지원했습니다!! 반갑습니다 :)
- **송휘린**: 안녕하세요!! 저는 응통 23학번 송휘린입니다. 모든게 초보지만 열심히 배우겠습니다.
- **강정묵**: 안녕하세요. 22학번 응용통계학과 강정묵입니다.

---
## 크롤링 프로젝트

_리뷰 데이터 수집_

장소: **성심당**

데이터 소개:

+ 구글 맵 : 사용자 이름, 사용자 정보, 별점, 날짜, 리뷰, 사진/ 각 지점별 3000개 이상/ (https://www.google.com/maps/place/%EC%84%B1%EC%8B%AC%EB%8B%B9+DCC%EC%A0%90/data=!4m8!3m7!1s0x3565498ff8570165:0x8cd47008647df355!8m2!3d36.3753313!4d127.3924207!9m1!1b1!16s%2Fg%2F11f0kvfpj0?entry=ttu&g_ep=EgoyMDI1MDEyMS4wIKXMDSoASAFQAw%3D%3D, https://www.google.com/maps/place/Sungsimdang+Bakery+Lotte+Daejeon+Branch/data=!4m8!3m7!1s0x3565495a46274a79:0x5b973bd3cfd7d125!8m2!3d36.3403653!4d127.3901764!9m1!1b1!16s%2Fg%2F1ptxmrrlz?entry=ttu&g_ep=EgoyMDI1MDEyMS4wIKXMDSoASAFQAw%3D%3D, https://www.google.com/maps/place/%EC%84%B1%EC%8B%AC%EB%8B%B9+%EB%B3%B8%EC%A0%90/data=!4m8!3m7!1s0x356548d8f73d355d:0x69e930d902c95eca!8m2!3d36.3276832!4d127.4273424!9m1!1b1!16s%2Fg%2F1tct_8rr?entry=ttu&g_ep=EgoyMDI1MDEyMC4wIKXMDSoASAFQAw%3D%3D)
+ 카카오 지도 : 사용자 이름, 사용자 정보, 날짜, 별점, 리뷰, 태그/ 총 5000개 이상/ (https://place.map.kakao.com/17733090)
+ 다이닝 코드 : 사용자 이름, 사용자 정보, 별점, 평가, 리뷰, 사진, 태그 / 총 200개 이상/(https://www.diningcode.com/profile.php?rid=LtMjLaf0kZJC)

실행방법: 


---


## Branch Protection Rule
![Branch Protection Rule](github/branch_protection.png)

## Push Rejected Example
![Push Rejected](github/push_rejected.png)

## Merged Branches
![Mookjsi](github/merged_Mookjsi.png)
![sleepylee02](github/merged_sleepylee02.png)
![Hwiplash](github/merged_Hwiplash.png)
---

## 프로젝트 소개
이 프로젝트는 FastAPI를 기반으로 사용자 관리 기능(로그인, 회원가입, 계정 삭제, 비밀번호 변경)을 제공하는 웹 애플리케이션입니다. 사용자는 간단한 절차를 통해 계정을 생성하고, 로그인하여 서비스를 이용할 수 있습니다.

---

## 사용 방법

### **1. 가상환경 설정 및 서버 실행**

1. **가상환경 활성화**:
   - 터미널 또는 명령 프롬프트에서 프로젝트 디렉토리로 이동 후, 아래 명령어를 실행합니다.
     - Windows:
       ```bash
       venv\Scripts\activate
       ```
     - Linux/Mac:
       ```bash
       source venv/bin/activate
       ```

2. **서버 실행**:
   - 아래 명령어를 입력하여 FastAPI 서버를 실행합니다:
     ```bash
     uvicorn app.main:app --reload
     ```
   - 실행 후, 터미널에 `Uvicorn running on http://127.0.0.1:8000`와 같은 메시지가 출력됩니다.

---

### **2. 웹페이지 접속 및 테스트**

1. **HTML 페이지 접속**:
   - 웹 브라우저를 열고 다음 URL을 입력합니다:
     ```
     http://127.0.0.1:8000/static/index.html
     ```
   - 페이지가 열리면 회원가입, 로그인, 비밀번호 변경, 계정 삭제 기능을 사용할 수 있습니다.

2. **회원가입**:
   - **회원가입 섹션**에서 다음 정보를 입력합니다:
     - 이메일 주소
     - 비밀번호
     - 사용자 이름
   - **회원가입 버튼**을 클릭하면 계정이 생성됩니다.
   - 성공 메시지가 표시되면 회원가입이 완료된 것입니다.

3. **로그인**:
   - **로그인 섹션**에서 이메일과 비밀번호를 입력합니다.
   - **로그인 버튼**을 클릭하면 로그인 성공 여부가 화면에 표시됩니다.
   - 성공적으로 로그인되면 환영 메시지가 나타납니다.

4. **비밀번호 변경**:
   - 로그인한 상태에서 **비밀번호 변경 섹션**으로 이동합니다.
   - 새 비밀번호를 입력한 뒤, **변경 버튼**을 클릭합니다.
   - 성공 메시지가 나타나면 비밀번호가 변경된 것입니다.

5. **계정 삭제**:
   - 로그인한 상태에서 **계정 삭제 섹션**으로 이동합니다.
   - **삭제 버튼**을 클릭하면 계정이 삭제됩니다.
   - 성공 메시지가 표시되며, 계정이 삭제되고 로그아웃됩니다.

---

## 문의 사항

서비스 이용 중 문제가 발생하거나 도움이 필요하면 관리자에게 문의하세요.
- 이메일: nickjmk1006@gmail.com

