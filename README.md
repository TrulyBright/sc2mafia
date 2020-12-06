# SC2 Mafia!
**회원가입 및 로그인 과정에 SQL Injection 취약점이 있습니다. 상용 사용 금지!**

스타크래프트 2의 유명 아케이드 '-마피아-'를 웹게임으로 구현했습니다.
## 실행 방법(리눅스 기준)
1. 이 레포지토리를 복사합니다.
```
$ git clone https://github.com/TrulyBright/sc2mafia
```
2. SQLite3을 설치합니다.
```
$ sudo apt-get install sqlite3
```
3. redis를 설치합니다.
```
$ sudo apt-get install redis
```
4. 레포지토리를 복사한 디렉토리에 들어갑니다.
```
$ cd sc2mafia
```
5. 파이썬 패키지들을 설치합니다.
```
$ pip install -r requirements.txt
```
6. SQLite DB 스키마를 적용합니다.
```
$ sqlite3 sql/users.db < sql/schema.sql
```
7. 서버를 실행합니다.
```
$ python main.py
```
8. `localhost:8080`으로 접속하면 사이트가 나옵니다.

## 구현된 기능

## 구현된 직업

## 보안 문제
