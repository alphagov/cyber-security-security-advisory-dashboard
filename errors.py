import sys
import json
import traceback


def get_log_event():
    """Finds the current exception and returns a JSON formatted
    representation. Useful when outputting stack traces to
    cloudwatch.
    """
    return json.dumps({
        "message": traceback.format_exc().split("\n"),
        "stack": [
            {
                "filename": frame.filename,
                "line": frame.line,
                "lineno": frame.lineno,
                "locals": frame.locals,
                "name": frame.name,
            }
            for frame in traceback.extract_tb(sys.exc_info()[2])
        ]
    })

