import pandas as pd

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
    " ALVORADA -  SEMI EXPRESSO": "ALVORADA",
    " JARDIM OCEÃ‚NICO (PARADOR)": "JARDIM OCEÂNICO",
    " MADUREIRA ( PARADOR ) - VOLTA": "MADUREIRA MANACEIA",
    " MATO ALTO ( EXPRESSO )": "MATO ALTO",
    "27 - MATO ALTO - SALVADOR ALLENDE (PARADOR)": "SALVADOR ALLENDE",
    "ALVORADA": "ALVORADA",
    "ALVORADA ( EXPRESSO )": "ALVORADA",
    "ALVORADA ( PARADOR )- IDA": "ALVORADA",
    "ALVORADA ( SEMI DIRETO )": "ALVORADA",
    "ALVORADA (PARADOR)": "ALVORADA",
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


def treat_brt_realized_trips(raw_path, brt_gtfs_path):
    """Reads official BRT realized trips file and converts to standarized realized trips.

    Station names may change, so make sure to update them.

    Parameters
    ----------
    raw_path : str
        where raw data is locates as .xlsx
    brt_gtfs_path : str
        where to safe the GTFS
    """
    original_brt = pd.read_excel(raw_path, engine="openpyxl", header=1).drop(
        "Unnamed: 0", 1
    )

    original_brt = original_brt.rename(columns=cols).dropna(how="all")

    original_brt["route_id"] = original_brt["traject"].apply(lambda x: x.split(" ")[0])
    original_brt["trip_headsign"] = original_brt["traject"].apply(
        lambda x: stations[x.upper().split("X ")[-1]]
    )
    original_brt["service_id"] = "U"
    original_brt["departure_datetime"] = original_brt.apply(
        lambda x: pd.Timestamp(str(x["date"].date()) + " " + str(x["departure_time"])),
        1,
    )
    original_brt["arrival_datetime"] = original_brt.apply(
        lambda x: pd.Timestamp(str(x["date"].date()) + " " + str(x["arrival_time"])), 1
    )

    original_brt = original_brt.merge(
        gtfs.trips[["route_id", "trip_headsign", "direction_id"]],
        on=["route_id", "trip_headsign"],
    )

    original_brt["trip_id"] = original_brt.apply(
        lambda x: "_".join(
            map(str, [x["route_id"], x["direction_id"], x["service_id"]])
        ),
        1,
    )

    return original_brt[
        [
            "vehicle_id",
            "route_id",
            "direction_id",
            "service_id",
            "trip_id",
            "departure_datetime",
            "arrival_datetime",
        ]
    ]
