import httpx
from typing import Optional
from app.config import settings


class FeishuService:
    """飞书开放平台API服务"""

    def __init__(self):
        self.base_url = settings.FEISHU_BASE_URL
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self._tenant_access_token: Optional[str] = None

    def get_auth_url(self, state: Optional[str] = None) -> str:
        """生成飞书OAuth2授权URL"""
        url = (
            f"https://open.feishu.cn/open-apis/authen/v1/authorize"
            f"?app_id={self.app_id}"
            f"&redirect_uri={settings.FEISHU_REDIRECT_URI}"
            f"&response_type=code"
            f"&state={state or ''}"
        )
        return url

    async def _get_tenant_access_token(self) -> str:
        """获取飞书tenant_access_token"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                },
            )
            data = resp.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to get tenant_access_token: {data.get('msg')}")
            self._tenant_access_token = data["tenant_access_token"]
            return self._tenant_access_token

    async def get_user_access_token(self, code: str) -> dict:
        """通过授权码获取用户access_token"""
        tenant_token = await self._get_tenant_access_token()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/authen/v1/oidc/access_token",
                headers={"Authorization": f"Bearer {tenant_token}"},
                json={
                    "grant_type": "authorization_code",
                    "code": code,
                },
            )
            data = resp.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to get user access token: {data.get('msg')}")
            return data["data"]

    async def get_user_info(self, user_access_token: str) -> dict:
        """获取飞书用户信息"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/authen/v1/user_info",
                headers={"Authorization": f"Bearer {user_access_token}"},
            )
            data = resp.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to get user info: {data.get('msg')}")
            return data["data"]

    async def get_department_list(self, parent_department_id: str = "0") -> list[dict]:
        """获取飞书部门列表"""
        tenant_token = await self._get_tenant_access_token()
        departments = []
        page_token = None

        async with httpx.AsyncClient() as client:
            while True:
                params = {
                    "parent_department_id": parent_department_id,
                    "fetch_child": False,
                    "page_size": 50,
                }
                if page_token:
                    params["page_token"] = page_token

                resp = await client.get(
                    f"{self.base_url}/contact/v3/departments",
                    headers={"Authorization": f"Bearer {tenant_token}"},
                    params=params,
                )
                data = resp.json()
                if data.get("code") != 0:
                    raise Exception(f"Failed to get departments: {data.get('msg')}")

                items = data.get("data", {}).get("items", [])
                departments.extend(items)

                page_token = data.get("data", {}).get("page_token")
                if not data.get("data", {}).get("has_more"):
                    break

        return departments

    async def get_department_detail(self, department_id: str) -> dict:
        """获取飞书部门详情"""
        tenant_token = await self._get_tenant_access_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/contact/v3/departments/{department_id}",
                headers={"Authorization": f"Bearer {tenant_token}"},
            )
            data = resp.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to get department detail: {data.get('msg')}")
            return data.get("data", {}).get("department", {})


feishu_service = FeishuService()
