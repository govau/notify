from notifications_utils.columns import Columns


class TemplateChange():

    def __init__(self, old_template, new_template):
        self.old_placeholders = Columns.from_keys(old_template.placeholders)
        self.new_placeholders = Columns.from_keys(new_template.placeholders)

    @property
    def has_different_placeholders(self):
        return bool(self.new_placeholders.keys() ^ self.old_placeholders.keys())

    @property
    def placeholders_added(self):
        return set(
            self.new_placeholders.get(key)
            for key in self.new_placeholders.keys() - self.old_placeholders.keys()
        )

    @property
    def placeholders_removed(self):
        return set(
            self.old_placeholders.get(key)
            for key in self.old_placeholders.keys() - self.new_placeholders.keys()
        )
