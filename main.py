import asyncio
from database import Database

from services.button_manager import ButtonManager
from services.servo_manager import ServoManager
from services.movement_service import MovementService
from services.position_service import PositionService
from services.video_control_service import VideoControlService

from websocket_handler import WebSocketHandler
from main_loop import MainLoop
import websockets

async def startDataServer(buttonManager, servoManager, movementService, positionService, videoControlService):
    websocketHandler = WebSocketHandler(buttonManager, servoManager, movementService, positionService, videoControlService)
    startServer = websockets.serve(websocketHandler.handleMessage, '0.0.0.0', 8765, max_size=None)
    await startServer
    print("Servidor WebSocket de datos iniciado en el puerto 8765")
    await asyncio.Future()  # Run forever

async def startVideoServer(videoControlService):
    startServer = websockets.serve(videoControlService.register, '0.0.0.0', 8766, max_size=None)
    await startServer
    print("Servidor WebSocket de video iniciado en el puerto 8766")
    await asyncio.Future()  # Run forever

async def main():
    db = Database()
    buttonManager = ButtonManager()
    servoManager = ServoManager()
    movementService = MovementService(db)
    positionService = PositionService(db)
    videoControlService = VideoControlService()
    mainLoop = MainLoop(buttonManager, servoManager, movementService, positionService, videoControlService)
    
    # Iniciar los servidores WebSocket de manera asincrónica
    videoTask = asyncio.create_task(startVideoServer(videoControlService))
    dataTask = asyncio.create_task(startDataServer(buttonManager, servoManager, movementService, positionService, videoControlService))
    mainLoop = asyncio.create_task(mainLoop.run())

    await asyncio.gather(videoTask, dataTask, mainLoop)

if __name__ == "__main__":
    asyncio.run(main())