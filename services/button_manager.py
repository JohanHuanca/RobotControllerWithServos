import configparser
from typing import List
from dataclasses import asdict
from models import Button
from response_handler import ResponseHandler

class ButtonManager(ResponseHandler):
    def __init__(self, configFile='config.ini'):
        self.configFile = configFile
        self.config = configparser.ConfigParser()
        self.buttons = []
        self.numButtons = 0
        self.loadConfig()

    def loadConfig(self):
        self.config.read(self.configFile)
        if 'Buttons' not in self.config:
            self.config['Buttons'] = {'num_buttons': '10'}
        self.numButtons = int(self.config['Buttons']['num_buttons'])
        self.buttons: List[Button] = [Button(id=i, state=False) for i in range(1, self.numButtons + 1)]

    def saveConfig(self):
        with open(self.configFile, 'w') as configfile:
            self.config.write(configfile)
    
    def saveNumButtons(self):
        self.config['Buttons']['num_buttons'] = str(self.numButtons)
        self.saveConfig()

    async def createButton(self, data, websocket, requestId):
        if 'state' not in data or not isinstance(data['state'], bool):
            print("Datos de botón inválidos:", data)
            await self.sendErrorResponse(websocket, {"message": "Invalid button data"}, requestId)
            return
        
        self.numButtons += 1
        button = Button(id=self.numButtons, state=data['state'])
        self.buttons.append(button)
        self.saveNumButtons()
        print("Botón creado:", button)
        await self.sendResponse(websocket, asdict(button), requestId)

    async def updateButtonById(self, data, websocket, requestId):
        if 'id' not in data or 'state' not in data or not isinstance(data['id'], int) or not isinstance(data['state'], bool):
            print("Datos de actualización de botón inválidos:", data)
            await self.sendErrorResponse(websocket, {"message": "Invalid button data"}, requestId)
            return
        
        button = next((b for b in self.buttons if b.id == data['id']), None)
        if button:
            button.state = data['state']
            print("Botón actualizado:", button)
            await self.sendResponse(websocket, asdict(button), requestId)
        else:
            print("Botón no encontrado")
            await self.sendErrorResponse(websocket, {"message": "Button not found"}, requestId)

    async def deleteButton(self, websocket, requestId):
        if not self.buttons:
            await self.sendErrorResponse(websocket, {"message": "No buttons to delete"}, requestId)
            return
        
        button = self.buttons.pop()
        self.numButtons -= 1
        self.saveNumButtons()
        print("Botón eliminado:", button)
        await self.sendResponse(websocket, asdict(button), requestId)

    async def getButtonById(self, buttonId, websocket, requestId):
        if not isinstance(buttonId, int):
            print("ID de botón inválido:", buttonId)
            await self.sendErrorResponse(websocket, {"message": "Invalid button ID"}, requestId)
            return
        
        button = next((b for b in self.buttons if b.id == buttonId), None)
        if button:
            print("Obteniendo botón:", button)
            await self.sendResponse(websocket, asdict(button), requestId)
        else:
            print("Botón no encontrado")
            await self.sendErrorResponse(websocket, {"message": "Button not found"}, requestId)

    async def getAllButtons(self, websocket, requestId):
        print("Obteniendo todos los botones:", self.buttons)
        payload = {
            "total_items": len(self.buttons),
            "content": [asdict(button) for button in self.buttons]
        }
        await self.sendResponse(websocket, payload, requestId)
