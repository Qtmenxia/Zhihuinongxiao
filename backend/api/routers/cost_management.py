"""
成本管理API路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from typing import Optional
from datetime import datetime, timedelta, date

from backend.api.dependencies import get_session, get_current_farmer
from backend.models.farmer import Farmer
from backend.models.cost_record import CostRecord
from backend.api.schemas.cost_record import (
    CostRecordCreate,
    CostRecordUpdate,
    CostRecordResponse,
    CostOverviewResponse,
    CostTrendResponse,
    CostTrendData
)

router = APIRouter()


@router.get(
    "/overview",
    response_model=CostOverviewResponse,
    summary="获取成本概览",
    description="获取成本概览统计数据"
)
async def get_cost_overview(
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """获取成本概览"""
    
    # 计算本月和上月的时间范围
    now = datetime.now()
    current_month_start = date(now.year, now.month, 1)
    
    if now.month == 1:
        last_month_start = date(now.year - 1, 12, 1)
        last_month_end = date(now.year - 1, 12, 31)
    else:
        last_month_start = date(now.year, now.month - 1, 1)
        # 本月第一天的前一天就是上月最后一天
        last_month_end = current_month_start - timedelta(days=1)
    
    # 本月总成本
    current_total_result = await db.execute(
        select(func.sum(CostRecord.amount)).where(
            and_(
                CostRecord.farmer_id == current_farmer.id,
                CostRecord.date >= current_month_start
            )
        )
    )
    current_total = current_total_result.scalar() or 0.0
    
    # 上月总成本
    last_total_result = await db.execute(
        select(func.sum(CostRecord.amount)).where(
            and_(
                CostRecord.farmer_id == current_farmer.id,
                CostRecord.date >= last_month_start,
                CostRecord.date <= last_month_end
            )
        )
    )
    last_total = last_total_result.scalar() or 0.0
    
    # 计算环比
    if last_total > 0:
        total_trend = round((current_total - last_total) / last_total * 100, 1)
    else:
        total_trend = 0.0
    
    # 按类型统计本月成本
    type_stats = {}
    for cost_type in ['material', 'labor', 'logistics', 'packaging', 'other']:
        result = await db.execute(
            select(func.sum(CostRecord.amount)).where(
                and_(
                    CostRecord.farmer_id == current_farmer.id,
                    CostRecord.type == cost_type,
                    CostRecord.date >= current_month_start
                )
            )
        )
        type_stats[cost_type] = result.scalar() or 0.0
    
    # 计算占比
    material_percent = round(type_stats['material'] / current_total * 100, 1) if current_total > 0 else 0
    labor_percent = round(type_stats['labor'] / current_total * 100, 1) if current_total > 0 else 0
    other_cost = type_stats['logistics'] + type_stats['packaging'] + type_stats['other']
    other_percent = round(other_cost / current_total * 100, 1) if current_total > 0 else 0
    
    return CostOverviewResponse(
        total_cost=current_total,
        total_trend=total_trend,
        material_cost=type_stats['material'],
        material_percent=material_percent,
        labor_cost=type_stats['labor'],
        labor_percent=labor_percent,
        other_cost=other_cost,
        other_percent=other_percent
    )


@router.get(
    "/trend",
    response_model=CostTrendResponse,
    summary="获取成本趋势",
    description="获取指定周期的成本趋势数据"
)
async def get_cost_trend(
    period: str = Query("month", description="统计周期: month/quarter/year"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """获取成本趋势"""
    
    now = datetime.now()
    
    if period == "month":
        # 本月每天的数据
        start_date = date(now.year, now.month, 1)
        end_date = now.date()
        days = (end_date - start_date).days + 1
        
        trend_data = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # 查询当天各类型成本
            daily_costs = {}
            for cost_type in ['material', 'labor', 'logistics', 'packaging', 'other']:
                result = await db.execute(
                    select(func.sum(CostRecord.amount)).where(
                        and_(
                            CostRecord.farmer_id == current_farmer.id,
                            CostRecord.type == cost_type,
                            CostRecord.date == current_date
                        )
                    )
                )
                daily_costs[cost_type] = result.scalar() or 0.0
            
            total = sum(daily_costs.values())
            trend_data.append(CostTrendData(
                date=f"{i + 1}日",
                material=daily_costs['material'],
                labor=daily_costs['labor'],
                logistics=daily_costs['logistics'],
                packaging=daily_costs['packaging'],
                other=daily_costs['other'],
                total=total
            ))
    
    elif period == "quarter":
        # 本季度每周的数据
        quarter = (now.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start_date = date(now.year, start_month, 1)
        end_date = now.date()
        
        trend_data = []
        current_date = start_date
        week_num = 1
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            # 查询本周各类型成本
            weekly_costs = {}
            for cost_type in ['material', 'labor', 'logistics', 'packaging', 'other']:
                result = await db.execute(
                    select(func.sum(CostRecord.amount)).where(
                        and_(
                            CostRecord.farmer_id == current_farmer.id,
                            CostRecord.type == cost_type,
                            CostRecord.date >= current_date,
                            CostRecord.date <= week_end
                        )
                    )
                )
                weekly_costs[cost_type] = result.scalar() or 0.0
            
            total = sum(weekly_costs.values())
            trend_data.append(CostTrendData(
                date=f"第{week_num}周",
                material=weekly_costs['material'],
                labor=weekly_costs['labor'],
                logistics=weekly_costs['logistics'],
                packaging=weekly_costs['packaging'],
                other=weekly_costs['other'],
                total=total
            ))
            
            current_date = week_end + timedelta(days=1)
            week_num += 1
    
    else:  # year
        # 本年度每月的数据
        trend_data = []
        for month in range(1, now.month + 1):
            # 查询本月各类型成本
            monthly_costs = {}
            for cost_type in ['material', 'labor', 'logistics', 'packaging', 'other']:
                result = await db.execute(
                    select(func.sum(CostRecord.amount)).where(
                        and_(
                            CostRecord.farmer_id == current_farmer.id,
                            CostRecord.type == cost_type,
                            extract('year', CostRecord.date) == now.year,
                            extract('month', CostRecord.date) == month
                        )
                    )
                )
                monthly_costs[cost_type] = result.scalar() or 0.0
            
            total = sum(monthly_costs.values())
            trend_data.append(CostTrendData(
                date=f"{month}月",
                material=monthly_costs['material'],
                labor=monthly_costs['labor'],
                logistics=monthly_costs['logistics'],
                packaging=monthly_costs['packaging'],
                other=monthly_costs['other'],
                total=total
            ))
    
    return CostTrendResponse(period=period, data=trend_data)


@router.get(
    "/records",
    response_model=dict,
    summary="获取成本记录列表",
    description="分页获取成本记录列表"
)
async def get_cost_records(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    type: Optional[str] = Query(None, description="成本类型筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """获取成本记录列表"""
    
    # 构建查询条件
    conditions = [CostRecord.farmer_id == current_farmer.id]
    
    if type:
        conditions.append(CostRecord.type == type)
    if start_date:
        conditions.append(CostRecord.date >= start_date)
    if end_date:
        conditions.append(CostRecord.date <= end_date)
    
    # 查询总数
    count_result = await db.execute(
        select(func.count()).select_from(CostRecord).where(and_(*conditions))
    )
    total = count_result.scalar()
    
    # 查询数据
    result = await db.execute(
        select(CostRecord)
        .where(and_(*conditions))
        .order_by(CostRecord.date.desc(), CostRecord.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    records = result.scalars().all()
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "records": [CostRecordResponse.model_validate(record) for record in records]
    }


@router.post(
    "/records",
    response_model=CostRecordResponse,
    summary="创建成本记录",
    description="创建新的成本记录"
)
async def create_cost_record(
    record: CostRecordCreate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """创建成本记录"""
    
    cost_record = CostRecord(
        farmer_id=current_farmer.id,
        **record.model_dump()
    )
    
    db.add(cost_record)
    await db.commit()
    await db.refresh(cost_record)
    
    return CostRecordResponse.model_validate(cost_record)


@router.put(
    "/records/{record_id}",
    response_model=CostRecordResponse,
    summary="更新成本记录",
    description="更新指定的成本记录"
)
async def update_cost_record(
    record_id: int,
    record_update: CostRecordUpdate,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """更新成本记录"""
    
    # 查询记录
    result = await db.execute(
        select(CostRecord).where(
            and_(
                CostRecord.id == record_id,
                CostRecord.farmer_id == current_farmer.id
            )
        )
    )
    cost_record = result.scalar_one_or_none()
    
    if not cost_record:
        raise HTTPException(status_code=404, detail="成本记录不存在")
    
    # 更新字段
    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cost_record, field, value)
    
    await db.commit()
    await db.refresh(cost_record)
    
    return CostRecordResponse.model_validate(cost_record)


@router.delete(
    "/records/{record_id}",
    summary="删除成本记录",
    description="删除指定的成本记录"
)
async def delete_cost_record(
    record_id: int,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """删除成本记录"""
    
    # 查询记录
    result = await db.execute(
        select(CostRecord).where(
            and_(
                CostRecord.id == record_id,
                CostRecord.farmer_id == current_farmer.id
            )
        )
    )
    cost_record = result.scalar_one_or_none()
    
    if not cost_record:
        raise HTTPException(status_code=404, detail="成本记录不存在")
    
    await db.delete(cost_record)
    await db.commit()
    
    return {"message": "删除成功"}

