from flask import Flask, request, render_template, url_for, session, redirect, jsonify
import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import mysql.connector
import atexit
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'test_1234'  # 세션을 위한 시크릿 키 추가

# DB 연결을 함수로 만들어 연결 끊김 문제 해결
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="test",
            password="12345",
            database="test_db"
        )
        return conn
    except Error as e:
        print(f"DB 연결 오류: {e}")
        return None
    
BUZZER = 18
LED_GREEN = 23
LED_RED = 2
LED_BLUE = 4
led_state = False

# GPIO 초기화 함수
def init_gpio():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUZZER, GPIO.OUT)
        GPIO.setwarnings(False)  # 경고 메시지 비활성화
        
        # 핀이 이미 사용 중인 경우를 대비해 정리
        try:
            GPIO.cleanup(LED_GREEN)
            GPIO.cleanup(LED_RED)
            GPIO.cleanup(LED_BLUE)
        except:
            pass
            
        GPIO.setup(LED_GREEN, GPIO.OUT)
        GPIO.setup(LED_RED, GPIO.OUT)
        GPIO.setup(LED_BLUE, GPIO.OUT)

        GPIO.output(LED_GREEN, GPIO.LOW)  # LED 초기 상태: OFF
        GPIO.output(LED_RED, GPIO.LOW)  # LED 초기 상태: OFF
        GPIO.output(LED_BLUE, GPIO.LOW)  # LED 초기 상태: OFF

        print(f"GPIO {LED_GREEN} 초기화 완료")
        print(f"GPIO {LED_RED} 초기화 완료")
        print(f"GPIO {LED_BLUE} 초기화 완료")
        return True
    except Exception as e:
        print(f"GPIO 초기화 오류: {e}")
        return False
    
def trigger_alarm():
    for _ in range(5):
        GPIO.output(BUZZER, True)
        GPIO.output(LED_RED, True)
        time.sleep(0.3)
        GPIO.output(BUZZER, False)
        GPIO.output(LED_RED, False)
        time.sleep(0.3)

