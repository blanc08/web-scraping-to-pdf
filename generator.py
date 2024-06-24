# Load the jinja library's namespace into the current module.
from os import path
import os
import uuid
import jinja2
import pandas as pd
import pdfkit

from constant import CATEGORIES
from utils import make_output_dir


class PDFGenerator:
    def __init__(self, category: str):
        self.output_path = None

        make_output_dir()

        if category.lower() not in CATEGORIES:
            raise FileNotFoundError("invalid category")

        self.category = category

        # In this case, we will load templates off the filesystem.
        # This means we must construct a FileSystemLoader object.
        #
        # The search path can be used to make finding templates by
        #   relative paths much easier.  In this case, we are using
        #   absolute paths and thus set it to the filesystem root.
        templateLoader = jinja2.FileSystemLoader(searchpath="template")

        # An environment provides the data necessary to read and
        #   parse our templates.  We pass in the loader object here.
        templateEnv = jinja2.Environment(loader=templateLoader)

        # This constant string specifies the template file we will use.
        TEMPLATE_FILE = f"{category.lower()}/index.html"

        # Read the template file using the environment object.
        # This also constructs our Template object.
        self.template = templateEnv.get_template(TEMPLATE_FILE)

    def generate_html_batch(self):
        """
        docstring
        """
        df = pd.DataFrame({})

        df_list = []
        file_list = os.listdir(path.join(path.curdir, "out/csv", self.category))
        for i in file_list:
            df_list.append(
                pd.read_csv(path.join(path.curdir, "out/csv", self.category, i))
            )

        # concat df object
        df = pd.concat(df_list, axis=0)

        # slice each pdf to contains 25 page, 1 page contain 4 image
        page_size = 75 * 4  # Adjust as needed

        # Create list of sub-DataFrames
        pages = [
            df for df in (df[i : i + page_size] for i in range(0, len(df), page_size))
        ]

        for index, page in enumerate(pages):
            chunk_size = 4  # Adjust as needed

            # Create list of sub-DataFrames
            data_chunks = [
                page
                for page in (
                    page[i : i + chunk_size] for i in range(0, len(page), chunk_size)
                )
            ]

            # Specify any input variables to the template as a dictionary.
            templateVars = {
                "title": "PDF Generator",
                "description": "A simple inquiry of function.",
                "data": data_chunks,
            }

            # Finally, process the template to produce our final text.
            outputText = self.template.render(templateVars)

            output_filename = str(index) + str(uuid.uuid4())

            output_file = path.join(
                path.curdir,
                "out/html",
                self.category.lower(),
                f"{output_filename}.html",
            )

            with open(output_file, "w") as file:
                file.write(outputText)

            self.output_path = output_file

    def generate_html(self, filename: str = None):
        """
        docstring
        """
        df = pd.DataFrame({})

        if filename == None or filename == "":
            df_list = []
            file_list = os.listdir(path.join(path.curdir, "out/csv", self.category))
            for i in file_list:
                df_list.append(
                    pd.read_csv(path.join(path.curdir, "out/csv", self.category, i))
                )

            # concat df object
            df = pd.concat(df_list, axis=0)
        else:
            df = pd.read_csv(path.join(path.curdir, "out/csv", self.category, filename))

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
        templateLoader = jinja2.FileSystemLoader(searchpath="template")

        # An environment provides the data necessary to read and
        #   parse our templates.  We pass in the loader object here.
        templateEnv = jinja2.Environment(loader=templateLoader)

        # This constant string specifies the template file we will use.
        TEMPLATE_FILE = f"{self.category.lower()}/index.html"

        # Read the template file using the environment object.
        # This also constructs our Template object.
        template = templateEnv.get_template(TEMPLATE_FILE)

        # Specify any input variables to the template as a dictionary.
        templateVars = {
            "title": "PDF Generator",
            "description": "A simple inquiry of function.",
            "data": data_chunks,
        }

        # Finally, process the template to produce our final text.
        outputText = template.render(templateVars)

        output_filename = "default"
        if filename != None and filename != "":
            output_file = filename.split(".")[0]

        output_file = path.join(
            path.curdir, "out/html", self.category.lower(), f"{output_filename}.html"
        )

        with open(output_file, "w") as file:
            file.write(outputText)

        self.output_path = output_file

    # TODO : Stylignnya masih kacau
    def generate_pdf(self):
        # Optional: Customize with configuration options
        options = {"encoding": "UTF-8"}
        output_path_as_list = self.output_path.split("/")

        # replace html to pdf
        output_path_as_list[-3] = "pdf"
        pdf_output_path = "/".join(output_path_as_list) + ".pdf"
        pdfkit.from_file(self.output_path, pdf_output_path, options=options)

    def generate_pdf_batch(self):
        # Optional: Customize with configuration options
        options = {"encoding": "UTF-8"}
        file_list = os.listdir(path.join(path.curdir, "out/html", self.category))

        # replace html to pdf
        input_path = path.join(path.curdir, "out/html", self.category)
        output_path = path.join(path.curdir, "out/pdf", self.category)

        for file in file_list:
            pdfkit.from_file(
                path.join(input_path, file),
                output_path + str(uuid.uuid4()) + ".pdf",
                options=options,
            )


# ceiling = PDFGenerator(category="ceiling")
# ceiling.generate_html_batch()

# fans = PDFGenerator(category="fans")
# fans.generate_html_batch()

# floor = PDFGenerator(category="floor")
# floor.generate_html_batch()

# outdoor = PDFGenerator(category="outdoor")
# outdoor.generate_html_batch()

# table = PDFGenerator(category="table")
# table.generate_html_batch()

wall = PDFGenerator(category="wall")
wall.generate_html_batch()

# input_path = path.join(path.curdir, "out/csv", "ceiling", "1.csv")
# generator.generate_pdf_batch()
