from adafruit_servokit import ServoKit
import board
import busio
import RPi.GPIO as GPIO  # Importar la librería GPIO para los pines de la Raspberry Pi

class ServoMotor:
    def __init__(self):
        # Configuración del bus I2C
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)

        # Inicializar el PCA9685
        self.kit = ServoKit(channels=16, i2c=self.i2c_bus)

        # Configuración del rango de ángulos del servo
        for servo_channel in range(16):
            self.kit.servo[servo_channel].set_pulse_width_range(500, 2500)  # Ajusta estos valores si es necesario

        # Inicializar servos controlados por pines de la Raspberry Pi
        self.rpi_servos = [12, 13, 18]  # Pines GPIO utilizados
        GPIO.setmode(GPIO.BCM)
        for pin in self.rpi_servos:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.PWM(pin, 50).start(0)  # Iniciar PWM a 50Hz

    def setServoAngle(self, index, angle):
        if 0 <= index < 16:
            self.kit.servo[index].angle = angle
        elif 16 <= index < 19:
            dutyCycle = self.mapAngleToDutyCycle(angle)
            GPIO.PWM(self.rpi_servos[index - 16], 50).ChangeDutyCycle(dutyCycle)
    
    def mapAngleToDutyCycle(self, angle):
        return 2.5 + (12.0 - 2.5) * angle / 180

