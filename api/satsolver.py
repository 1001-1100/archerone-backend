import datetime
from z3 import *
from .models import CourseOffering, Course, Timeslot


def addHardConstraints(z3, highCourses, lowCourses, filterFull):
    allOfferings = CourseOffering.objects.none()
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
        for o in offerings:
            for o2 in offerings:
                if(o.section != o2.section):
                    a = Bool(str(o.classnumber))
                    b = Not(Bool(str(o2.classnumber)))
                    z3.add(Implies(a,b))
    for c in lowCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
        for o in offerings:
            for o2 in offerings:
                if(o.section != o2.section):
                    a = Bool(str(o.classnumber))
                    b = Not(Bool(str(o2.classnumber)))
                    z3.add(Implies(a,b))
    for o in allOfferings:
        if(filterFull):
            if(o.current_enrolled >= o.max_enrolled):
                a = Not(Bool(str(o.classnumber)))
                z3.add(a)
        for o2 in allOfferings:
            if(o.section != o2.section or o.course != o2.course):
                if(o.day == o2.day):
                    if(o.timeslot == o2.timeslot):
                        a = Bool(str(o.classnumber))
                        b = Not(Bool(str(o2.classnumber)))
                        z3.add(Implies(a,b))
                    else:
                        firstTime = o.timeslot
                        secondTime = o2.timeslot
                        if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))

def addSoftConstraints(z3, highCourses, lowCourses):
    currentPriority = 10 
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        for o in offerings:
            z3.add_soft(Bool(str(o.classnumber)), currentPriority) 
        currentPriority -= 0.1
    currentPriority = 2
    for c in lowCourses:
        offerings = CourseOffering.objects.filter(course=c)
        for o in offerings:
            z3.add_soft(Bool(str(o.classnumber)), currentPriority)
        currentPriority -= 0.01
    # for o in courseOfferings:
    #     a = Not(Bool(str(o['classNmbr'])))
    #     z3.add_soft(a, 10)

def addFriendConstraints(z3, mainCourses, diffCourses, sameCourses, mainUser, friends):

    mainOfferings = CourseOffering.objects.none()
    diffOfferings = CourseOffering.objects.none()
    sameOfferings = CourseOffering.objects.none()
    diffClassnumbers = []

    for c in mainCourses:
        offerings = CourseOffering.objects.filter(course=c)
        mainOfferings = mainOfferings | offerings

    for c in diffCourses:
        offerings = CourseOffering.objects.filter(course=c)
        for o in offerings:
            diffClassnumbers.append(o.classnumber)
        diffOfferings = diffOfferings | offerings

    for c in sameCourses:
        offerings = CourseOffering.objects.filter(course=c)
        sameOfferings = sameOfferings | offerings

    for o in sameOfferings:
        z3.add_soft(Bool(str(o.classnumber)))
    
    diffClassnumbers = list(set(diffClassnumbers))

    for c in mainUser['scheduleClasses']:
        if(c not in diffClassnumbers):
            z3.add_soft(Bool(str(c)))

    for o in mainOfferings:
        for o2 in diffOfferings:
            if(o.day == o2.day):
                if(o.timeslot == o2.timeslot):
                    a = Bool(str(o.classnumber))
                    b = Bool(str(o2.classnumber))
                    z3.add_soft(Implies(a,b),2)
                else:
                    firstTime = o.timeslot
                    secondTime = o2.timeslot
                    if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                        a = Bool(str(o.classnumber))
                        b = Bool(str(o2.classnumber))
                        z3.add_soft(Implies(a,b))
                    elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                        a = Bool(str(o.classnumber))
                        b = Bool(str(o2.classnumber))
                        z3.add_soft(Implies(a,b))
                    elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                        a = Bool(str(o.classnumber))
                        b = Bool(str(o2.classnumber))
                        z3.add_soft(Implies(a,b))

