import pandas as pd


def make_short_name(full_name):
    tmp = full_name.split()
    tmp[1] = tmp[1][0] + "."
    tmp[2] = tmp[2][0] + "."

    return " ".join(tmp)


def make_cute_date(datetime, day=True, month=True, year=True):
    datetime = pd.to_datetime(datetime)
    date = []
    if day:
        date.append(datetime.day)
    if month:
        date.append(datetime.month)
    if year:
        date.append(datetime.year)

    return ".".join(map(str, date))


def parse_table(table_path, version):
    general_info_df = pd.read_excel(
        table_path, sheet_name="Общая информация", index_col=0
    ).T
    group_members_df = pd.read_excel(table_path, sheet_name="Участники").fillna("")
    rout_df = pd.read_excel(table_path, sheet_name="Маршрут", header=[0, 1], dtype=str)
    equipment_df = pd.read_excel(
        table_path, sheet_name="Снаряжение", header=[0, 1], dtype=str
    )

    general_rout_df = rout_df["основной вариант"].fillna("")
    reserve_rout_df = rout_df["запасной вариант"].dropna()
    emergency_rout_df = rout_df["аварийный вариант"].dropna()
    difficulties_df = rout_df["сложные участки маршрута"].dropna()
    weights_df = equipment_df["Весовые хар-ки груза"].dropna()

    general_info_df[general_info_df.columns.name] = general_info_df.index.values
    weights_df.set_index("Наименование", inplace=True)
    report_info = general_info_df["Отчёт кому (о начале)"].values[0].split(", ")

    general_info = {
        "date": make_cute_date(general_info_df["Дата подписания"].values[0]),
        "year": make_cute_date(
            general_info_df["Дата подписания"].values[0], day=False, month=False
        ),
        "start_day": make_cute_date(general_info_df["Дата начала"].values[0]),
        "finish_day": make_cute_date(general_info_df["Дата окончания"].values[0]),
        "leader_short_name": make_short_name(general_info_df["ФИО руковода"].values[0]),
        "leader_short_name_pp": make_short_name(general_info_df["ФИО руковода род. падеж"].values[0]),
        "start_report_date": make_cute_date(general_info_df["До (о начале)"].values[0]),
        "finish_report_date": make_cute_date(general_info_df["До (о конце)"].values[0]),
        "size_of_group": group_members_df.shape[0],
        "club_name": general_info_df["Турклуб"].values[0],
        "city": general_info_df["Город"].values[0],
        "complexity": general_info_df["Категория сложности"].values[0],
        "mountanious_area": general_info_df["Район"].values[0],
        "leader_full_name": general_info_df["ФИО руковода"].values[0],
        "leader_full_name_pp": general_info_df["ФИО руковода род. падеж"].values[0],
        "leader_phone_number": general_info_df["Телефон руковода"].values[0],
        "group_phone_number": general_info_df["Телефон группы"].values[0],
        "mchs_phone_number": general_info_df["Телефон мчс"].values[0],
        "mchs_name": general_info_df["Название ПСО"].values[0],
        "mchs_addres": general_info_df["Адрес ПСО"].values[0],
        "rout": general_info_df["Нитка маршрута"].values[0].replace("--", '"---'),
        "start_report_point": general_info_df["Из города (о начале)"].values[0],
        "finish_report_point": general_info_df["Из города (о конце)"].values[0],
        "total_distance": general_rout_df.iloc[-1]["км"],
        "total_days": general_rout_df.iloc[-1]["День пути"],
        "total_reserve_distance": general_rout_df.iloc[-1]["км"],
        "total_reserve_days": general_rout_df.iloc[-1]["День пути"],
    }

    food_weight = float(weights_df.loc["Раскладка (в день на чел), кг"].values[0])
    shared_equipment_weight = float(weights_df.loc["Групповое, кг"].values[0])
    personal_equipment_weight = float(weights_df.loc["Личное, кг"].values[0])
    long_circle_days = int(weights_df.loc["Самое долгое кольцо (дней)"].values[0])
    k = float(weights_df.loc["k = вес М - вес Ж (рюкзака, кг)"].values[0])

    n_days = int(general_info["total_days"])
    n_guys = int(general_info["size_of_group"])
    women_count = sum(group_members_df["Пол"] == "ж")
    men_count = n_guys - women_count

    total_weight = (
        food_weight * n_days + shared_equipment_weight + personal_equipment_weight
    )
    total_weight_per_cycle = (
        food_weight * long_circle_days
        + shared_equipment_weight
        + personal_equipment_weight
    )

    weights = [["", ""], ["", ""], ["", ""], ["", ""], [0, 0]]
    weights[0][0] = f"{round(food_weight * n_days, 1)}\,кг / {food_weight}\,кг"
    weights[0][1] = (
        f"{round(food_weight * n_days * n_guys, 1)}\,кг / {round(food_weight * n_guys, 1)}\,кг"
    )
    weights[1][0] = f"{round(shared_equipment_weight, 1)}\,кг"
    weights[1][1] = f"{round(shared_equipment_weight * n_guys)}\,кг"
    weights[2][0] = f"{round(personal_equipment_weight, 1)}\,кг"
    weights[2][1] = f"{round(personal_equipment_weight * n_guys)}\,кг"
    weights[3][0] = (
        f"{round(total_weight, 1)}\,кг ({round(total_weight_per_cycle, 1)}\,кг)"
    )
    weights[3][1] = (
        f"{round(total_weight * n_guys, 1)}\,кг ({round(total_weight_per_cycle * n_guys, 1)}\,кг)"
    )
    weights[4][0] = round(
        (total_weight_per_cycle * n_guys - men_count * k) / n_guys, 1
    )
    weights[4][1] = round(weights[4][0] + k, 1)

    # weights[4][0] = round(
    #     total_weight_per_cycle * n_guys / (women_count + men_count * k), 1
    # )
    # weights[4][1] = round(k * weights[4][0], 1)

    # =========================
    group_members_table_1 = []
    group_members_table_2 = []
    rout_plan_table = []
    reserve_rout_plan_table = []
    emergency_rout_plan_table = []
    equipment_table = []
    report_to = []
    tables = {}

    match version:
        case 'Moscow':
            for i, row in enumerate(group_members_df.iterrows(), start=1):
                full_name = row[1]["ФИО"]
                birthdate = row[1]["Год рождения"]
                home = row[1]["Место проживания: субъект РФ, населённый пункт"]
                phone = row[1]["Телефон"]
                relatives_phone = row[1]["Телефон родственников"]
                experience = row[1]["Походный опыт"]
                post = row[1]["Походная должность"]

                birthdate = make_cute_date(birthdate, month=False, day=False)
                living_place = f"{home}, {str(phone)}"
                relatives_phone = str(relatives_phone)
                
                group_members_table_1.append(
                    " & ".join([str(i), full_name, birthdate, living_place, ""])
                    + r"\\ \hline "
                )
                group_members_table_2.append(" & ".join([relatives_phone, experience, post, ""]) + r"\\ \hline ")
        case 'Region':
            for i, row in enumerate(group_members_df.iterrows(), start=1):
                full_name = row[1]["ФИО"]
                birthdate = row[1]["Дата рождения"]
                workplace = row[1]["Место работы, должность"]
                home = row[1]["Адрес прописки"]
                phone = row[1]["Номер родственников"]
                experience = row[1]["Походный опыт"]
                post = row[1]["Походная должность"]

                birthdate = make_cute_date(birthdate)
                living_place = f"{home}, +{str(phone)}"

                group_members_table_1.append(
                    " & ".join([str(i), full_name, birthdate, workplace, living_place, ""])
                    + r"\\ \hline "
                )
                group_members_table_2.append(" & ".join([experience, post, ""]) + r"\\ \hline ")

    for row in general_rout_df.iterrows():
        row[1]["Дата"] = make_cute_date(row[1]["Дата"], year=False)
        rout_plan_table.append(" & ".join(row[1].values))

    for row in reserve_rout_df.iterrows():
        row[1]["Дата"] = make_cute_date(row[1]["Дата"], year=False)
        reserve_rout_plan_table.append(" & ".join(row[1].values))

    for row in emergency_rout_df.iterrows():
        first_day, last_day = row[1]["Дата"].split("--")
        row[1]["Дата"] = (
            f"{make_cute_date(first_day, year=False)}--{make_cute_date(last_day, year=False)}"
        )
        emergency_rout_plan_table.append(" & ".join(row[1].values))

    for row in equipment_df[["Групповое", "Личное"]].fillna("").iterrows():
        row[1].values[0] = row[1].values[0].replace("Diam", "\diameter")
        # print(row[1].values)
        equipment_table.append(" & ".join(row[1].values))

    for phone_and_name in report_info:
        name, phone_number = phone_and_name[:-1].split("(")
        report_to.append(f"\item {name}\hfill {phone_number}\n")

    tables["group_members_1"] = "".join(group_members_table_1)
    tables["group_members_2"] = "".join(group_members_table_2)
    tables["general_rout"] = r"\\ \hline ".join(rout_plan_table[:-1] + [""])
    tables["reserve_rout"] = r"\\ \hline ".join(reserve_rout_plan_table + [""])
    tables["emergency_rout"] = r"\\ \hline ".join(emergency_rout_plan_table + [""])
    tables["equipment"] = r"\\ \hline ".join(equipment_table + [""])

    general_info["report_to"] = "".join(report_to)  # TODO(Dima): телефон
    general_info["difficult_parts"] = "\n".join(
        [
            r"\item " + row[1].values[0].replace("ГРАД", "$^\circ$")
            for row in difficulties_df.iterrows()
        ]
    )

    return (general_info, tables, weights)
