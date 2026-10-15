import os
import httpx
from typing import Dict, Any, Tuple, Optional
from app import database as db

from app.config import settings

def get_credentials(custom_token: Optional[str] = None, custom_urn: Optional[str] = None) -> Tuple[str, str]:
    token = (custom_token and custom_token.strip()) or db.get_setting("linkedin_access_token", "") or (settings.linkedin_access_token or "")
    urn = (custom_urn and custom_urn.strip()) or db.get_setting("linkedin_person_urn", "") or (settings.linkedin_person_urn or "")
    return token.strip(), urn.strip()

async def verify_linkedin_token(token_input: Optional[str] = None) -> Dict[str, Any]:
    token = token_input.strip() if token_input else get_credentials()[0]
    if not token:
        raise ValueError("LinkedIn Access Token was not provided.")

    async with httpx.AsyncClient(timeout=20.0) as client:
        # Step 1: Try OpenID /v2/userinfo
        try:
            res = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if res.status_code == 200:
                user_data = res.json()
                person_urn = f"urn:li:person:{user_data['sub']}" if "sub" in user_data else ""
                name = user_data.get("name") or f"{user_data.get('given_name', '')} {user_data.get('family_name', '')}".strip() or "LinkedIn User"
                picture = user_data.get("picture", "")

                if person_urn:
                    db.set_setting("linkedin_person_urn", person_urn)
                if name:
                    db.set_setting("user_name", name)
                if picture:
                    db.set_setting("user_avatar_url", picture)
                db.set_setting("linkedin_access_token", token)

                return {
                    "valid": True,
                    "name": name,
                    "email": user_data.get("email"),
                    "person_urn": person_urn,
                    "picture": picture
                }
        except Exception as e:
            print(f"[LinkedIn] OpenID check warning: {e}")

        # Step 2: Fallback to /v2/me
        try:
            me_res = await client.get(
                "https://api.linkedin.com/v2/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if me_res.status_code == 200:
                me_data = me_res.json()
                person_urn = f"urn:li:person:{me_data['id']}" if "id" in me_data else ""
                name = f"{me_data.get('localizedFirstName', '')} {me_data.get('localizedLastName', '')}".strip() or "LinkedIn User"

                if person_urn:
                    db.set_setting("linkedin_person_urn", person_urn)
                if name:
                    db.set_setting("user_name", name)
                db.set_setting("linkedin_access_token", token)

                return {
                    "valid": True,
                    "name": name,
                    "person_urn": person_urn
                }
            else:
                raise Exception(f"Token validation failed ({me_res.status_code}): {me_res.text}")
        except Exception as e:
            raise Exception(f"Error validating LinkedIn token: {str(e)}")

import mimetypes
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

async def get_image_bytes_and_type(image_url: str) -> Tuple[bytes, str]:
    if not image_url:
        raise ValueError("Image URL was not provided.")

    if image_url.startswith("/static/uploads/"):
        filename = image_url.replace("/static/uploads/", "").strip("/")
        local_path = settings.uploads_dir / filename
        if not local_path.exists():
            raise FileNotFoundError(f"Local image file not found: {filename}")
        data = local_path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(local_path))
        return data, content_type or "image/jpeg"

    if image_url.startswith("http://") or image_url.startswith("https://"):
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(image_url)
            if res.status_code != 200:
                raise Exception(f"Unable to download image from URL ({res.status_code})")
            content_type = res.headers.get("content-type") or mimetypes.guess_type(image_url)[0] or "image/jpeg"
            return res.content, content_type

    # Fallback to local path directly
    local_path = Path(image_url)
    if local_path.exists():
        data = local_path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(local_path))
        return data, content_type or "image/jpeg"

    raise ValueError(f"Unrecognized image source: {image_url}")

