import time
from servo_motor import ServoMotor
import asyncio

class MainLoop:
    def __init__(self, buttonManager, servoManager, movementService, positionService, videoControlService):
        self.buttonManager = buttonManager
        self.servoManager = servoManager
        self.movementService = movementService
        self.positionService = positionService
        self.videoControlService = videoControlService
        self.servoMotor = ServoMotor()
        self.isMoving = False

    def moveServosToPositions(self, targetAngles, duration):
        initialAngles = {servo.id: servo.angle for servo in self.servoManager.servos}
        startTime = time.monotonic()
        endTime = startTime + duration / 1000.0
        lastUpdateTime = startTime

        while time.monotonic() < endTime:
            currentTime = time.monotonic()
            if currentTime - lastUpdateTime > 0.01:  # 10 ms intervalo de actualización
                lastUpdateTime = currentTime
                elapsedTime = currentTime - startTime
                progress = elapsedTime / (duration / 1000.0)
                for servoId, targetAngle in targetAngles.items():
                    initialAngle = initialAngles[servoId]
                    newAngle = self.lerp(initialAngle, targetAngle, progress)
                    self.servoMotor.setServoAngle(servoId - 1, newAngle)

        # Asegurar que los servos alcanzan la posición final
        for servoId, targetAngle in targetAngles.items():
            self.servoMotor.setServoAngle(servoId - 1, targetAngle)

        # Actualizar los ángulos iniciales con los objetivos finales
        for servo in self.servoManager.servos:
            if servo.id in targetAngles:
                servo.angle = targetAngles[servo.id]

    def lerp(self, start, end, progress):
        return (1 - progress) * start + progress * end

    async def run(self):
        while True:
            if self.positionService.executeMovementBoolean:
                for position in self.positionService.positions:
                    angles = position.angles
                    targetAngles = {angle['id']: angle['angle'] for angle in angles}
                    self.moveServosToPositions(targetAngles, position.time)
                self.positionService.executeMovementBoolean = False
            elif self.positionService.moveToInitialPositionsBoolean:  # Cambiado de `else if` a `elif`
                self.servoManager.loadConfig()
                self.positionService.moveToInitialPositionsBoolean = False
            else:
                for servo in self.servoManager.servos:
                    self.servoMotor.setServoAngle(servo.id - 1, servo.angle)

            await asyncio.sleep(0.01)