def normal_alarm():
    for _ in range(3):
        GPIO.output(LED_GREEN, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(LED_GREEN, GPIO.LOW)  # LED 초기 상태: OFF
        time.sleep(0.3)


# GPIO 초기화 실행
gpio_initialized = init_gpio()

# DHT11 센서를 GPIO 21번 핀에 연결
try:
    dht = adafruit_dht.DHT11(board.D21)
except Exception as e:
    print(f"DHT 센서 초기화 오류: {e}")
    dht = None

@app.route('/')
def mainlogin():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def main():
    global led_state

    user_id = request.form['id']
    password = request.form['pw']

    # 사용자 인증
    user = authenticate_user(user_id, password)
    
    if user:
        user_nick = user[0]
        # 메인 페이지로 리다이렉트하여 중복 코드 제거
        # session['logged_in'] = True 
        session['user_nick'] = user_nick  # 세션에 사용자 정보 저장
        return redirect(url_for('main_page'))
    else:
        state = "LOGIN FAIL. TRY AGAIN"
        return render_template("index.html", state=state)

@app.route('/main')
def main_page():
    if 'user_nick' not in session:
        return redirect(url_for('mainlogin'))

    user_nick = session['user_nick']

    #📋 최근 온습도 정보 불러오기
    temp_data = get_latest_temp_humid_data()

    button_text = "OFF" if led_state else "ON"

    return render_template("main.html", 
        temp=temp_data['temp'], 
        humid=temp_data['humid'], 
        date=temp_data['date'],
        user_nick=user_nick, 
        button_text=button_text, 
        led_state=led_state,
        login_form=False)

@app.route("/ledControl", methods=['POST'])
def led_control():
    global led_state
    
    # 로그인 체크
    if 'user_nick' not in session:
        return redirect(url_for('mainlogin'))
    
    # GPIO 초기화 체크
    if not gpio_initialized:
        error_msg = "GPIO가 초기화되지 않았습니다"
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 500
        else:
            return redirect(url_for('main_page'))
    
    try:
        # LED 상태 토글
        led_state = not led_state
        if led_state:
            # 흰색 켜기
            GPIO.output(LED_RED, GPIO.HIGH)
            GPIO.output(LED_GREEN, GPIO.HIGH)
            GPIO.output(LED_BLUE, GPIO.HIGH)
        else:
            # 모두 끄기
            GPIO.output(LED_RED, GPIO.LOW)
            GPIO.output(LED_GREEN, GPIO.LOW)
            GPIO.output(LED_BLUE, GPIO.LOW)

        print(f"LED 상태: {'ON' if led_state else 'OFF'}")
        
        # AJAX 요청인지 확인
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            # AJAX 응답: JSON으로 상태만 반환
            return jsonify({
                'success': True,
                'led_state': led_state,
                'button_text': 'OFF' if led_state else 'ON'
            })
        else:
            # 일반 폼 요청: 메인 페이지로 리다이렉트
            return redirect(url_for('main_page'))
            
    except Exception as e:
        print(f"LED 제어 오류: {e}")
        
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            # 오류 시에도 메인 페이지로 돌아가기
            return redirect(url_for('main_page'))

# 헬퍼 함수들
def authenticate_user(user_id, password):
    """사용자 인증"""
    conn = get_db_connection()  # 수정: 연결 함수 사용
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        sql = "SELECT user_nick FROM user WHERE user_id=%s AND password=%s"
        cursor.execute(sql, (user_id, password))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"사용자 인증 오류: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_latest_temp_humid_data():
    """최신 온습도 데이터 조회"""
    conn = get_db_connection()  # 수정: 연결 함수 사용
    if not conn:
        return {'temp': "DB 연결 오류", 'humid': "DB 연결 오류", 'date': "DB 연결 오류"}
    try:
        cursor = conn.cursor()
        sql = "SELECT temp, humid, date FROM tempHumData ORDER BY date DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result:
            temp, humid, date = result
            return {'temp': temp, 'humid': humid, 'date': date}
        else:
            return {'temp': "데이터없음", 'humid': "데이터없음", 'date': "데이터없음"}
    except Error as e:
        print(f"데이터 조회 오류: {e}")
        return {'temp': "조회 오류", 'humid': "조회 오류", 'date': "조회 오류"}
    finally:
        if conn:
            conn.close()

# 로그아웃 라우트 추가
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_page'))
try:
    dht_device = adafruit_dht.DHT11(board.D21)
    print("DHT 센서 초기화 성공")
except Exception as e:
    print(f"DHT 센서 초기화 실패: {e}")
    dht_device = None

@app.route("/measure", methods=['POST'])
def measure():
    """한 번의 측정만 수행하고 결과 반환"""
    if not dht:
        return jsonify({'success': False, 'error': 'DHT 센서가 초기화되지 않았습니다'})
    
    try:
        # 센서에서 온도와 습도 값을 읽어옴
        temperature = dht.temperature
        humidity = dht.humidity

        if temperature is not None and humidity is not None:
            print(f"Temp: {temperature}°C")
            print(f"Humi: {humidity}%")
            print("-"*20)
            
            if(temperature >= 18 and temperature <= 25):
                # 정적온도일때
                normal_alarm()
            if(temperature >= 35 and humidity > 80):
                # 온도가 35도 이상 올라갈 경우 부저 5번 울림 + led 빨간색 켜졌다가 꺼짐 5번 반복
                trigger_alarm()

            # DB에 데이터 삽입
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    sql3 = "INSERT INTO tempHumData (temp, humid) VALUES (%s, %s)"
                    val = (temperature, humidity)
                    cursor.execute(sql3, val)
                    conn.commit()
                    
                    return jsonify({
                        'success': True,
                        'temperature': temperature,
                        'humidity': humidity,
                    })
                except Error as e:
                    print(f"DB 저장 오류: {e}")
                    return jsonify({'success': False, 'error': 'DB 저장 실패'})
                finally:
                    conn.close()
            else:
                return jsonify({'success': False, 'error': 'DB 연결 실패'})
        else:
            print("데이터 읽기 실패")
            return jsonify({'success': False, 'error': '센서 데이터 읽기 실패'})
        
    except RuntimeError as error:
        print(f"센서 읽기 오류: {error.args[0]}")
        return jsonify({'success': False, 'error': f'센서 오류: {error.args[0]}'})

# # 주기적 측정을 위한 별도 엔드포인트 (백그라운드 작업용)
# @app.route("/start_monitoring")
# def start_monitoring():
#     """주기적 모니터링 시작 (별도 스레드에서 실행하는 것을 권장)"""
#     return jsonify({'message': '별도의 백그라운드 프로세스로 구현하는 것을 권장합니다'})

@atexit.register
def cleanup():
    try:
        GPIO.cleanup()
        if dht:
            dht.exit()
        print("GPIO 및 센서 정리 완료")

    except Exception as e:
        print(f"정리 과정 오류: {e}")

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=1234)
    except KeyboardInterrupt:
        print("서버 종료 중...")
    finally:
        cleanup()