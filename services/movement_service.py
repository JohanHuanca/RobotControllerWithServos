from response_handler import ResponseHandler
from repositories.movement_repository import MovementRepository
from dataclasses import asdict
import sqlite3

class MovementService(ResponseHandler):
    def __init__(self, db):
        self.repository = MovementRepository(db)

    async def createMovement(self, data, websocket, requestId):
        name = data.get('name')
        
        if not name:
            await self.sendErrorResponse(websocket, {"message": "Movement name is required"}, requestId)
            return

        if self.repository.findByName(name):
            await self.sendErrorResponse(websocket, {"message": "Movement with this name already exists"}, requestId)
            return

        movementId = self.repository.save(name)
        movement = self.repository.findById(movementId)
        await self.sendResponse(websocket, asdict(movement), requestId)

    async def updateMovementById(self, data, websocket, requestId):
        movementId = data.get('id')
        name = data.get('name')
        if not movementId or not isinstance(movementId, int):
            await self.sendErrorResponse(websocket, {"message": "Movement ID is required and must be an integer"}, requestId)
            return

        if not name:
            await self.sendErrorResponse(websocket, {"message": "Movement name is required"}, requestId)
            return

        if not self.repository.findById(movementId):
            await self.sendErrorResponse(websocket, {"message": "Movement ID does not exist"}, requestId)
            return

        existingMovement = self.repository.findByName(name)
        if existingMovement and existingMovement.id != movementId:
            await self.sendErrorResponse(websocket, {"message": "Movement with this name already exists"}, requestId)
            return

        self.repository.updateById(movementId, name)
        movement = self.repository.findById(movementId)
        await self.sendResponse(websocket, asdict(movement), requestId)

    async def deleteMovementById(self, movementId, websocket, requestId):
        if not movementId or not isinstance(movementId, int):
            await self.sendErrorResponse(websocket, {"message": "Movement ID is required and must be an integer"}, requestId)
            return

        if not self.repository.findById(movementId):
            await self.sendErrorResponse(websocket, {"message": "Movement ID does not exist"}, requestId)
            return

        self.repository.deleteById(movementId)
        await self.sendResponse(websocket, {'id': movementId}, requestId)

    async def getMovementById(self, movementId, websocket, requestId):
        if not movementId or not isinstance(movementId, int):
            await self.sendErrorResponse(websocket, {"message": "Movement ID is required and must be an integer"}, requestId)
            return
        
        movement = self.repository.findById(movementId)
        if movement:
            await self.sendResponse(websocket, asdict(movement), requestId)
        else:
            await self.sendErrorResponse(websocket, {"message": "Movement not found"}, requestId)

    async def getAllMovements(self, websocket, requestId):
        movements = self.repository.findAll()
        payload = {
            "total_items": len(movements),
            "content": [asdict(movement) for movement in movements]
        }
        await self.sendResponse(websocket, payload, requestId)
