GIOVANNI_BASE_URL = "https://giovanni.gsfc.nasa.gov/giovanni/"

VARIABLE_CATALOG = {
    "AIRS3STM_006_SurfAirTemp_A": {
        "name": "daytime surface air temperature",
        "topic": "Temperature",
        "display_units": "°C",
        "scale_factor": 1.0,
        "offset": -273.15,
        "definition": "Air temperature near the ground, measured by the AIRS infrared sounder.",
    },
    "M2TMNXOCN_5_12_4_QV10M": {
        "name": "near-surface humidity",
        "topic": "Atmosphere moisture",
        "display_units": "g/kg",
        "scale_factor": 1000.0,
        "offset": 0.0,
        "definition": "Grams of water vapor per kilogram of air, 10 m above the surface (MERRA-2 model).",
    },
    "M2TMNXSLV_5_12_4_TO3": {
        "name": "total column ozone",
        "topic": "Atmosphere composition",
        "display_units": "DU",
        "scale_factor": 1.0,
        "offset": 0.0,
        "definition": "Total ozone in the air column above a point, in Dobson Units (MERRA-2 model).",
    },
    "GLDAS_NOAH025_M_2_1_Rainf_tavg": {
        "name": "rainfall rate",
        "topic": "Water",
        "display_units": "mm/day",
        "scale_factor": 86400.0,
        "offset": 0.0,
        "definition": "Average rainfall rate, in millimeters of water per day (GLDAS land model).",
    },
    "GLDAS_NOAH025_M_2_1_SoilMoi10_40cm_inst": {
        "name": "soil moisture (10–40 cm depth)",
        "topic": "Land",
        "display_units": "kg/m²",
        "scale_factor": 1.0,
        "offset": 0.0,
        "definition": "Water stored in the soil layer 10–40 cm underground; 1 kg/m² equals 1 mm of water (GLDAS).",
    },
    "FLDAS_NOAH01_C_GL_M_001_Wind_f_tavg": {
        "name": "near-surface wind speed",
        "topic": "Wind",
        "display_units": "m/s",
        "scale_factor": 1.0,
        "offset": 0.0,
        "definition": "Average wind speed near the ground (FLDAS land model).",
    },
}

DEMO_FILE_KEYS = {  # filename label -> catalog key
    #"temp": "AIRS3STM_006_SurfAirTemp_A",
    "humidity": "M2TMNXOCN_5_12_4_QV10M",
    "ozone": "M2TMNXSLV_5_12_4_TO3",
    "rain": "GLDAS_NOAH025_M_2_1_Rainf_tavg",
    "soil": "GLDAS_NOAH025_M_2_1_SoilMoi10_40cm_inst",
   #"wind": "FLDAS_NOAH01_C_GL_M_001_Wind_f_tavg",
}

TOPIC_QUESTIONS = {
    #"Is it getting warmer?": "Temperature",
    "Is the air getting more humid?": "Atmosphere moisture",
    "Is rainfall changing?": "Water",
    "Is the ground drying out?": "Land",
    "Is the ozone layer changing?": "Atmosphere composition",
    #"Are winds getting stronger?": "Wind",
}


def apply_catalog_scaling(time_series, variable_info: dict):
    return time_series * variable_info["scale_factor"] + variable_info["offset"]


def build_giovanni_link(variable_id: str, start_date: str, end_date: str) -> str:
    return (
        f"{GIOVANNI_BASE_URL}#service=ArAvTs&starttime={start_date}T00:00:00Z"
        f"&endtime={end_date}T23:59:59Z&data={variable_id}"
    )