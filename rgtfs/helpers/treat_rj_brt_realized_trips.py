import pandas as pd
from datetime import datetime

from rgtfs.tables import realized_trips_cols

cols = {
    "Data": "date",
    "Trajeto": "traject",
    "Veiculo Real": "vehicle_id",
    "Partida Real": "departure_time",
    "Chegada Real": "arrival_time",
    "Tempo Viagem Real": "trip_time",
    "Veiculo Planejado": "planned_vehicle_id",
    "Partida Planejada": "planned_departure_time",
    "Chegada Planejada": "planned_arrival_time",
    "KM Executado": "trip_distance",
}

# Keys: BRT last station
# Values: GTFS trip_headsign
stations = {
    " ALVORADA -  SEMI EXPRESSO": "TERMINAL ALVORADA",
    " JARDIM OCEÃ‚NICO (PARADOR)": "JARDIM OCEÂNICO",
    " MADUREIRA ( PARADOR ) - VOLTA": "MADUREIRA MANACEIA",
    " MATO ALTO ( EXPRESSO )": "MATO ALTO",
    "27 - MATO ALTO - SALVADOR ALLENDE (PARADOR)": "SALVADOR ALLENDE",
    "ALVORADA": "TERMINAL ALVORADA",
    "ALVORADA ( EXPRESSO )": "TERMINAL ALVORADA",
    "ALVORADA ( PARADOR )- IDA": "TERMINAL ALVORADA",
    "ALVORADA ( SEMI DIRETO )": "TERMINAL ALVORADA",
    "ALVORADA (PARADOR)": "TERMINAL ALVORADA",
    "CAMPO GRANDE": "CAMPO GRANDE",
    "CURICICA (PARADOR)": None,
    "FUNDÃƑO": "FUNDÃO",
    "GALEAO (PARADOR)": "GALEÃO",
    "GALEÃƑO (PARADOR)": "GALEÃO",
    "J. OCEÃ‚NICO (PARADOR)": "JARDIM OCEÂNICO",
    "J.OCEÃ‚NICO (PARADOR)": "JARDIM OCEÂNICO",
    "JARDIM OCEÃ‚NICO": "JARDIM OCEÂNICO",
    "JARDIM OCEÃ‚NICO ( EXPRESSO )": "JARDIM OCEÂNICO",
    "JD. OCEANICO (PARADOR)": "JARDIM OCEÂNICO",
    "MADUREIRA": "MADUREIRA MANACEIA",
    "MADUREIRA ( EXPRESSO )": "MADUREIRA MANACEIA",
    "MADUREIRA (PARADOR)": "MADUREIRA MANACEIA",
    "MATO ALTO (PARADOR)": "MATO ALTO",
    "MATO ALTO -  SEMI EXPRESSO": "MATO ALTO",
    "PENHA ( EXPRESSO )": "PENHA",
    "PINGO D'AGUA ( EXPRESSO )": "PINGO D'ÁGUA",
    "PINGO D'ÃGUA": "PINGO D'ÁGUA",
    "RECREIO (EXPRESSO)": "RECREIO SHOPPING",
    "RECREIO SHOPPING": "RECREIO SHOPPING",
    "RECREIO SHOPPING ( EXPRESSO )": "RECREIO SHOPPING",
    "SALVADOR ALLENDE": "SALVADOR ALLENDE",
    "SALVADOR ALLENDE ( EXPRESSO )": "SALVADOR ALLENDE",
    "SALVADOR ALLENDE (PARADOR)": "SALVADOR ALLENDE",
    "SANTA CRUZ": "SANTA CRUZ",
    "SANTA CRUZ ( EXPRESSO )": "SANTA CRUZ",
    "SANTA EFIGÃŠNIA": None,
    "SULACAP ( EXPRESSO )": "SULACAP",
    "SULACAP (PARADOR)": "SULACAP",
    "T. RECREIO (PARADOR)": "RECREIO SHOPPING",
    "TANQUE": None,
    "TERMINAL ALVORADA": "TERMINAL ALVORADA",
    "TERMINAL MADUREIRA (EXPRESSO)": "TERMINAL MADUREIRA",
    "TERMINAL OLIMPICO (PARADOR)": "TERMINAL CENTRO OLÍMPICO",
    "VICENTE DE CARVALHO ( SEMI DIRETO )": "VICENTE DE CARVALHO",
    "VILA MILITAR": "VILA MILITAR",
    "VILA MILITAR (PARADOR)": "VILA MILITAR",
}


cols = {
    "Data": "date",
    "Trajeto": "trip_short_name",
    "Veiculo Real": "vehicle_id",
    "Partida Real": "departure_time",
    "Chegada Real": "arrival_time",
    "Tempo Viagem": "elapsed_time",
    "KM Executado": "distance",
    "Vel. Media Km": "average_speed",
    "Status da Viagem": "trajectory_type",
}

trajectory_type_map = {
    1: "complete_trip",
    2: "not_complete_trip",
    3: "complete_trip",
    6: "not_complete_trip",
}


def translate(raw_path):
    """Reads official Rio de Janeiro BRT realized trips file
    and converts to standarized realized trips.

    TODO:
    - get trip_id, maybe from GTFS?
    - get departure_id and arrival_id, also from GTFS?

    Parameters
    ----------
    raw_path : str
        where raw data is locates as .xlsx
    """
    original_brt = pd.read_csv(
        raw_path,
        encoding="utf8",
        sep=";",
        na_values=["-"],
        decimal=",",
        parse_dates=["Data"],
        infer_datetime_format=False,
        date_parser=lambda x: datetime.strptime(x, "%d/%m/%Y"),
    )

    # filter columns
    original_brt = original_brt[list(cols.keys())].rename(columns=cols)

    # drop not executed
    original_brt = original_brt.dropna(
        subset=["vehicle_id", "departure_time", "arrival_time"]
    )
    # parse datetimes
    original_brt["departure_datetime"] = original_brt.apply(
        lambda x: pd.Timestamp(str(x["date"].date()) + " " + str(x["departure_time"])),
        1,
    )
    original_brt["arrival_datetime"] = original_brt.apply(
        lambda x: pd.Timestamp(str(x["date"].date()) + " " + str(x["arrival_time"])), 1
    )

    # map trajectory type
    original_brt["trajectory_type"] = original_brt["trajectory_type"].replace(
        trajectory_type_map
    )

    # creates missing columns
    for c in realized_trips_cols:
        if c not in original_brt.columns:
            original_brt[c] = None

    # vehicle id to str
    # original_brt["vehicle_id"] = (
    #     original_brt["vehicle_id"].apply(lambda x: x.replace"*", "").astype(int).astype(str)
    # )

    return original_brt[realized_trips_cols]
