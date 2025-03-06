from drf_yasg.inspectors import FieldInspector
from drf_yasg import openapi
from rest_framework.fields import DecimalField

# Field Inspector to handle Decimal fields as floats
class DecimalAsFloatInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        # Convert DecimalField to float in the schema
        if isinstance(obj, DecimalField):
            result.type = openapi.TYPE_NUMBER
            result.format = openapi.FORMAT_FLOAT
        return result
