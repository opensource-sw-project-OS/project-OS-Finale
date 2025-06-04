# project-OS-Finale
OpenSW 최종 과제 결과물 입니다

# 설명
## 1. client 폴더

client에서 사용할 html이 모여있는 폴더 입니다.

project_os_intro.html 에서 시작하여 로그인/회원가입후 사용하면 됩니다.


## 2. server 폴더

server 역할을 하는 server.js와 그외의 서버에서 필요한 파일이 모여있습니다.

서버를 구동하기 위해서는 다음의 절차를 따라야 합니다.

1. server.js가 위치한 경로에서 `npm install`을 하여 필요한 모듈을 다운 받습니다.
2. Mysql 서버를 준비합니다.
3. Mysql 서버에 `receipt_app` 이름의 DATABASE를 생성합니다.
4. 이후 필요 테이블을 생성합니다. 예제 코드는 아래에 있습니다.
5. `server.js`에서 `const db = mysql.createPool()` 부분을 자신의 유저명과 비밀번호 등 Mysql 환경과 맞게 설정합니다.
6. `config/database.js`에서 `const createPool = () => ...` 부분을 Mysql 환경과 맞게 설정합니다.
7. `server.js`가 있는 경로에서 `node server.js`로 nodejs 서버를 실행시킵니다
