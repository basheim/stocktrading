from lib.clients.backend_manager import get_last_plant_date
from lib.clients.rds_manager import get_selected_plants, update_selected_plant
from datetime import datetime, timedelta


def refresh_plants():
    if __should_refresh():
        plants = get_selected_plants()
        now = datetime.now() - timedelta(days=1)
        start = datetime.combine(now, datetime.min.time())
        end = start + timedelta(days=1)
        for plant in plants:
            update_selected_plant(plant.plant_id, start, end)
            start = end
            end = end + timedelta(days=1)


def __should_refresh():
    d = datetime.fromtimestamp(get_last_plant_date()["latestDate"])
    now = datetime.now() + timedelta(days=1)
    return d < now