# Load the jinja library's namespace into the current module.
import jinja2
from os import path

import pandas as pd


base_dir = path.join(path.curdir, "saved", "ceiling")
asset_dir = path.join(path.curdir, "assets")

df = pd.read_csv(path.join(base_dir, "1.csv"))

chunk_size = 4  # Adjust as needed

# Create list of sub-DataFrames
data_chunks = [
    df for df in (df[i : i + chunk_size] for i in range(0, len(df), chunk_size))
]

# In this case, we will load templates off the filesystem.
# This means we must construct a FileSystemLoader object.
#
# The search path can be used to make finding templates by
#   relative paths much easier.  In this case, we are using
#   absolute paths and thus set it to the filesystem root.
templateLoader = jinja2.FileSystemLoader(searchpath="/")

# An environment provides the data necessary to read and
#   parse our templates.  We pass in the loader object here.
templateEnv = jinja2.Environment(loader=templateLoader)

# This constant string specifies the template file we will use.
main_template = path.join(path.curdir, "pdf/template/index.html")
TEMPLATE_FILE = (
    "/Users/macbookpro/src/web-scraping/visualcomfort/pdf/template/index.html"
)

# Read the template file using the environment object.
# This also constructs our Template object.
template = templateEnv.get_template(TEMPLATE_FILE)

# Specify any input variables to the template as a dictionary.
templateVars = {
    "title": "Test Example",
    "description": "A simple inquiry of function.",
    "data": data_chunks,
}

# Finally, process the template to produce our final text.
outputText = template.render(templateVars)

output_file = path.join(path.curdir, "pdf", "output", "html", "index.html")

with open(output_file, "w") as file:
    file.write(outputText)

print(outputText)
