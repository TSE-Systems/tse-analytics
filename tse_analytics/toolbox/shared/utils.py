def get_plot_layout(number_of_elements: int) -> tuple[int, int]:
    if number_of_elements == 1:
        return 1, 1
    elif number_of_elements == 2:
        return 1, 2
    elif number_of_elements <= 4:
        return 2, 2
    else:
        return round(number_of_elements / 3) + 1, 3
