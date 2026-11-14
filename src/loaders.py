import io
import re

import numpy as np
import pandas as pd


def parse_giovanni_metadata(metadata_lines: list[str]) -> dict:
    metadata = {}
    for line in metadata_lines:
        key, separator, value = line.partition(":,")
        if separator:
            metadata[key.strip()] = value.strip().strip('"')
    return metadata


def load_giovanni_csv(uploaded_file) -> tuple[pd.Series, dict]:
    """Parse a Giovanni time-series CSV -> (monthly series, metadata)."""
    raw_text = uploaded_file.read().decode("utf-8", errors="replace")
    all_lines = raw_text.splitlines()

    header_line_index = next(
        line_index
        for line_index, line in enumerate(all_lines)
        if line.strip().lower().startswith("time,")
    )
    metadata = parse_giovanni_metadata(all_lines[:header_line_index])

    table_text = "\n".join(all_lines[header_line_index:])
    data_frame = pd.read_csv(io.StringIO(table_text), skipinitialspace=True)
    time_column, value_column = data_frame.columns[0], data_frame.columns[1]

    fill_value_key = next((key for key in metadata if key.startswith("Fill Value")), None)
    fill_value = float(metadata[fill_value_key]) if fill_value_key else -9999.0

    values = pd.to_numeric(data_frame[value_column], errors="coerce")
    values = values.where(values != fill_value, np.nan)

    time_index = pd.to_datetime(data_frame[time_column])
    time_series = pd.Series(values.to_numpy(), index=time_index, name=value_column)
    time_series = time_series.sort_index().asfreq("MS")

    url = metadata.get("URL to Reproduce Results", "")
    variable_match = re.search(r"data=([^&]+)", url)
    metadata["variable_id"] = variable_match.group(1) if variable_match else value_column
    metadata["title"] = metadata.get("Title", value_column)
    return time_series, metadata