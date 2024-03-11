import uuid


def error(err,descr = "",id = ""):
    error = ""
    description = ""
    if isinstance(err, Exception):
        str_err = str(err)
        start_index = str_err.find("(")
        end_index = str_err.rfind(")")
        if not id:
            id = uuid.uuid4()
        error = str(type(err)).split("'")[1]
        description = str_err[start_index + 1:end_index],
    else:
        error = err
        description = descr

    error = {
            "error": error,
            "description": description,
            "identifier": id
        }
    return error