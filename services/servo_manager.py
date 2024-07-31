import json
from dataclasses import asdict
from models import Servo
from response_handler import ResponseHandler
import configparser
import time
import asyncio

class ServoManager(ResponseHandler):
    def __init__(self, configFile='config.ini'):
        self.configFile = configFile
        self.config = configparser.ConfigParser()
        self.servos = []
        self.numServos = 0
        self.loadConfig()

    def loadConfig(self):
        self.config.read(self.configFile)
        if 'Servos' not in self.config:
            defaultServos = [
                {"id": i, "angle": 90} for i in range(1, 20)
            ]
            self.config['Servos'] = {'initial_positions': json.dumps(defaultServos)}
        initialPositions = json.loads(self.config['Servos']['initial_positions'])
        self.servos = [Servo(**servo) for servo in initialPositions]
        self.numServos = len(self.servos)

    def saveConfig(self):
        with open(self.configFile, 'w') as configfile:
            self.config.write(configfile)

    def saveServoPositions(self):
        self.config['Servos']['initial_positions'] = json.dumps([asdict(servo) for servo in self.servos])
        self.saveConfig()

    async def savePosition(self, websocket, requestId):
        print("Guardando la posicion de todos los servos:", self.servos)
        self.saveServoPositions()
        await self.sendResponse(websocket, {"message": "Positions saved successfully"}, requestId)

    async def createServo(self, data, websocket, requestId):
        if 'angle' not in data or not isinstance(data['angle'], int) or isinstance(data['angle'], bool) or not (0 <= data['angle'] <= 180):
            print("Datos de servo inválidos:", data)
            await self.sendErrorResponse(websocket, {"message": "Invalid servo data: angle must be an integer between 0 and 180"}, requestId)
            return

        if len(self.servos) == 19:
            await self.sendErrorResponse(websocket, {"message": "Maximum Servos Created"}, requestId)
            return

        self.numServos += 1
        servo = Servo(id=self.numServos, angle=data['angle'])
        self.servos.append(servo)
        self.saveServoPositions()
        print("Servo creado:", servo)
        await self.sendResponse(websocket, asdict(servo), requestId)

    async def updateServoById(self, data, websocket, requestId):
        if 'id' not in data or 'angle' not in data or not isinstance(data['id'], int) or not isinstance(data['angle'], int) or isinstance(data['angle'], bool) or not (0 <= data['angle'] <= 180):
            print("Datos de actualización de servo inválidos:", data)
            await self.sendErrorResponse(websocket, {"message": "Invalid servo data: angle must be an integer between 0 and 180"}, requestId)
            return
        
        servo = next((s for s in self.servos if s.id == data['id']), None)
        if servo:
            servo.angle = data['angle']
            print("Servo actualizado:", servo)
            await self.sendResponse(websocket, asdict(servo), requestId)
        else:
            print("Servo no encontrado")
            await self.sendErrorResponse(websocket, {"message": "Servo not found"}, requestId)

    async def deleteServo(self, websocket, requestId):
        if not self.servos:
            await self.sendErrorResponse(websocket, {"message": "No servos to delete"}, requestId)
            return

        servo = self.servos.pop()
        self.numServos -= 1
        self.saveServoPositions()
        print("Servo eliminado:", servo)
        await self.sendResponse(websocket, asdict(servo), requestId)

    async def getServoById(self, servoId, websocket, requestId):
        if not isinstance(servoId, int):
            print("ID de servo inválido:", servoId)
            await self.sendErrorResponse(websocket, {"message": "Invalid servo ID"}, requestId)
            return

        servo = next((s for s in self.servos if s.id == servoId), None)
        if servo:
            print("Obteniendo servo:", servo)
            await self.sendResponse(websocket, asdict(servo), requestId)
        else:
            print("Servo no encontrado")
            await self.sendErrorResponse(websocket, {"message": "Servo not found"}, requestId)

    async def getAllServos(self, websocket, requestId):
        print("Obteniendo todos los servos:", self.servos)
        payload = {
            "total_items": len(self.servos),
            "content": [asdict(servo) for servo in self.servos]
        }
        await self.sendResponse(websocket, payload, requestId)
