class MyClass:
    # 这里的mytoken就是类似Java中的静态变量
    mytoken = 0

    @classmethod
    def set_class_var(cls, new_value):
        cls.mytoken = new_value

    @classmethod
    def get_class_var(cls):
        return cls.mytoken

