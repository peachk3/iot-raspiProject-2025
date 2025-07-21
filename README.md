# iot-raspiProject-2025
## 🌡️ Raspberry Pi 온습도 모니터링 & LED 제어 웹 프로젝트

### 📌 개요
Flask 웹 서버를 통해 라즈베리파이에서 DHT11 센서로 온습도 데이터를 측정, GPIO를 활용해 LED를 제어할 수 있는 웹 기반 시스템 제작

### ⚙️ 주요 기능
- 사용자 로그인 기능 (MySQL 연동)
- DHT11 센서를 통한 온/습도 측정 및 DB 저장
- 가장 최근 온습도 데이터를 웹 페이지에 표시
- 웹 버튼을 통한 LED 제어
- 센서 데이터와 제어 상태는 MySQL에 저장

### 🧱 사용 기술
- Raspberry Pi
- Python (Flask, adafruit_dht, mysql-connector-python)
- HTML (Jinja2 템플릿)
- MySQL
- RPi.GPIO

### 🗃️ DB 테이블 구조 예시
```sql
-- 사용자 테이블
CREATE TABLE user (
  user_id VARCHAR(20) PRIMARY KEY,
  password VARCHAR(20),
  user_nick VARCHAR(30)
);

-- 온습도 데이터 저장 테이블
CREATE TABLE tempHumData (
  id INT AUTO_INCREMENT PRIMARY KEY,
  temp FLOAT,
  humid FLOAT,
  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
### 📌 라우팅 구조
| Route         | 설명                 |
| ------------- | ------------------ |
| `/`           | 로그인 페이지            |
| `/login`      | 로그인 처리 (POST)      |
| `/main`       | 메인 페이지 (센서 데이터 표시) |
| `/measure`    | 온습도 측정 및 저장        |
| `/ledControl` | LED On/Off 제어      |

### 🚨 주의 사항
- measure() 함수는 무한 루프이므로, 실제 서비스에서는 백그라운드 작업 혹은 쓰레드로 처리 필요
- GPIO는 프로그램 종료 시 반드시 GPIO.cleanup()으로 정리

### 📷 실행 화면 예시


### 목표
#### 1. 로그인
- **완료**  
- 입력된 ID/PW가 맞으면 관리자창으로 이동

#### 2. 회원가입

#### 3. 일정 주기 온습도 기록  
- **웹 페이지 버튼 클릭 기능 완료**  
  - 측정 후 웹페이지에 온도, 습도 출력

- **LED 색상으로 상태 표시 (예정)**  
  - 적정 온습도: 녹색 LED ON  
  - 온도 상승 시(더움): 빨간색 LED ON

#### 4. 온습도 경보 시스템 (환경 감시기)  
- 특정 수치 이상일 때 알림 발생  
  - 온도 > 30도 또는 습도 > 70% 시  
    - 부저 울림  
    - LED 깜빡임 (경고 표시)

- 버튼을 눌러 알람 끄기 기능 구현 예정

#### 5. 보안  
- `/main` 및 `/ledControl` 페이지에  
  로그인하지 않은 사용자의 접근 제한 필요