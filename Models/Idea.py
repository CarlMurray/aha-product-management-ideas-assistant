class Idea():
    id: str = ""
    ref: str = ""
    name: str = ""
    description: str = ""

    def __init__(self, id, ref, name, description):
        self.id = id
        self.ref = ref
        self.name = name
        self.description = description
