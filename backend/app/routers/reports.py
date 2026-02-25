"""Report generation & download endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.report import Report
from app.schemas import ReportCreate, ReportResponse
from app.services.report_service import generate_incident_report, generate_pdf_bytes
from app.utils.security import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=list[ReportResponse])
async def list_reports(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).order_by(desc(Report.created_at)))
    reports = result.scalars().all()
    return [ReportResponse.model_validate(r) for r in reports]


@router.post("/generate", response_model=ReportResponse)
async def create_report(
    data: ReportCreate,
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    if not data.incident_id:
        raise HTTPException(status_code=400, detail="incident_id is required for incident reports")

    try:
        report = await generate_incident_report(
            db=db,
            incident_id=data.incident_id,
            title=data.title,
            generated_by=user.id,
        )
        return ReportResponse.model_validate(report)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.model_validate(report)


@router.get("/{report_id}/pdf")
async def download_pdf(report_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    pdf_bytes = generate_pdf_bytes(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="SOCForge_Report_{report_id}.pdf"'},
    )
