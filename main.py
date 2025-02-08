import asyncio
from app.activity.service.migration import migrate_activities
from app.funding.service.migration import migrate_fundings

if __name__ == "__main__":
    # asyncio.run(migrate_activities())
    asyncio.run(migrate_fundings())