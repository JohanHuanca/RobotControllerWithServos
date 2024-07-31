Crear y activar un entorno virtual:

bash
Copiar código
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instalar dependencias:

bash
Copiar código
pip install -r requirements.txt
Actualizar requirements.txt después de agregar nuevas dependencias:

bash
Copiar código
pip install new-package
pip freeze > requirements.txt