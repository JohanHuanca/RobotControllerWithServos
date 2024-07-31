import asyncio
import subprocess
import websockets

class VideoControlService:
    def __init__(self):
        self.clients = set()
        self.process = None
        self.streamingTask = None

    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    async def captureAndStream(self):
        if self.process is None:
            self.process = subprocess.Popen(
                ['libcamera-vid', '--inline', '-t', '0', '--framerate', '20', 
                '--width', '640', '--height', '480', '--codec', 'mjpeg', '-o', '-'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

        try:
            while True:
                data = self.process.stdout.read(12000)
                if not data:
                    break
                if self.clients:
                    await asyncio.gather(*(client.send(data) for client in self.clients))
                await asyncio.sleep(1 / 20)  # Ajusta la tasa de frames aquí
        except websockets.ConnectionClosed:
            print("Conexión cerrada")
        finally:
            self.stopVideoStream()

    async def startVideoStream(self):
        if self.process:
            print("La captura de video ya está en funcionamiento.")
            return
        print("Iniciando captura de video")
        self.streamingTask = asyncio.create_task(self.captureAndStream())

    def stopVideoStream(self):
        if not self.process:
            print("La captura de video ya está detenida.")
            return
        print("Deteniendo la transmisión de video")
        self.process.terminate()
        self.process = None
        if self.streamingTask:
            self.streamingTask.cancel()
            self.streamingTask = None
