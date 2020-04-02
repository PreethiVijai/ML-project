import pandas as pd

FOOD_FILE = './data/food-environment.xls'
EDUCATION_FILE = './data/educational-attainment.xls'

# FOOD ENVIRONMENT DATA.

# Each of these sheets becomes a key in the `food` dict.
food_sheets = [
    "Supplemental Data - County",
    "ACCESS",
    "STORES",
    "RESTAURANTS",
    "ASSISTANCE",
    "INSECURITY",
    "PRICES_TAXES",
    "LOCAL",
    "HEALTH",
    "SOCIOECONOMIC",
]

# Import dictionary of food environment data.
food = pd.read_excel(
    FOOD_FILE,
    sheet_name=food_sheets,
    thousands=',', # Convert numbers stored as strings to ints/floats.
    # Index each DataFrame by the FIPS column.  This is a unique ID
    # for every county/region.  If this works properly, we should be
    # be able to match rows across DataFrames easily.
    index_col=0,
)
# Let's rekey the supplemental DataFrame for easier access.
food["SUPPLEMENTAL"] = food["Supplemental Data - County"]
del food["Supplemental Data - County"]
# For some reason the supplemental data sheet contains a 2 counties that
# the other sheets do not contain, and the other sheets contain 3 counties that
# the supplemental data sheet doesn't contain.  (All the other sheets contain
# the exact same set of counties, I checked.)
# Let's simplify things and just delete the 5 extraneous counties from all
# of the DataFrames.  If we decide not to use the SUPPLEMENTAL data we can
# delete this section:
food["SUPPLEMENTAL"].drop(
    food["SUPPLEMENTAL"].index.difference(food["ACCESS"].index),
    inplace=True
)
for key, df in food.items():
    if key == "SUPPLEMENTAL":
        # Skip this one
        continue
    df.drop(df.index.difference(food["SUPPLEMENTAL"].index), inplace=True)

# Merge all the food into one DataFrame, without repeating columns
_l = list(food.values())
all_food = _l.pop()
for df in _l:
    all_food = pd.concat([all_food, df[df.columns.difference(all_food.columns)]], axis=1)

# EDUCATIONAL ATTAINMENT DATA.

education = pd.read_excel(
    EDUCATION_FILE,
    # sheet_name=0, # There's only one sheet.
    # Again, the first column is the FIPS Code column.
    index_col=0,
    skiprows=4, # The first four rows are just intro text
)
# Rename the Index column to "FIPS" to match the other files.
education.index.names = ['FIPS']

# There is more significant mismatch between the education data and the other
# data.  The education spreadsheet includes 143 FIPS that the other spreadsheet
# doesn't have.  Let's do the simple thing here and delete those 143 as well.
education.drop(education.index.difference(food["ACCESS"].index), inplace=True)

# The other spreadsheet doesn't include any extra FIPS other than the ones
# already caught by calculating the intersection between the supplemental and
# other sheets, but lets include this loop anyway, just in case we delete that
# section above.
for key, df in food.items():
    df.drop(df.index.difference(education.index), inplace=True)
