"""Modul is supposed for exploratory data analysis"""
# Import usable libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

# Reading the file
hotel_bookings = pd.read_csv(r'C:\Users\User\Downloads\hotel_bookings.csv')

# Setting a convenient width
pd.set_option('display.width', None)

# EDA section
# first check
heading = hotel_bookings.head()


with open(".\\result\\" + "analyse_result.txt", "w") as f1:
    f1.write("Result of calculation" + "\n"*2)


def add_result_to_file(name_of_data, output_data):
    with open(".\\result\\" + "analyse_result.txt", "a") as f:
        f.write(name_of_data + "\n")
        f.write(str(output_data) + "\n"*2)
        f.write(f"{'*'*300}"+"\n")
        f.write("\n" * 2)


add_result_to_file('Heading of dataframe', heading)
print(heading, '\n')

# short description about numerical columns
description = hotel_bookings.describe()
add_result_to_file('Description of numeric columns', description)
print(description, '\n')

# some information about all columns
buf = io.StringIO()
hotel_bookings.info(buf=buf)
df_info = buf.getvalue()
add_result_to_file('Information about columns', df_info)
print(df_info)

# columns of different types with missed values
numeric_columns_with_missed_values = [col for col in hotel_bookings.columns
                                      if (hotel_bookings[col].isnull().any()) and
                                      (hotel_bookings[col].dtype == 'int64' or
                                       hotel_bookings[col].dtype == 'float64')]
object_columns_with_missed_values = [col for col in hotel_bookings.columns if (hotel_bookings[col].isnull().any())
                                     and hotel_bookings[col].dtype == 'object']

# unnecessary column
hotel_bookings.drop(['index'], axis=1, inplace=True)

# changing types and filling the gaps with reasonable values individually for all problematic columns
hotel_bookings['children'] = hotel_bookings['children'].fillna(0).astype('int64')
hotel_bookings['country'] = hotel_bookings['country'].fillna('Not_stated')
hotel_bookings['agent'] = hotel_bookings['agent'].fillna('Absent').astype('object')
hotel_bookings['company'] = hotel_bookings['company'].fillna('Unknown_company').astype('object')

# Creating new columns and replacing 0 with median values
hotel_bookings['all_stay_nights'] = hotel_bookings['stays_in_weekend_nights'] + hotel_bookings['stays_in_week_nights']
hotel_bookings['all_stay_nights'] = hotel_bookings['all_stay_nights'].replace(0, hotel_bookings[
    'all_stay_nights'].median())
hotel_bookings['adr'] = hotel_bookings['adr'].replace(0, hotel_bookings['adr'].median())
hotel_bookings['total_revenue'] = hotel_bookings['adr'] * hotel_bookings['all_stay_nights']

families_with_children = hotel_bookings.loc[(hotel_bookings['children'] > 0) & (hotel_bookings['babies'] == 0)]
families_with_babies = hotel_bookings.loc[(hotel_bookings['babies'] > 0)]
lonely_adults = hotel_bookings.loc[
    (hotel_bookings['children'] == 0) & (hotel_bookings['babies'] == 0) & (hotel_bookings['adults'] == 1)]
couples_of_adults = hotel_bookings.loc[
    (hotel_bookings['children'] == 0) & (hotel_bookings['babies'] == 0) & (hotel_bookings['adults'] == 2)]
groups_of_adults = hotel_bookings.loc[
    (hotel_bookings['children'] == 0) & (hotel_bookings['babies'] == 0) & (hotel_bookings['adults'] > 2)]


def plotting(groups: tuple, subgroups: dict, title: str) -> plt:
    """
    Shows plot of the group.
    :param groups: tuple of names
    :param subgroups: dictionary of collected data
    :param title: title of the plot
    """

    x = np.arange(len(groups))
    width = 0.35
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in subgroups.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=2)
        multiplier += 1

    ax.set_ylabel('Summary_adr')
    ax.set_title(title)
    ax.set_xticks(x + width, groups)
    ax.legend(loc='upper left')
    ax.set_ylim(auto=True)
    file_name = (".\\result\\" + f"{'_'.join(title.replace('/', '_').split())}.png")
    plt.savefig(f"{file_name}")
    plt.show()


