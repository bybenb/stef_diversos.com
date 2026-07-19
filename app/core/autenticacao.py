from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import base64
import httpx
import os

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")


def obter_clerk_frontend_api(publishable_key: str) -> str:
    encoded = publishable_key.split("_", 2)[2]
    return base64.b64decode(encoded).decode("utf-8").rstrip("$")
security = HTTPBearer()

async def obter_usuario_admin(credentials = Depends(security)):
    """
    Middleware que valida o token JWT do Clerk usando a API REST oficial.
    Esta é a forma mais estável e não depende de SDKs em constante mudança.
    """
    token = credentials.credentials
    
    async with httpx.AsyncClient() as client:
        # A Clerk recomenda validar o token chamando a API de verificação
        response = await client.post(
            "https://api.clerk.com/v1/verify_token",
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
            json={"token": token}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        dados = response.json()
        
        # Retorna os dados do usuário
        return {
            "id": dados.get("sub"),
            "email": dados.get("email"),
            "nome": dados.get("name")
        }