import json

class ResponseHandler:
    async def sendResponse(self, websocket, payload, requestId):
        response = {
            'request_id': requestId,
            'payload': payload
        }
        await websocket.send(json.dumps(response))

    async def sendErrorResponse(self, websocket, errorMessage, requestId):
        response = {
            'request_id': requestId,
            'error': errorMessage
        }
        await websocket.send(json.dumps(response))