# Initializing tranzit variables
categories = [families_with_children, families_with_babies, lonely_adults, couples_of_adults, groups_of_adults]
state = ('families_with_children', 'families_with_babies', 'lonely_adults', 'couples_of_adults', 'groups_of_adults')

sums = {'Canceled': [], 'Proved': []}
canceled_sums = []
proved_sums = []

type_hotel_sums = {'Resort_hotel': [], 'City_hotel': []}
City_sums = []
Resort_sums = []

guest_sums = {'Repeated_guests': [], 'New_guest': []}
Repeated_sums = []
New_sums = []

# Summing "total revenue" = money that guests have spent already during their beings in the hotels
for category in categories:
    canceled_sums.append(category[category['is_canceled'] == 1]['total_revenue'].sum())
    proved_sums.append(category[category['is_canceled'] == 0]['total_revenue'].sum())

    City_sums.append(category[category['hotel'] == 'City Hotel']['total_revenue'].sum())
    Resort_sums.append(category[category['hotel'] == 'Resort Hotel']['total_revenue'].sum())

    Repeated_sums.append(category[category['is_repeated_guest'] == 1]['total_revenue'].sum())
    New_sums.append(category[category['is_repeated_guest'] == 0]['total_revenue'].sum())

sums['Canceled'] = canceled_sums
sums['Proved'] = proved_sums

type_hotel_sums['Resort_hotel'] = City_sums
type_hotel_sums['City_hotel'] = Resort_sums

guest_sums['Repeated_guests'] = Repeated_sums
guest_sums['New_guest'] = New_sums

# Calling "plotting" function from different divisions
plotting(state, sums, 'Summary adr of canceled/proved bookings by categories')
plotting(state, type_hotel_sums, 'Summary adr of hotel types by categories')
plotting(state, guest_sums, 'Summary adr of repeated/new guests by categories')


def number_of_the_month(month: str) -> int:
    """
    Extracts number of the month
    :param month: name of the month
    :return: number of month
    """

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December', ]
    return months.index(month) + 1


hotel_bookings['month_number'] = hotel_bookings['arrival_date_month'].apply(lambda month: number_of_the_month(month))

(hotel_bookings[['arrival_date_year', 'month_number', 'total_revenue']]
 .groupby(['arrival_date_year', 'month_number']).sum('total_revenue')
 .sort_values(by=['arrival_date_year', 'month_number']).plot.bar().set_ylim(auto=True))
plt.show()


(hotel_bookings[['arrival_date_year', 'total_revenue']]
 .groupby(['arrival_date_year']).sum('total_revenue')
 .sort_values(by=['arrival_date_year']).plot.bar().set_ylim(auto=True))
plt.show()


# Dividing on subgroups by 'repeated_guest' flag and 'group by' statement
repeated_ch_families = (families_with_children.loc[families_with_children['is_repeated_guest'] == 1]
                        [['is_canceled', 'hotel', 'children', 'total_revenue', 'lead_time']]
                        .groupby(['is_canceled', 'hotel', 'children']).agg(['mean', 'count']))
not_repeated_ch_families = (families_with_children.loc[families_with_children['is_repeated_guest'] == 0]
                            [['is_canceled', 'hotel', 'children', 'total_revenue', 'lead_time']]
                            .groupby(['is_canceled', 'hotel', 'children']).agg(['mean', 'count']))

repeated_ba_families = (families_with_babies.loc[families_with_babies['is_repeated_guest'] == 1]
                        [['is_canceled', 'hotel', 'babies', 'total_revenue', 'lead_time']]
                        .groupby(['is_canceled', 'hotel', 'babies']).agg(['mean', 'count']))
