import asyncio
from app.activity.service.migration import migrate_activities

if __name__ == "__main__":
    asyncio.run(migrate_activities())
