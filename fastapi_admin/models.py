from tortoise import Model, fields


class AbstractAdmin(Model):
    username: str = fields.CharField(max_length=50, unique=True)
    password: str = fields.CharField(max_length=200)

    class Meta:
        abstract = True