not_repeated_ba_families = (families_with_babies.loc[families_with_babies['is_repeated_guest'] == 0]
                            [['is_canceled', 'hotel', 'babies', 'total_revenue', 'lead_time']]
                            .groupby(['is_canceled', 'hotel', 'babies']).agg(['mean', 'count']))

repeated_lonely_adults = (lonely_adults.loc[lonely_adults['is_repeated_guest'] == 1]
                          [['is_canceled', 'hotel', 'adults', 'total_revenue', 'lead_time']]
                          .groupby(['is_canceled', 'hotel', 'adults']).agg(['mean', 'count']))
not_repeated_lonely_adults = (lonely_adults.loc[lonely_adults['is_repeated_guest'] == 0]
                              [['is_canceled', 'hotel', 'adults', 'total_revenue', 'lead_time']]
                              .groupby(['is_canceled', 'hotel', 'adults']).agg(['mean', 'count']))

repeated_couples_of_adults = (couples_of_adults.loc[couples_of_adults['is_repeated_guest'] == 1]
                              [['is_canceled', 'hotel', 'adults', 'total_revenue', 'lead_time']]
                              .groupby(['is_canceled', 'hotel', 'adults']).agg(['mean', 'count']))
not_repeated_couples_of_adults = (couples_of_adults.loc[couples_of_adults['is_repeated_guest'] == 0]
                                  [['is_canceled', 'hotel', 'adults', 'total_revenue', 'lead_time']]
                                  .groupby(['is_canceled', 'hotel', 'adults']).agg(['mean', 'count']))

repeated_groups_of_adults = (groups_of_adults.loc[groups_of_adults['is_repeated_guest'] == 1]
                             [['is_canceled', 'hotel', 'adults', 'total_revenue', 'lead_time']]
                             .groupby(['is_canceled', 'hotel', 'adults']).agg(['mean', 'count']))
not_repeated_groups_of_adults = (groups_of_adults.loc[groups_of_adults['is_repeated_guest'] == 0]
                                 [['is_canceled', 'hotel', 'adults', 'total_revenue', 'lead_time']]
                                 .groupby(['is_canceled', 'hotel', 'adults']).agg(['mean', 'count']))

# Initializing the list of groups and the list of their names
subgroups_by_repetition = [repeated_ch_families, not_repeated_ch_families, repeated_ba_families,
                           not_repeated_ba_families, repeated_lonely_adults, not_repeated_lonely_adults,
                           repeated_couples_of_adults, not_repeated_couples_of_adults, repeated_groups_of_adults,
                           not_repeated_groups_of_adults]
subgroups_by_repetition_names = ['repeated children families', 'not repeated children families',
                                 'repeated babies families', 'not repeated babies families', 'repeated lonely adults',
                                 'not repeated lonely adults', 'repeated couples of adults',
                                 'not repeated couples of adults', 'repeated groups of adults',
                                 'not repeated groups of adults']

# Adding new feature - coverage of the class in the subgroup (= median revenue * count of cases)
# Count under-received money due to cancellations and its rate
for name, subgroup in enumerate(subgroups_by_repetition):
    subgroup['coverage_of_group'] = subgroup.iloc[:, 0] * subgroup.iloc[:, 1]
    if subgroup is repeated_ba_families:
        loss_rate = 0
        loss_amount = 0
    else:
        loss_amount = subgroup.loc[1,]['coverage_of_group'].sum()
        loss_rate = subgroup.loc[1,]['coverage_of_group'].sum() / subgroup['coverage_of_group'].sum()
    add_result_to_file(subgroups_by_repetition_names[name], subgroup)
    print(subgroup, '\n')
    result = (f'Under-received (due to cancellations) money share in {subgroups_by_repetition_names[name]} is '
              f'{int(round(loss_rate, 2) * 100)}% ~ {int(loss_amount)}$.' + 3 * '\n')
    add_result_to_file('Brief conclusion', result)
    print(result)
