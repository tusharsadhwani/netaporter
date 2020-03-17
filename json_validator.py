from jsonschema import Draft4Validator, FormatChecker
from jsonschema.exceptions import ValidationError

def input_validator():
    schema = {
        "type" : "object",
        "properties" : {
            "filters" : {
                "type" : "array",
                "minItems": 1,
                "items" : {
                    "type" : "object",
                    "properties" : {
                        "operand1" : {
                            "type" : "string",
                        },
                        "operator" : {
                            "type" : "string",
                            "format" : "operator",
                        },
                        "operand2" : {
                            "type" : ["number", "string"],
                        },
                    },
                    "required" : ["operand1", "operator", "operand2"],
                },
            },
        },
        "required" : ["filters"],
    }
    format_checker = FormatChecker()

    @format_checker.checks('operator')
    def is_operator(value):
        return value in ['==', '<', '>']

    return Draft4Validator(schema, format_checker=format_checker)