def addPreferences(z3, highCourses, lowCourses, preferences):
    allOfferings = CourseOffering.objects.none()
    otherPreferences = {}
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
    for c in lowCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
    for p in preferences:
        if(p.earliest_class_time != None):
            earliest = p.earliest_class_time
            for o in allOfferings:
                if(earliest > o.timeslot.begin_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))),2)
        if(p.latest_class_time != None):
            latest = p.latest_class_time
            for o in allOfferings:
                if(latest < o.timeslot.end_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))))
        if(p.preferred_days != None):
            day_id = p.preferred_days.id
            for o in allOfferings:
                if(day_id == o.day.id):
                    z3.add_soft(Bool(str(o.classnumber)))
        if(p.preferred_buildings != None):
            print(p.preferred_buildings)
        if(p.preferred_sections != None):
            section_code = p.preferred_sections
            for o in allOfferings:
                if(len(str(section_code)) == 1):
                    if(str(section_code)[0] == str(o.section.section_code)[0]):
                        z3.add_soft(Bool(str(o.classnumber)),2)
                else:
                    if(str(section_code) == str(o.section.section_code)):
                        z3.add_soft(Bool(str(o.classnumber)),2)
        if(p.preferred_faculty != None):
            faculty_id = p.preferred_faculty.id
            for o in allOfferings:
                if(o.faculty != None):
                    if(faculty_id == o.faculty.id):
                        z3.add_soft(Bool(str(o.classnumber)))
        if(p.min_courses != None):
            otherPreferences['min_courses'] = p.min_courses
        if(p.max_courses != None):
            otherPreferences['max_courses'] = p.max_courses
        if(p.undesirable_classes != None):
            classnumber = p.undesirable_classes
            z3.add_soft(Not(Bool(str(classnumber))), 100)
        # if(p.break_length != None):
        #     break_length = p.break_length
        #     for o in allOfferings:
        #         for o2 in allOfferings:
        #             if(o.section != o2.section or o.course != o2.course):
        #                 if(o.day == o2.day):
        #                     if(o.timeslot != o2.timeslot):
        #                         firstTime = o.timeslot
        #                         secondTime = o2.timeslot
        #                         if(firstTime.end_time < secondTime.begin_time):
        #                             firstEnd = datetime.datetime.combine(datetime.date.today(), firstTime.end_time)
        #                             secondBegin = datetime.datetime.combine(datetime.date.today(), secondTime.begin_time)
        #                             difference = (secondBegin - firstEnd).total_seconds() / 60
        #                             if(abs(difference - break_length) <= 60):
        #                                 a = Bool(str(o.classnumber))
        #                                 b = Bool(str(o2.classnumber))
                                        # z3.add(Implies(a,b))
                                        
def addFriendPreferences(z3, highCourses, preferences):
    allOfferings = CourseOffering.objects.none()
    otherPreferences = {}
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
    for p in preferences:
        if(p.earliest_class_time != None):
            earliest = p.earliest_class_time
            for o in allOfferings:
                if(earliest > o.timeslot.begin_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))))
        if(p.latest_class_time != None):
            latest = p.latest_class_time
            for o in allOfferings:
                if(latest < o.timeslot.end_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))))
        if(p.preferred_days != None):
            day_id = p.preferred_days.id
            for o in allOfferings:
                if(day_id == o.day.id):
                    z3.add_soft(Bool(str(o.classnumber)))
        if(p.preferred_buildings != None):
            print(p.preferred_buildings)
        if(p.preferred_sections != None):
            section_code = p.preferred_sections
            for o in allOfferings:
                if(len(str(section_code)) == 1):
                    if(str(section_code)[0] == str(o.section.section_code)[0]):
                        z3.add_soft(Bool(str(o.classnumber)))
                else:
                    if(str(section_code) == str(o.section.section_code)):
                        z3.add_soft(Bool(str(o.classnumber)))
        if(p.preferred_faculty != None):
            faculty_id = p.preferred_faculty.id
            for o in allOfferings:
                if(o.faculty != None):
                    if(faculty_id == o.faculty.id):
                        z3.add_soft(Bool(str(o.classnumber)))
        if(p.min_courses != None):
            otherPreferences['min_courses'] = p.min_courses
        if(p.max_courses != None):
            otherPreferences['max_courses'] = p.max_courses
        if(p.undesirable_classes != None):
            classnumber = p.undesirable_classes
            z3.add_soft(Not(Bool(str(classnumber))), 2)
        # if(p.break_length != None):
        #     break_length = p.break_length
        #     for o in allOfferings:
        #         for o2 in allOfferings:
        #             if(o.section != o2.section or o.course != o2.course):
        #                 if(o.day == o2.day):
        #                     if(o.timeslot != o2.timeslot):
        #                         firstTime = o.timeslot
        #                         secondTime = o2.timeslot
        #                         if(firstTime.end_time < secondTime.begin_time):
        #                             firstEnd = datetime.datetime.combine(datetime.date.today(), firstTime.end_time)
        #                             secondBegin = datetime.datetime.combine(datetime.date.today(), secondTime.begin_time)
        #                             difference = (secondBegin - firstEnd).total_seconds() / 60
        #                             if(abs(difference - break_length) <= 60):
        #                                 a = Bool(str(o.classnumber))
        #                                 b = Bool(str(o2.classnumber))
                                        # z3.add(Implies(a,b))

    return otherPreferences

