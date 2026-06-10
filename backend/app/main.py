from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, users, skills, tools, permission_requests
from app.api.admin import users as admin_users, roles as admin_roles, skills as admin_skills, tools as admin_tools, approvals as admin_approvals, departments as admin_departments, audit as admin_audit
from app.api.v1 import verify


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI Skills & Tools Permission Management System",
        redirect_slashes=False,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Client API routes
    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(users.router, prefix="/api/users", tags=["Users"])
    app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
    app.include_router(tools.router, prefix="/api/tools", tags=["Tools"])
    app.include_router(permission_requests.router, prefix="/api/permission-requests", tags=["Permission Requests"])

    # Admin API routes
    app.include_router(admin_users.router, prefix="/api/admin/users", tags=["Admin - Users"])
    app.include_router(admin_roles.router, prefix="/api/admin/roles", tags=["Admin - Roles"])
    app.include_router(admin_skills.router, prefix="/api/admin/skills", tags=["Admin - Skills"])
    app.include_router(admin_tools.router, prefix="/api/admin/tools", tags=["Admin - Tools"])
    app.include_router(admin_approvals.router, prefix="/api/admin/approvals", tags=["Admin - Approvals"])
    app.include_router(admin_departments.router, prefix="/api/admin/departments", tags=["Admin - Departments"])
    app.include_router(admin_audit.router, prefix="/api/admin/audit-logs", tags=["Admin - Audit Logs"])

    # External verification API
    app.include_router(verify.router, prefix="/api/v1", tags=["Permission Verification"])

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()


def main():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
