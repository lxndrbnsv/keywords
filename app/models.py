from app import db


class KeywordsDomain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kw_domain = db.Column(db.String(240))
    kw_query = db.Column(db.String(240))
    kw_file_path = db.Column(db.String(240))

    def __repr__(self):
        return "<Element {}>".format(self.id)
