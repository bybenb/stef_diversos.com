from fastapi import Request, HTTPException, status

# Lista de e-mails e senha autorizados
ADMIN_EMAILS = {
    "itsbenyreis@gmail.com",
    "benybkiamvu@gmail.com",
    "estefanianeto20@mail"
}

async def obter_usuario_admin(request: Request):
    """
    Middleware que verifica se o usuário está logado via sessão.
    """
    email = request.session.get("admin_user")
    
    if not email or email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso não autorizado. Faça login com seu e-mail autorizado."
        )
    
    return {"email": email}