def checkPreferences(z3, model, preferences):
    unsatisfied = []
    offerings = None
    min_courses = None
    max_courses = None
    allOfferings = CourseOffering.objects.none()
    for o in model:
        if(model[o]):
            allOfferings = allOfferings | CourseOffering.objects.filter(classnumber=int(o.name()))
    days = []
    sections = []
    perDay = {
        'M': [],
        'T': [],
        'W': [],
        'H': [],
    }
    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            for d in perDay:
                for o in offerings:
                    if(o.day.day_code == d):
                        perDay[d].append(o)
            for p in preferences:
                if(p.earliest_class_time != None):
                    earliest = p.earliest_class_time
                    for o in offerings:
                        if(earliest > o.timeslot.begin_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts earlier than '+str(earliest))
                if(p.latest_class_time != None):
                    latest = p.latest_class_time
                    for o in offerings:
                        if(latest < o.timeslot.end_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts later than '+str(latest))
                if(p.preferred_days != None):
                    day = p.preferred_days.id
                    days.append(day)
                    # for o in offerings:
                    #     if(day_id != o.day.id):
                            # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day ('+str(p.preferred_days.day_code)+')')
                if(p.preferred_buildings != None):
                    pass
                if(p.preferred_sections != None):
                    section_code = p.preferred_sections
                    sections.append(section_code)
                    # for o in offerings:
                        # if(section_code not in o.section.section_code):
                            # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section ('+str(p.preferred_sections.section_code)+')')
                if(p.preferred_faculty != None):
                    faculty_id = p.preferred_faculty.id
                    for o in offerings:
                        if(o.faculty != None):
                            if(faculty_id != o.faculty.id):
                                pass
                                # unsatisfied.append('faculty')
                if(p.min_courses != None):
                    min_courses = p.min_courses
                if(p.max_courses != None):
                    max_courses = p.max_courses
                if(p.break_length != None):
                    break_length = p.break_length
    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            notSections = []
            for o in offerings:
                if(o.day.id not in days):
                    if(days != []):
                        unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day')
                sectionSatisfied = False
                for s in sections:
                    if(s in o.section.section_code):
                        sectionSatisfied = True
                if(not sectionSatisfied):
                    if(o.course.course_code not in notSections):
                        if(sections != []):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section')
                            notSections.append(o.course.course_code)

    if(min_courses != None):
        for d in perDay:
            if(int(min_courses) > len(perDay[d])):
                unsatisfied.append(str(d)+' has less than '+str(min_courses)+' courses')
    if(max_courses != None):
        for d in perDay:
            if(int(max_courses) < len(perDay[d])):
                unsatisfied.append(str(d)+' has more than '+str(max_courses)+' courses')
    return unsatisfied

def checkPreferencesFriends(offerings, preferences):
    z3 = Optimize()
    for o in offerings:
        z3.add(Bool(str(o.classnumber)))
    z3.check()
    model = z3.model()
    unsatisfied = []
    offerings = None
    min_courses = None
    max_courses = None
    allOfferings = CourseOffering.objects.none()
    for o in model:
        if(model[o]):
            allOfferings = allOfferings | CourseOffering.objects.filter(classnumber=int(o.name()))
    days = []
    sections = []
    perDay = {
        'M': [],
        'T': [],
        'W': [],
        'H': [],
    }
    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            for d in perDay:
                for o in offerings:
                    if(o.day.day_code == d):
                        perDay[d].append(o)
            for p in preferences:
                if(p.earliest_class_time != None):
                    earliest = p.earliest_class_time
                    for o in offerings:
                        if(earliest > o.timeslot.begin_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts earlier than '+str(earliest))
                if(p.latest_class_time != None):
                    latest = p.latest_class_time
                    for o in offerings:
                        if(latest < o.timeslot.end_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts later than '+str(latest))
                if(p.preferred_days != None):
                    day = p.preferred_days.id
                    days.append(day)
                if(p.preferred_buildings != None):
                    pass
                if(p.preferred_sections != None):
                    section_code = p.preferred_sections
                    sections.append(section_code)
                if(p.preferred_faculty != None):
                    faculty_id = p.preferred_faculty.id
                    for o in offerings:
                        if(o.faculty != None):
                            if(faculty_id != o.faculty.id):
                                unsatisfied.append('faculty')
                if(p.min_courses != None):
                    min_courses = p.min_courses
                if(p.max_courses != None):
                    max_courses = p.max_courses
                if(p.break_length != None):
                    break_length = p.break_length

    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            notSections = []
            for o in offerings:
                if(o.day.id not in days):
                    if(days != []):
                        unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day')
                sectionSatisfied = False
                for s in sections:
                    if(s in o.section.section_code):
                        sectionSatisfied = True
                if(not sectionSatisfied):
                    if(o.course.course_code not in notSections):
                        if(sections != []):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section')
                            notSections.append(o.course.course_code)


    if(min_courses != None):
        for d in perDay:
            if(int(min_courses) > len(perDay[d])):
                unsatisfied.append(str(d)+' has less than '+str(min_courses)+' courses')
    if(max_courses != None):
        for d in perDay:
            if(int(max_courses) < len(perDay[d])):
                unsatisfied.append(str(d)+' has more than '+str(max_courses)+' courses')
    return unsatisfied

def checkPreferencesFriendsOther(offerings, mainCourses, friends):
    for friend in friends:
        friendCourses = friend['highCourses'] + friend['lowCourses']
        diffCourses = list(set(mainCourses) - set(friendCourses))
        chosenCourses = list(set(friendCourses) - set(diffCourses)) 
        newCourses = list(set(chosenCourses) - set(mainCourses))
        preferences = friend['preferences']
        z3 = Optimize()
        for o in offerings:
            if(o.course.id in chosenCourses):
                z3.add(Bool(str(o.classnumber)))
        friendOfferings = CourseOffering.objects.none()
        for c in newCourses:
            offerings = CourseOffering.objects.filter(course=c)
            friendOfferings = friendOfferings | offerings
        for o in friendOfferings:
            z3.add_soft(Bool(str(o.classnumber)))
        z3.check()
        model = z3.model()
        unsatisfied = []
        offerings = None
        min_courses = None
        max_courses = None
        allOfferings = CourseOffering.objects.none()
        for o in model:
            if(model[o]):
                allOfferings = allOfferings | CourseOffering.objects.filter(classnumber=int(o.name()))
        days = []
        sections = []
        classnumbers = []
        perDay = {
            'M': [],
            'T': [],
            'W': [],
            'H': [],
        }
        for o in model:
            if(model[o]):
                offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
                for d in perDay:
                    for o in offerings:
                        if(o.day.day_code == d):
                            perDay[d].append(o)
                for p in preferences:
                    if(p.earliest_class_time != None):
                        earliest = p.earliest_class_time
                        for o in offerings:
                            if(earliest > o.timeslot.begin_time):
                                unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts earlier than '+str(earliest))
                    if(p.latest_class_time != None):
                        latest = p.latest_class_time
                        for o in offerings:
                            if(latest < o.timeslot.end_time):
                                unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts later than '+str(latest))
                    if(p.preferred_days != None):
                        day = p.preferred_days.id
                        days.append(day)
                    if(p.preferred_buildings != None):
                        pass
                    if(p.preferred_sections != None):
                        section_code = p.preferred_sections
                        sections.append(section_code)
                    if(p.preferred_faculty != None):
                        faculty_id = p.preferred_faculty.id
                        for o in offerings:
                            if(o.faculty != None):
                                if(faculty_id != o.faculty.id):
                                    unsatisfied.append('faculty')
                    if(p.min_courses != None):
                        min_courses = p.min_courses
                    if(p.max_courses != None):
                        max_courses = p.max_courses
                    if(p.break_length != None):
                        break_length = p.break_length
                    if(p.undesirable_classes != None):
                        classnumber = p.undesirable_classes
                        classnumbers.append(classnumber)

        for o in model:
            if(model[o]):
                offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
                notSections = []
                notClass = []
                for o in offerings:
                    if(o.day.id not in days):
                        if(days != []):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day')
                    sectionSatisfied = False
                    for s in sections:
                        if(s in o.section.section_code):
                            sectionSatisfied = True
                    if(not sectionSatisfied):
                        if(o.course.course_code not in notSections):
                            if(sections != []):
                                unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section')
                                notSections.append(o.course.course_code)
                    if(o.classnumber in classnumbers):
                        if(o.course.course_code not in notClass):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' is not a preferred class')
                            notClass.append(o.course.course_code)

        if(min_courses != None):
            for d in perDay:
                if(int(min_courses) > len(perDay[d])):
                    unsatisfied.append(str(d)+' has less than '+str(min_courses)+' courses')
        if(max_courses != None):
            for d in perDay:
                if(int(max_courses) < len(perDay[d])):
                    unsatisfied.append(str(d)+' has more than '+str(max_courses)+' courses')

        selectedCourses = []
        for o in allOfferings:
            if(o.course.id in chosenCourses):
                selectedCourses.append(o.course.course_code)
        selectedCourses = set(selectedCourses)
        allCourses = []
        for c in newCourses:
            allCourses.append(Course.objects.get(id=c).course_code)
            
        for c in allCourses:
            if not (c in selectedCourses):
                unsatisfied.append(c+' does not fit with this schedule.')

        return unsatisfied

def addExtraConstraints(z3, model):
    current = []
    for o in model:
        if(model[o]):
            current.append((Not(Bool(str(o)))))
    z3.add(Or(tuple(current)))

def addExtraConstraintsFriends(z3, offerings):
    current = []
    for o in offerings:
        current.append(Not(Bool(str(o.classnumber))))
    z3.add(Or(tuple(current)))

def search(courses, preferences):
    z3 = Optimize()

    addSoftConstraints(z3, [], courses)
    otherPreferences = addPreferences(z3, courses, [], preferences)

    schedules = []

    z3.check()
    model = z3.model()
    offerings = CourseOffering.objects.none() 
    for o in model:
        if(model[o]):
            offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))

    return offerings

def solve(highCourses, lowCourses, preferences, filterFull):
    z3 = Optimize()

    addHardConstraints(z3, highCourses, lowCourses, filterFull)
    addSoftConstraints(z3, highCourses, lowCourses)
    otherPreferences = addPreferences(z3, highCourses, lowCourses, preferences)

    schedules = []

    for i in range(0, 10):
        z3.check()
        model = z3.model()
        schedule = {}
        information = []
        selectedCourses = []
        offerings = CourseOffering.objects.none() 
        for o in model:
            if(model[o]):
                offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))
        if(len(offerings) == 0):
            break
        for o in offerings:
            selectedCourses.append(o.course.course_code)
        selectedCourses = set(selectedCourses)
        allCourses = []
        for c in highCourses:
            allCourses.append(Course.objects.get(id=c).course_code)
        for c in lowCourses:
            allCourses.append(Course.objects.get(id=c).course_code)
            
        for c in allCourses:
            if not (c in selectedCourses):
                information.append(c)
            
        schedule['offerings'] = offerings
        schedule['information'] = set(information)
        schedule['preferences'] = checkPreferences(z3, model, preferences)
        print(schedule['information'])
        print(schedule['preferences'])
        schedules.append(schedule)

        addExtraConstraints(z3, model)
        addSoftConstraints(z3, highCourses, lowCourses)

    return schedules 

