from lib import CONN, CURSOR

class Review:
    all = {}

    def __init__(self, year, summary, employee, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        if isinstance(employee, int):
            from lib.employee import Employee
            self.employee = Employee.find_by_id(employee)
        else:
            self.employee = employee

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee {self.employee.id}>"

    # ---------- Table Methods ----------
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(sql)
        CONN.commit()

    # ---------- ORM Methods ----------
    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee.id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        from lib.employee import Employee
        employee = Employee.find_by_id(employee_id)
        review = cls(year, summary, employee)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review = cls.all.get(row[0])
        if review:
            review.year = row[1]
            review.summary = row[2]
            from lib.employee import Employee
            review.employee = Employee.find_by_id(row[3])
        else:
            from lib.employee import Employee
            employee = Employee.find_by_id(row[3])
            review = cls(row[1], row[2], employee, row[0])
            cls.all[row[0]] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee.id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # ---------- Property Methods ----------
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer >= 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee(self):
        return self._employee

    @employee.setter
    def employee(self, value):
        from lib.employee import Employee
        if isinstance(value, Employee) and value.id is not None:
            self._employee = value
        else:
            raise ValueError("Employee must be a persisted Employee instance")

    @property
    def employee_id(self):
        return self.employee.id
    
    @employee_id.setter
    def employee_id(self, value):
        from lib.employee import Employee
        employee = Employee.find_by_id(value)
        if employee:
            self.employee = employee
        else:
            raise ValueError("Employee ID must reference a valid employee in the database")
