def build_verdict(variable_name: str, units: str, trend_result: dict, start_year: int, end_year: int) -> str:
    slope = trend_result["theil_sen_slope_per_decade"]
    ci_low = trend_result["ci_low_per_decade"]
    ci_high = trend_result["ci_high_per_decade"]
    direction = "increased" if slope > 0 else "decreased"

    summary = (
        f"Between {start_year} and {end_year}, {variable_name} {direction} by "
        f"**{slope:+.2f} {units} per decade** (95% CI: {ci_low:+.2f} to {ci_high:+.2f})."
    )

    if trend_result["is_significant"]:
        significance = (
            f"The trend is **statistically significant** (all tests give p < 0.05; "
            f"most conservative p = {trend_result['worst_case_p_value']:.4f})."
        )
    else:
        significance = (
            f"The trend is **not statistically significant** "
            f"(most conservative p = {trend_result['worst_case_p_value']:.3f}). "
            "A longer record could change this."
        )

    caveat = (
        f"Based on {trend_result['number_of_years']:.0f} years of monthly data, "
        "with the seasonal cycle removed. A linear trend assumes steady change."
    )
    return f"{summary}\n\n{significance}\n\n_{caveat}_"


def build_comparison_verdict(
    first_label: str, second_label: str, first_result: dict, second_result: dict, units: str
) -> str:
    first_slope = first_result["theil_sen_slope_per_decade"]
    second_slope = second_result["theil_sen_slope_per_decade"]
    both_significant = first_result["is_significant"] and second_result["is_significant"]
    opposite_signs = first_slope * second_slope < 0

    comparison = (
        f"{first_label}: **{first_slope:+.2f} {units}/decade** "
        f"({'significant' if first_result['is_significant'] else 'not significant'}). "
        f"{second_label}: **{second_slope:+.2f} {units}/decade** "
        f"({'significant' if second_result['is_significant'] else 'not significant'})."
    )
    if opposite_signs and both_significant:
        note = "The two regions show **significant trends in opposite directions**."
    elif opposite_signs:
        note = "The trends point in opposite directions, but at least one is not statistically significant."
    else:
        note = "Both regions trend in the same direction."
    return f"{comparison}\n\n{note}"