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


### ✅ 주요 기능
#### 1. 🔐 로그인/로그아웃
- 사용자 ID/PW로 로그인 인증
- 성공 시 관리자 대시보드(`/main`)로 이동
- `session`을 사용하여 사용자 상태 유지
- 로그아웃 시 세션 데이터 초기화
```python
  if 'user_nick' not in session:
      return redirect(url_for('mainlogin'))
```

#### 2.💡 LED 전원 ON/OFF
- `/ledControl` 라우트에서 버튼 클릭 시 LED 전원 제어
- LED 3색(빨강, 파랑, 초록)을 동시에 켜 흰색을 표현
- AJAX 요청을 통해 버튼 상태 비동기 반영

#### 3.🌡️ 온습도 측정 및 기록
- DHT11 센서로 실시간 온도, 습도 측정
- 웹페이지 버튼 클릭 시 `/measure`로 POST 요청
- 측정된 값은 MySQL DB(`tempHumData` 테이블)에 저장
- 최신 기록은 `/main` 페이지에 자동 출력

#### . 🚨 환경 감시 및 알림 시스템
- 측정값을 기반으로 경보 동작
| 조건                      | 반응                         |
| ----------------------- | -------------------------- |
| **18℃ ≤ 온도 ≤ 25℃**      | 녹색 LED 깜빡임 (적정 환경 표시)      |
| **온도 ≥ 35℃ 및 습도 ≥ 80%** | 부저 울림 + 빨간색 LED 깜빡임 (총 5회) |


#### 5. 🔐 페이지 접근 제어 (보안)
- `/main`, `/ledControl`, `/measure` 등 모든 주요 페이지는 로그인 세션 확인
- 로그인하지 않은 사용자는 자동으로 로그인 페이지로 리다이렉트됨