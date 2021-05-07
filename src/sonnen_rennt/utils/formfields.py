
from django import forms


class NT_DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    input_formats = ["%d.%m.%Y %H:%M"]
    # input_formats = ["%d-%m-%Y %H:%M %Z"],
    #
    # def __init__(self, attrs):
    #     super().__init__(attrs)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# class NT_DurationInput(forms.TimeInput):
#     input_type = 'time'
#
#
# 'start': forms.DateInput(
#
#
#     attrs={
#         'class':'datepicker',
#         'value': datetime.now().strftime("%d-%m-%Y")
#     }
#
#
# )