def solveFriends(mainUser, friends):
    z3 = Optimize()

    friendCourses = []
    mainCourses = mainUser['highCourses'] + mainUser['lowCourses']
    for f in friends:
        friendCourses += list(set(f['highCourses'] + f['lowCourses']))
        
    diffCourses = list(set(friendCourses) - set(mainCourses))
    sameCourses = list(set(mainCourses + friendCourses) - set(diffCourses))

    addFriendConstraints(z3, mainCourses, diffCourses, sameCourses, mainUser, friends)
    addHardConstraints(z3, mainUser['highCourses'], mainUser['lowCourses'], mainUser['filterFull'])
    addSoftConstraints(z3, mainUser['highCourses'], mainUser['lowCourses'])
    otherPreferences = addPreferences(z3, mainUser['highCourses'], mainUser['lowCourses'], mainUser['preferences'])

    for f in friends:
        otherPreferences = addFriendPreferences(z3, sameCourses, f['preferences'])

    schedules = []

    for i in range(0, 10):
        z3.check()
        model = z3.model()
        schedule = {}
        information = []
        selectedCourses = []
        offerings = CourseOffering.objects.none() 
        for o in model:
            if(model[o]):
                offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))
        if(len(offerings) == 0):
            break
        newOfferings = []
        for o in offerings:
            if(o.course.id in mainUser['highCourses'] or o.course.id in mainUser['lowCourses']):
                newOfferings.append(o)
                selectedCourses.append(o.course.course_code)
        offerings = newOfferings
        selectedCourses = set(selectedCourses)
        allCourses = []
        for c in mainUser['highCourses']:
            allCourses.append(Course.objects.get(id=c).course_code)
        for c in mainUser['lowCourses']:
            allCourses.append(Course.objects.get(id=c).course_code)
            
        for c in allCourses:
            if not (c in selectedCourses):
                information.append(c)
            
        schedule['offerings'] = offerings
        schedule['information'] = set(information)
        schedule['preferences'] = checkPreferencesFriends(offerings, mainUser['preferences'])
        schedule['friendPreferences'] = checkPreferencesFriendsOther(offerings, mainCourses, friends)
        print(schedule['information'])
        print(schedule['preferences'])
        schedules.append(schedule)

        addExtraConstraintsFriends(z3, offerings)

        addSoftConstraints(z3, mainUser['highCourses'], mainUser['lowCourses'])
        for f in friends:
            addSoftConstraints(z3, f['highCourses'], f['lowCourses'])

    return schedules 


