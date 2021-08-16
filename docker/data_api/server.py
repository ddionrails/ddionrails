# pylint: ignore
# nosec
from pathlib import Path

from flask import Flask, Response, json, request

main_path = Path("./platform-datasets/testdaten/").absolute()

test = [{"id": 1, "name": "A"}]

api = Flask(__name__)


@api.route("/meta", methods=["POST"])
def get_meta():
    variable = request.json["variable"]  # args.get("variable", default="")
    meta_file_name = "meta.json"
    file_path = main_path.joinpath(f"{variable}")
    file_path = file_path.joinpath(meta_file_name)

    with open(file_path, "r") as _file:
        file_content = "".join(_file.readlines())
    return Response(
        file_content,
        mimetype="text/json",
        headers={"Content-disposition": f"attachment; filename={meta_file_name}"},
    )


@api.route("/data", methods=["POST"])
def get_data():
    variable = request.json["variable"]  # args.get("variable", default="")
    dimensions = ["year"]
    extra_dimensions = list(set(request.json.get("dimensions", [])))
    if extra_dimensions:
        extra_dimensions = sorted(extra_dimensions, key=lambda item: item.lower())
    dimensions.extend(extra_dimensions)
    dimensions_string = "_".join(dimensions)
    meta_file_name = "meta.json"
    file_name = f"{variable}_{dimensions_string}.csv"

    file_path = main_path.joinpath(f"{variable}")
    file_path = file_path.joinpath(file_name)

    with open(file_path, "r") as _file:
        file_content = "".join(_file.readlines())
    return Response(
        file_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={file_name}"},
    )


if __name__ == "__main__":
    api.run(host="0.0.0.0")
