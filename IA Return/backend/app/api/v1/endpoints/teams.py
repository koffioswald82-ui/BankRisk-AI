from fastapi import APIRouter, HTTPException
from ....services.data_store import get_teams, get_engineers, get_ai_usage, get_sprint_metrics

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/")
async def list_teams():
    teams = get_teams()
    engineers = get_engineers()
    ai_usage = get_ai_usage()

    team_engineer_count = {}
    for e in engineers:
        team_engineer_count[e["team_id"]] = team_engineer_count.get(e["team_id"], 0) + 1

    import pandas as pd
    if ai_usage:
        ai_df = pd.DataFrame(ai_usage)
        team_cost = ai_df.groupby("team_id")["total_cost_usd"].sum().to_dict()
    else:
        team_cost = {}

    result = []
    for t in teams:
        result.append({
            **t,
            "engineer_count": team_engineer_count.get(t["id"], t["size"]),
            "total_ai_cost_usd": round(team_cost.get(t["id"], 0), 2),
        })

    return {"teams": result, "total": len(result)}


@router.get("/{team_id}/engineers")
async def get_team_engineers(team_id: str):
    engineers = [e for e in get_engineers() if e["team_id"] == team_id]
    if not engineers:
        raise HTTPException(status_code=404, detail="Team not found or has no engineers")
    return {"engineers": engineers, "total": len(engineers)}


@router.get("/{team_id}/sprints")
async def get_team_sprints(team_id: str):
    sprints = get_sprint_metrics(team_id=team_id)
    if not sprints:
        raise HTTPException(status_code=404, detail="No sprint data for this team")

    import pandas as pd
    df = pd.DataFrame(sprints)
    df["period_start"] = pd.to_datetime(df["period_start"])
    df = df.sort_values("period_start")
    return {"sprints": df.to_dict(orient="records"), "total": len(sprints)}