def removeFriendsConstraint(z3, user, allCourses):
    diffCourses = list(set(allCourses) - set(user['highCourses'] + user['lowCourses']))
    for c in diffCourses:
        offerings = CourseOffering.objects.filter(course=c)
        for o in offerings:
            a = Not(Bool(str(o.classnumber)))
            z3.add(a)

def solveFriendsMulti(users):
    z3 = Optimize()

    highCourses = []
    lowCourses = []
    for u in users:
        highCourses += u['highCourses']
        lowCourses += u['lowCourses']
        addHardConstraints(z3, u['highCourses'], u['lowCourses'], u['filterFull'])
        addSoftConstraints(z3, u['highCourses'], u['lowCourses'])
        addPreferences(z3, u['highCourses'], u['lowCourses'], u['preferences'])

    highCourses = list(set(highCourses))
    lowCourses = list(set(highCourses))
    allCourses = highCourses + lowCourses

    schedules = []

    for u in users:
        for i in range(0, 10):
            tempz3 = z3
            removeFriendsConstraint(tempz3, u, allCourses)
            tempz3.check()
            model = tempz3.model()
            schedule = {}
            information = []
            selectedCourses = []
            offerings = CourseOffering.objects.none() 
            for o in model:
                if(model[o]):
                    offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))
            if(len(offerings) == 0):
                break
            newOfferings = []
            for o in offerings:
                if(o.course.id in u['highCourses'] or o.course.id in u['lowCourses']):
                    newOfferings.append(o)
                    selectedCourses.append(o.course.course_code)
            offerings = newOfferings
            selectedCourses = set(selectedCourses)
            allCourses = []
            for c in u['highCourses']:
                allCourses.append(Course.objects.get(id=c).course_code)
            for c in u['lowCourses']:
                allCourses.append(Course.objects.get(id=c).course_code)
                
            for c in allCourses:
                if not (c in selectedCourses):
                    information.append(c)
                
            schedule['offerings'] = offerings
            schedule['information'] = set(information)
            schedule['preferences'] = checkPreferencesFriends(offerings, u['preferences'])
            schedule['friendPreferences'] = checkPreferencesFriendsOther(offerings, u, u)
            print(schedule['information'])
            print(schedule['preferences'])
            schedules.append(schedule)

            addExtraConstraintsFriends(z3, offerings)

            addSoftConstraints(z3, u['highCourses'], u['lowCourses'])

    return schedules 

