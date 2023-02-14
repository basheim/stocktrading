from datetime import datetime


class SelectedPlant:
    plant_id: str
    start: datetime
    end: datetime

    @staticmethod
    def build(sql_data: {}):
        return SelectedPlant(
            sql_data["id"],
            sql_data["start"],
            sql_data["end"]
        )

    def __init__(self, plant_id: str, start: datetime, end: datetime):
        self.plant_id = plant_id
        self.start = start
        self.end = end

    def __repr__(self):
        return str({
            "id" : self.plant_id,
            "start": self.start,
            "end": self.end
        })
