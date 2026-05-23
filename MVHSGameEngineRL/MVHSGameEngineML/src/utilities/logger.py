

class Logger:

    @staticmethod
    def log_error(caller, error_message):
        caller_object_name = caller.__class__.__name__ if object is not None else ""
        print(f"{"\033[31mError\033[0m"} - {caller_object_name}: {error_message}")

    @staticmethod
    def log_warning(caller, warning_message):
        caller_object_name = caller.__class__.__name__ if object is not None else ""
        print("\033[33mWarning\033[0m", caller_object_name + ":", warning_message)


    @staticmethod
    def log_message(caller, message):
        caller_object_name = caller.__class__.__name__ if object is not None else ""
        print(caller_object_name + ":", message)

    @staticmethod
    def log_success(caller, success_message):
        caller_object_name = caller.__class__.__name__ if object is not None else ""
        print("\033[32mSuccess\033[0m", caller_object_name + ":", success_message)