def solveEdit(classes, newclasses, courses):
    def addHardConstraints():
        allOfferings = CourseOffering.objects.none()
        for c in courses:
            offerings = CourseOffering.objects.filter(course=c)
            allOfferings = allOfferings | offerings
            for o in offerings:
                for o2 in offerings:
                    if(o.section != o2.section):
                        a = Bool(str(o.classnumber))
                        b = Not(Bool(str(o2.classnumber)))
                        z3.add(Implies(a,b))
        for o in allOfferings:
            for o2 in allOfferings:
                if(o.section != o2.section or o.course != o2.course):
                    if(o.day == o2.day):
                        if(o.timeslot == o2.timeslot):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        else:
                            firstTime = o.timeslot
                            secondTime = o2.timeslot
                            if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
        for c in newclasses:
            z3.add_soft(Bool(str(c)),10)
    def addSoftConstraints():
        for c in classes:
            z3.add_soft(Bool(str(c)))

    z3 = Optimize()

    addHardConstraints()
    addSoftConstraints()

    z3.check()
    model = z3.model()
    offerings = CourseOffering.objects.none() 
    print(model)
    print(classes)
    print(newclasses)
    print(courses)
    for o in model:
        if(model[o]):
            offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))

    schedule = {}
    allCourses = []
    selectedCourses = []
    selectedNumbers = []
    rejected = []

    for c in courses:
        allCourses.append(Course.objects.get(id=c).course_code)

    for o in offerings:
        selectedCourses.append(o.course.course_code)
        selectedNumbers.append(o.classnumber)
    selectedCourses = set(selectedCourses)

    for c in allCourses:
        if not (c in selectedCourses):
            rejected.append(c)
    
    print(schedule)
    print(selectedCourses)
    print(allCourses)

    schedule['rejected'] = set(rejected)
    schedule['classnumbers'] = set(selectedNumbers)

    return schedule 

def checkConflicts(classnumbers):
    def addHardConstraints():
        allOfferings = CourseOffering.objects.none()
        for c in classnumbers:
            offerings = CourseOffering.objects.filter(classnumber=c)
            allOfferings = allOfferings | offerings
        for o in allOfferings:
            for o2 in allOfferings:
                if(o.section != o2.section or o.course != o2.course):
                    if(o.day == o2.day):
                        if(o.timeslot == o2.timeslot):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        else:
                            firstTime = o.timeslot
                            secondTime = o2.timeslot
                            if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
    def addClassnumbers():
        for c in classnumbers:
            z3.add(Bool(str(c)))

    z3 = Optimize()

    addHardConstraints()
    addClassnumbers()

    return z3.check()