<img src="https://capsule-render.vercel.app/api?type=venom&height=300&color=gradient&text=Project_OS_Final&fontColor=BLACK&fontSize=70&descAlign=50">

# project-OS-Final
OpenSW 최종 과제 결과물 입니다

# 설명
## 1. client 폴더

client에서 사용할 html이 모여있는 폴더 입니다.
실제로 서버 가동시 사용되는 폴더는 아니며, html만을 모아 놓은 것입니다.
서버 가동시 접속은 `http://localhost:3000` 입니다

<br>

### repository 구조

```
📁 models                       ← 감정을 나타내는 3D GLB 파일들
├── 📄 angry.glb                ← 분노 감정 모델 
├── 📄 anxious.glb              ← 불안 감정 모델 
├── 📄 happy.glb                ← 기쁨 감정 모델 
├── 📄 normal.glb               ← 중립 감정 모델 
└── 📄 sad.glb                  ← 슬픔 감정 모델 

📁 public                       ← 정적 파일(CSS, JS) 저장 위치 
├── 📁 css
│   └── 📄 dashboard.css        ← 대시보드의 스타일을 정의한 CSS 파일 
└── 📁 js
    └── 📄 dashboard.js         ← 대시보드의 주요 기능 구현 JavaScript 파일 

📁 template                     ← 렌더링될 HTML 템플릿 페이지들 
├── 📄 dashboard.html           ← 메인 대시보드 페이지
├── 📄 login.html               ← 로그인 페이지 
├── 📄 project_os_intro.html    ← 최초 접속 페이지 
└── 📄 signup.html              ← 회원가입 페이지 
```

<br>

## 2. server 폴더

server 역할을 하는 server.js와 그외의 서버에서 필요한 파일이 모여있습니다.
client에 전송할 html 파일은 `/server/template` 폴더 내부에 있습니다.

서버를 구동하기 위해서는 다음의 절차를 따라야 합니다.

1. server.js가 위치한 경로에서 `npm install`을 하여 필요한 모듈을 다운 받습니다.
2. 감정 분석을 하기 위해 필요한 python 모듈을 다운 받습니다. `pip install transformers torch eunjeon`을 실행시키면 됩니다
3. Mysql 서버를 준비합니다.
4. Mysql 서버에 `receipt_app` 이름의 DATABASE를 생성합니다.
5. 이후 필요 테이블을 생성합니다. 예제 코드는 아래에 있습니다.
6. `server.js`에서 `const db = mysql.createPool()` 부분을 자신의 유저명과 비밀번호 등 Mysql 환경과 맞게 설정합니다.
7. `config/database.js`에서 `const createPool = () => ...` 부분을 Mysql 환경과 맞게 설정합니다.
8. `server.js`가 있는 경로에서 `node server.js`로 nodejs 서버를 실행시킵니다

### MySQL 데이터베이스 생성 쿼리
```SQL
-- 데이터베이스가 없다면 생성, 명시한 DB 사용
CREATE DATABASE IF NOT EXISTS receipt_app;
USE receipt_app;

-- user 테이블 생성 (변동 없음)
CREATE TABLE IF NOT EXISTS user (
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- receipt 테이블 생성 (자료형 변경 반영)
CREATE TABLE IF NOT EXISTS receipt (
    receipt_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    receipt_date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    total_amount INT NOT NULL, -- DECIMAL에서 INT로 다시 변경
    emotion_type VARCHAR(20) NULL COMMENT '영수증에 기록된 감정 유형',
    emotion_description TEXT NULL COMMENT '감정에 대한 설명',
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);
```


