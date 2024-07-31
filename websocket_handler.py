import json

class WebSocketHandler:
    def __init__(self, buttonManager, servoManager, movementService, positionService, videoControl):
        self.buttonManager = buttonManager
        self.servoManager = servoManager
        self.movementService = movementService
        self.positionService = positionService
        self.videoControl = videoControl

    async def handleMessage(self, websocket, path):
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                print('Error al decodificar el mensaje JSON')
                await self.sendErrorResponse(websocket, 'Invalid JSON', None)
                continue
            
            endpoint = data.get('endpoint')
            method = data.get('method')
            payload = data.get('payload', {})
            requestId = data.get('request_id')

            if not endpoint or not method:
                await self.sendErrorResponse(websocket, 'Invalid request', requestId)
                continue

            # Rutas para Button
            if endpoint.startswith("/app/buttons"):
                await self.handleButtonRequests(endpoint, method, payload, websocket, requestId)
            # Rutas para Servo
            elif endpoint.startswith("/app/servos"):
                await self.handleServoRequests(endpoint, method, payload, websocket, requestId)
            # Rutas para Movements
            elif endpoint.startswith("/app/movements"):
                await self.handleMovementRequests(endpoint, method, payload, websocket, requestId)
            # Rutas para Positions
            elif endpoint.startswith("/app/positions"):
                await self.handlePositionRequests(endpoint, method, payload, websocket, requestId)
            # Rutas para Video Control
            elif endpoint.startswith("/app/video"):
                await self.handleVideoRequests(endpoint, method, websocket, requestId)
            else:
                await self.sendErrorResponse(websocket, 'Invalid endpoint', requestId)

    async def handleButtonRequests(self, endpoint, method, payload, websocket, requestId):
        if endpoint == "/app/buttons/create" and method == "POST":
            await self.buttonManager.createButton(payload, websocket, requestId)
        elif endpoint == "/app/buttons/update" and method == "POST":
            await self.buttonManager.updateButtonById(payload, websocket, requestId)
        elif endpoint == "/app/buttons/delete" and method == "POST":
            await self.buttonManager.deleteButton(websocket, requestId)
        elif endpoint == "/app/buttons/get" and method == "GET":
            await self.buttonManager.getButtonById(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/buttons/getAll" and method == "GET":
            await self.buttonManager.getAllButtons(websocket, requestId)
        else:
            await self.sendErrorResponse(websocket, 'Invalid button request', requestId)

    async def handleServoRequests(self, endpoint, method, payload, websocket, requestId):
        if endpoint == "/app/servos/create" and method == "POST":
            await self.servoManager.createServo(payload, websocket, requestId)
        elif endpoint == "/app/servos/update" and method == "POST":
            await self.servoManager.updateServoById(payload, websocket, requestId)
        elif endpoint == "/app/servos/delete" and method == "POST":
            await self.servoManager.deleteServo(websocket, requestId)
        elif endpoint == "/app/servos/get" and method == "GET":
            await self.servoManager.getServoById(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/servos/getAll" and method == "GET":
            await self.servoManager.getAllServos(websocket, requestId)
        elif endpoint == "/app/servos/savePosition" and method == "POST":
            await self.servoManager.savePosition(websocket, requestId)
        else:
            await self.sendErrorResponse(websocket, 'Invalid servo request', requestId)

    async def handleMovementRequests(self, endpoint, method, payload, websocket, requestId):
        if endpoint == "/app/movements/create" and method == "POST":
            await self.movementService.createMovement(payload, websocket, requestId)
        elif endpoint == "/app/movements/update" and method == "POST":
            await self.movementService.updateMovementById(payload, websocket, requestId)
        elif endpoint == "/app/movements/delete" and method == "POST":
            await self.movementService.deleteMovementById(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/movements/get" and method == "GET":
            await self.movementService.getMovementById(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/movements/getAll" and method == "GET":
            await self.movementService.getAllMovements(websocket, requestId)
        else:
            await self.sendErrorResponse(websocket, 'Invalid movement request', requestId)

    async def handlePositionRequests(self, endpoint, method, payload, websocket, requestId):
        if endpoint == "/app/positions/create" and method == "POST":
            await self.positionService.createPosition(payload, websocket, requestId)
        elif endpoint == "/app/positions/update" and method == "POST":
            await self.positionService.updatePositionById(payload, websocket, requestId)
        elif endpoint == "/app/positions/delete" and method == "POST":
            await self.positionService.deletePositionById(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/positions/get" and method == "GET":
            await self.positionService.getPositionById(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/positions/getAll" and method == "GET":
            await self.positionService.getAllPositions(websocket, requestId)
        elif endpoint == "/app/positions/getByMovementId" and method == "GET":
            await self.positionService.getPositionsByMovementId(payload.get('movement_id'), websocket, requestId)
        elif endpoint == "/app/positions/moveUp" and method == "POST":
            await self.positionService.movePositionUp(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/positions/moveDown" and method == "POST":
            await self.positionService.movePositionDown(payload.get('id'), websocket, requestId)
        elif endpoint == "/app/positions/moveToInitial" and method == "POST":
            await self.positionService.moveToInitialPosition(websocket, requestId)
        elif endpoint == "/app/positions/executeMovement" and method == "POST":
            await self.positionService.executeMovement(payload.get('movement_id'), websocket, requestId)
        else:
            await self.sendErrorResponse(websocket, 'Invalid position request', requestId)

    async def handleVideoRequests(self, endpoint, method, websocket, requestId):
        if endpoint == "/app/video/start" and method == "POST":
            await self.videoControl.startVideoStream()
        elif endpoint == "/app/video/stop" and method == "POST":
            self.videoControl.stopVideoStream()
        else:
            await self.sendErrorResponse(websocket, 'Invalid video request', requestId)

    async def sendErrorResponse(self, websocket, errorMessage, requestId):
        response = {
            'request_id': requestId,
            'error': errorMessage
        }
        await websocket.send(json.dumps(response))
