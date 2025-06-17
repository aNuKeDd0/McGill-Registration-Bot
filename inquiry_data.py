
class Inquiry:
    """
    Object to hold user data for course registration
    """
    def __init__(self, sid, pin, term, faculty, course_num, section):
        self.sid = sid
        self.pin = pin
        self.term = term
        self.faculty = faculty
        self.course_num = course_num
        self.section = section

    #TODO - Future, have main parse a CSV file with multiple course information, and sign up
    #TODO - for multiple courses at the same time from a single CSV file.