async def upload_image_to_linkedin(image_url: str, token: str, target_urn: str) -> Dict[str, str]:
    """
    Realiza o fluxo completo de upload de imagem para o LinkedIn:
    1. Obtém os bytes da imagem (local ou remoto).
    2. Registra o upload na API do LinkedIn.
    3. Faz o upload binário dos dados.
    4. Retorna os URNs da mídia para uso em /rest/posts ou /v2/ugcPosts.
    """
    image_bytes, content_type = await get_image_bytes_and_type(image_url)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Tentativa 1: API REST moderna (/rest/images?action=initializeUpload)
        try:
            init_res = await client.post(
                "https://api.linkedin.com/rest/images?action=initializeUpload",
                json={"initializeUploadRequest": {"owner": target_urn}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "LinkedIn-Version": "202401",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json"
                }
            )
            if init_res.status_code == 200:
                init_data = init_res.json().get("value", {})
                upload_url = init_data.get("uploadUrl")
                image_urn = init_data.get("image")

                if upload_url and image_urn:
                    put_res = await client.put(
                        upload_url,
                        content=image_bytes,
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": content_type
                        }
                    )
                    if put_res.status_code in [200, 201]:
                        return {"type": "rest", "urn": image_urn}
        except Exception as e:
            print(f"[LinkedIn] REST Images upload warning: {e}. Tentando UGC Assets API...")

        # Tentativa 2: API UGC Assets (/v2/assets?action=registerUpload)
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": target_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        reg_res = await client.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            json=register_payload,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
        )

        if reg_res.status_code not in [200, 201]:
            raise Exception(f"Falha ao registrar upload no LinkedIn ({reg_res.status_code}): {reg_res.text}")

        val = reg_res.json().get("value", {})
        asset_urn = val.get("asset")
        mech = val.get("uploadMechanism", {}).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
        upload_url = mech.get("uploadUrl")

        if not upload_url or not asset_urn:
            raise Exception("LinkedIn não retornou a URL de upload de mídia.")

        put_res = await client.put(
            upload_url,
            content=image_bytes,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": content_type
            }
        )

        if put_res.status_code not in [200, 201]:
            raise Exception(f"Falha ao enviar binário da imagem para o LinkedIn ({put_res.status_code})")

        return {"type": "ugc", "urn": asset_urn}

async def publish_to_linkedin(
    content: str,
    image_url: Optional[str] = None,
    custom_token: Optional[str] = None,
    custom_urn: Optional[str] = None
) -> Dict[str, Any]:
    token, urn = get_credentials(custom_token, custom_urn)

    if not token:
        raise ValueError("Token de Acesso do LinkedIn não configurado. Por favor, adicione seu token na aba Configurações.")

    target_urn = urn
    if not target_urn:
        verified = await verify_linkedin_token(token)
        target_urn = verified.get("person_urn")

    if not target_urn:
        raise ValueError("URN do autor não encontrado. Certifique-se de que seu token tem permissão de leitura de perfil.")

    # Se houver imagem, realizar upload prévio
    media_asset = None
    if image_url:
        try:
            print(f"[LinkedIn] Fazendo upload da imagem para o post: {image_url}")
            media_asset = await upload_image_to_linkedin(image_url, token, target_urn)
            print(f"[LinkedIn] Imagem enviada com sucesso: {media_asset}")
        except Exception as e:
            print(f"[LinkedIn] Erro ao enviar imagem: {e}")
            raise Exception(f"Falha no upload da imagem anexada: {str(e)}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Tentativa 1: API REST moderna (/rest/posts)
        try:
            post_payload: Dict[str, Any] = {
                "author": target_urn,
                "commentary": content,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": []
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False
            }

            if media_asset and media_asset.get("urn"):
                post_payload["content"] = {
                    "media": {
                        "id": media_asset["urn"],
                        "altText": "Post media"
                    }
                }

            rest_res = await client.post(
                "https://api.linkedin.com/rest/posts",
                json=post_payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "LinkedIn-Version": "202401",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json"
                }
            )

            if rest_res.status_code == 201:
                post_urn = rest_res.headers.get("x-restli-id") or rest_res.headers.get("location") or "urn:li:share:published"
                return {
                    "success": True,
                    "post_urn": post_urn,
                    "api": "rest/posts",
                    "has_image": bool(media_asset)
                }

            print(f"[LinkedIn] REST API returned status {rest_res.status_code}: {rest_res.text}. Tentando UGC API...")
        except Exception as e:
            print(f"[LinkedIn] REST API call error: {e}. Tentando UGC API...")

        # Tentativa 2: API Clássica UGC Posts (/v2/ugcPosts)
        ugc_share_content: Dict[str, Any] = {
            "shareCommentary": {
                "text": content
            }
        }

        if media_asset and media_asset.get("urn"):
            ugc_share_content["shareMediaCategory"] = "IMAGE"
            ugc_share_content["media"] = [
                {
                    "status": "READY",
                    "description": {"text": "Post image"},
                    "media": media_asset["urn"],
                    "title": {"text": "Post image"}
                }
            ]
        else:
            ugc_share_content["shareMediaCategory"] = "NONE"

        ugc_payload = {
            "author": target_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": ugc_share_content
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        ugc_res = await client.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=ugc_payload,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
        )

        if ugc_res.status_code in [200, 201]:
            ugc_data = ugc_res.json()
            return {
                "success": True,
                "post_urn": ugc_data.get("id", "urn:li:ugcPost:published"),
                "api": "v2/ugcPosts",
                "has_image": bool(media_asset)
            }

        raise Exception(f"Publicação no LinkedIn falhou ({ugc_res.status_code}): {ugc_res.text}")
